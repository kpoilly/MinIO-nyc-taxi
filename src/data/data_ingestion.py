import os
import requests
import pandas as pd
from datetime import datetime

import sys
from pathlib import Path
# Add src directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config
from config.minio_setup import upload_to_minio, download_from_minio

# Configuration
BASE_URL = config.BASE_URL
RAW_DATA_DIR = config.RAW_DATA_DIR
BUCKET_NAME = config.BUCKET_NAME
MONTHS_TO_KEEP = 6
SAMPLE_FRACTION = 0.01

def download_parquet_file(year, month):
    """Download a month's taxi data and save it locally."""
    file_name = f"yellow_tripdata_{year}-{month:02d}.parquet"
    file_url = f"{BASE_URL}{file_name}"
    local_path = os.path.join(RAW_DATA_DIR, file_name)

    response = requests.get(file_url)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {file_name}")
        return local_path
    else:
        print(f"Failed to download {file_url}. HTTP Status Code: {response.status_code}")
        return None

def integrate_new_data(new_data_path):
    """Merge sampled new data with existing data while keeping only the last N months."""
    object_name = config.CONSOLIDATED_FILE_NAME
    local_csv_path = os.path.join(RAW_DATA_DIR, object_name)

    # Try to load existing dataset from MinIO
    if download_from_minio(BUCKET_NAME, object_name, local_csv_path):
        df_existing = pd.read_csv(local_csv_path)
        print("Loaded existing dataset from MinIO")
    else:
        df_existing = pd.DataFrame()
        print("No existing dataset found in MinIO. Creating a new dataset.")

    # Convert 'tpep_pickup_datetime' column to datetime
    if "tpep_pickup_datetime" in df_existing.columns and not pd.api.types.is_datetime64_any_dtype(df_existing["tpep_pickup_datetime"]):
        df_existing["tpep_pickup_datetime"] = pd.to_datetime(df_existing["tpep_pickup_datetime"], errors='coerce')

    # Load new month's data and sample
    df_new = pd.read_parquet(new_data_path)
    df_new_sampled = df_new.sample(frac=SAMPLE_FRACTION, random_state=42)
    df_new_sampled["tpep_pickup_datetime"] = pd.to_datetime(df_new_sampled["tpep_pickup_datetime"], errors='coerce')

    # Merge new sampled data with existing dataset
    df_combined = pd.concat([df_existing, df_new_sampled], ignore_index=True)

    # Apply rolling window: keep only the last N months of data
    latest_date = df_combined["tpep_pickup_datetime"].max()
    df_combined = df_combined[df_combined["tpep_pickup_datetime"] >= latest_date - pd.DateOffset(months=MONTHS_TO_KEEP)]

    # Save and upload the new dataset
    df_combined.to_csv(local_csv_path, index=False)
    upload_to_minio(local_csv_path, BUCKET_NAME, object_name)

def process_data():
    """Determine months to process and download, sample, integrate, and upload new data."""
    today = datetime.today()
    current_month = today.month
    current_year = today.year -1

    # Determine the last two full months
    if current_month in [1, 2]:
        year1, month1 = current_year - 1, 12 if current_month == 1 else 11
        year2, month2 = current_year - 1, 11 if current_month == 1 else 10
    else:
        year1, month1 = current_year, current_month - 1
        year2, month2 = current_year, current_month - 2

    months_to_process = [(year1, month1), (year2, month2)]

    for year, month in months_to_process:
        parquet_path = download_parquet_file(year, month)
        if parquet_path:
            integrate_new_data(parquet_path)

def main():
    if not os.path.exists(RAW_DATA_DIR):
        os.makedirs(RAW_DATA_DIR)
    process_data()

if __name__ == "__main__":
    main()
