# Example: Cloud SDK usage
import boto3
from google.cloud import storage
import azure.storage.blob

# AWS S3
s3 = boto3.client('s3')

# Google Cloud Storage
gcs_client = storage.Client()

# Azure Blob Storage
blob_service_client = azure.storage.blob.BlobServiceClient.from_connection_string("fake_connection_string")
