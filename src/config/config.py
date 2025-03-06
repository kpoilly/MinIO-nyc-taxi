import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration constants
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/"
RAW_DATA_DIR = os.getenv("RAW_DATA_DIR", "./data/raw")
PROCESSED_DATA_DIR = os.getenv("PROCESSED_DATA_DIR", "./data/processed")
CONSOLIDATED_FILE_NAME = os.getenv("CONSOLIDATED_FILE_NAME", "yellow_tripdata_sampled.csv")
FEATURES_FILE_NAME = os.getenv("FEATURES_FILE_NAME", "yellow_tripdata_features.csv")

# MinIO Configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_BUCKET")

# MLFlow Configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI")
