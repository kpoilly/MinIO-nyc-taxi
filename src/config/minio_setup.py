import boto3
from botocore.exceptions import NoCredentialsError
from config import config

# Initialize MinIO client
s3_client = boto3.client(
    "s3",
    endpoint_url=config.MINIO_ENDPOINT,
    aws_access_key_id=config.MINIO_ACCESS_KEY,
    aws_secret_access_key=config.MINIO_SECRET_KEY,
)

def enable_versioning(bucket_name):
    """Enable versioning on a bucket."""
    try:
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={
                'Status': 'Enabled'  # Set to 'Enabled' or 'Suspended' if you want to suspend it
            }
        )
        print(f"Versioning enabled for bucket '{bucket_name}'")
    except Exception as e:
        print(f"Error enabling versioning for bucket '{bucket_name}': {e}")

def ensure_bucket_exists(bucket_name, versioning):
    """Check if the bucket exists, create if it doesn’t."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except:
        print(f"Bucket '{bucket_name}' not found. Creating it...")
        s3_client.create_bucket(Bucket=bucket_name)

    # Enable versioning on the bucket (if it's not already enabled)
    if versioning:
        enable_versioning(bucket_name)

def check_versioning_status(bucket_name):
    """Check if versioning is enabled on a bucket."""
    try:
        response = s3_client.get_bucket_versioning(Bucket=bucket_name)
        versioning_status = response.get('Status', 'Not Enabled')
        print(f"Versioning status for bucket '{bucket_name}': {versioning_status}")
        return versioning_status
    except Exception as e:
        print(f"Error checking versioning status for bucket '{bucket_name}': {e}")
        return None

def upload_to_minio(local_path, bucket, object_name, versioning = False):
    """Upload a file to MinIO."""
    ensure_bucket_exists(bucket, versioning)
    try:
        s3_client.upload_file(local_path, bucket, object_name)
        print(f"Uploaded {object_name} to MinIO")
    except NoCredentialsError:
        print("Error: Invalid MinIO credentials.")

def download_from_minio(bucket, object_name, local_path):
    """Download a file from MinIO."""
    try:
        s3_client.download_file(bucket, object_name, local_path)
        print(f"Downloaded {object_name} from MinIO")
        return True
    except Exception as e:
        print(f"Error downloading {object_name}: {e}")
        return False
    

