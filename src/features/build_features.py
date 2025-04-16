import os
import pandas as pd
from sklearn.model_selection import train_test_split

import sys
from pathlib import Path
# Add src directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config
from config.minio_setup import upload_to_minio, download_from_minio

# Configuration
RAW_DATA_DIR = config.RAW_DATA_DIR
PROCESSED_DATA_DIR = config.PROCESSED_DATA_DIR
CONSOLIDATED_FILE_NAME = config.CONSOLIDATED_FILE_NAME
FEATURES_FILE_NAME = config.FEATURES_FILE_NAME
BUCKET_NAME = config.BUCKET_NAME

def clean_missing_data(df):
    """Handle missing data in the dataset."""
    df = df.dropna(subset=["tpep_pickup_datetime", "tpep_dropoff_datetime"])
    
    num_cols = df.select_dtypes(include=["number"]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())

    cat_cols = df.select_dtypes(include=["object"]).columns
    for col in cat_cols:
        df[col] = df[col].fillna(df[col].mode()[0])
    
    return df

def create_features(df):
    """Generate new features from the dataset."""
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_dayofweek"] = df["tpep_pickup_datetime"].dt.dayofweek
    df["pickup_month"] = df["tpep_pickup_datetime"].dt.month
    df["pickup_weekday"] = df["pickup_dayofweek"].apply(lambda x: 1 if x < 5 else 0)
    df["trip_duration"] = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60

    df["total_fare"] = (
        df["fare_amount"]
        + df["extra"]
        + df["mta_tax"]
        + df["improvement_surcharge"]
        + df["tolls_amount"]
        + df["congestion_surcharge"]
        + df.get("Airport_fee", 0)
    )

    # Drop unnecessary columns
    df = df.drop(columns=["tpep_pickup_datetime", "tpep_dropoff_datetime", "store_and_fwd_flag"])
    
    return df

def split_and_save_data(df):
    """Split data into training and test sets, save to local storage, and upload to MinIO."""
    
    # Define target variable (assuming trip_duration is the target)
    target_column = "trip_duration"
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' not found in the dataset.")

    X = df.drop(["total_fare", "fare_amount"], axis = 1)
    y = df['total_fare']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define paths
    X_train_path = os.path.join(PROCESSED_DATA_DIR, "X_train.csv")
    X_test_path = os.path.join(PROCESSED_DATA_DIR, "X_test.csv")
    y_train_path = os.path.join(PROCESSED_DATA_DIR, "y_train.csv")
    y_test_path = os.path.join(PROCESSED_DATA_DIR, "y_test.csv")

    # Save locally
    X_train.to_csv(X_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_train.to_csv(y_train_path, index=False)
    y_test.to_csv(y_test_path, index=False)

    print("Saved train/test datasets locally.")

    # Upload to MinIO
    upload_to_minio(X_train_path, BUCKET_NAME, "X_train.csv")
    upload_to_minio(X_test_path, BUCKET_NAME, "X_test.csv")
    upload_to_minio(y_train_path, BUCKET_NAME, "y_train.csv")
    upload_to_minio(y_test_path, BUCKET_NAME, "y_test.csv")

def build_features():
    """Download, clean, process, split, and upload taxi trip data."""
    consolidated_file_path = os.path.join(RAW_DATA_DIR, CONSOLIDATED_FILE_NAME)
    features_file_path = os.path.join(PROCESSED_DATA_DIR, FEATURES_FILE_NAME)

    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    # Download Dataset from MinIO
    if not download_from_minio(BUCKET_NAME, CONSOLIDATED_FILE_NAME, consolidated_file_path):
        print(f"Error: The consolidated file {CONSOLIDATED_FILE_NAME} does not exist in MinIO.")
        return

    print(f"Loading data from {consolidated_file_path}")
    df = pd.read_csv(consolidated_file_path)

    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"], errors="coerce")
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"], errors="coerce")

    df = clean_missing_data(df)
    df = create_features(df)

    # Save the processed dataset
    df.to_csv(features_file_path, index=False)

    # Upload processed dataset to MinIO
    upload_to_minio(features_file_path, BUCKET_NAME, FEATURES_FILE_NAME)

    # Split the data and save train/test sets
    split_and_save_data(df)

if __name__ == "__main__":
    build_features()
