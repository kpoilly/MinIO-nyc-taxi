import os
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pickle

import sys
from pathlib import Path
# Add src directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import config
from config.minio_setup import upload_to_minio, download_from_minio

# Configuration
PROCESSED_DATA_DIR = config.PROCESSED_DATA_DIR
BUCKET_NAME = os.getenv("MINIO_BUCKET")
MLFLOW_TRACKING_URI = config.MLFLOW_TRACKING_URI

def load_data():
    """Load the train and test datasets from MinIO"""
    # Ensure the directory exists before downloading
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    
    X_train_path = os.path.join(PROCESSED_DATA_DIR, "X_train.csv")
    X_test_path = os.path.join(PROCESSED_DATA_DIR, "X_test.csv")
    y_train_path = os.path.join(PROCESSED_DATA_DIR, "y_train.csv")
    y_test_path = os.path.join(PROCESSED_DATA_DIR, "y_test.csv")
    
    # Download datasets from MinIO
    if not download_from_minio(BUCKET_NAME, "X_train.csv", X_train_path):
        return None, None, None, None  # Return None if download fails
    if not download_from_minio(BUCKET_NAME, "X_test.csv", X_test_path):
        return None, None, None, None  # Return None if download fails
    if not download_from_minio(BUCKET_NAME, "y_train.csv", y_train_path):
        return None, None, None, None  # Return None if download fails
    if not download_from_minio(BUCKET_NAME, "y_test.csv", y_test_path):
        return None, None, None, None  # Return None if download fails
   
    # Load the datasets into DataFrames
    try:
        X_train = pd.read_csv(X_train_path)
        X_test = pd.read_csv(X_test_path)
        y_train = pd.read_csv(y_train_path).values.ravel()  # Flatten y_train
        y_test = pd.read_csv(y_test_path).values.ravel()    # Flatten y_test
        print("Data loaded successfully.")
        return X_train, X_test, y_train, y_test
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None, None

def train_model(X_train, X_test, y_train, y_test):
    """Train a RandomForest model and save it."""
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Mean Absolute Error: {mae}")

    # Save the model as 'model.pkl'
    model_path = "./models/model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    return model, mae, model_path

def log_model(model, mae):
    """Log the model and metrics into MLflow, using MinIO as the artifact store."""
    # Set up MinIO environment variables
    os.environ["AWS_ACCESS_KEY_ID"] = config.MINIO_ACCESS_KEY
    os.environ["AWS_SECRET_ACCESS_KEY"] = config.MINIO_SECRET_KEY
    os.environ["MLFLOW_S3_ENDPOINT_URL"] = config.MINIO_ENDPOINT
    os.environ["MLFLOW_TRACKING_URI"] = MLFLOW_TRACKING_URI
    os.environ["MLFLOW_ARTIFACT_LOCATION"] = f"s3://{BUCKET_NAME}/mlflow-artifacts"

    # Log parameters, metrics, and artifacts within the MLflow run
    mlflow.log_param("model_type", "RandomForestRegressor")
    mlflow.log_metric("mae", mae)
    mlflow.sklearn.log_model(model, "model")
    mlflow.log_artifact("./models/model.pkl")
    print("Logged model and metrics to MLflow")

def main():
    # Set the experiment only once at the beginning
    mlflow.set_experiment("nyc_taxi_fare_prediction")  # This is where your experiment name is set

    # Start a new run under this experiment
    with mlflow.start_run():
        # Load the data
        X_train, X_test, y_train, y_test = load_data()
        if X_train is None:
            print("Error: Failed to download or load data.")
            return

        # Train model and get path to saved model
        model, mae, model_path = train_model(X_train, X_test, y_train, y_test)

        # Log model and metrics
        log_model(model, mae)

        # Log the saved model file as an artifact
        mlflow.log_artifact(model_path)

if __name__ == "__main__":
    main()
