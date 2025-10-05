"""
S3 storage system for archiving closed meetings.
"""
import os
import json
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional


class S3Storage:
    """Handles S3 operations for meeting data and reports."""
    
    def __init__(self):
        """Initialize S3 client with credentials from environment."""
        self.bucket_name = os.getenv('AWS_S3_BUCKET')
        self.access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        if not all([self.bucket_name, self.access_key, self.secret_key]):
            print("Warning: AWS credentials not found. S3 uploads will be disabled.")
            self.s3_client = None
            return
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            print(f"S3 client initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            print("Error: AWS credentials are invalid. S3 uploads will be disabled.")
            self.s3_client = None
        except Exception as e:
            print(f"Error initializing S3 client: {e}. S3 uploads will be disabled.")
            self.s3_client = None
    
    def is_available(self) -> bool:
        """Check if S3 is available and configured."""
        return self.s3_client is not None
    
    def upload_meeting_json(self, meeting_id: str, meeting_data: dict) -> bool:
        """
        Upload meeting JSON data to S3.
        
        Args:
            meeting_id: The meeting ID
            meeting_data: The meeting data dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available():
            print(f"S3 not available, skipping upload for meeting {meeting_id}")
            return False
        
        try:
            # Convert meeting data to JSON string
            json_content = json.dumps(meeting_data, indent=2, ensure_ascii=False)
            
            # Upload to S3
            key = f"meetings/{meeting_id}/meeting.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_content.encode('utf-8'),
                ContentType='application/json'
            )
            
            print(f"Successfully uploaded meeting JSON for {meeting_id} to S3")
            return True
            
        except ClientError as e:
            print(f"Error uploading meeting JSON for {meeting_id}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading meeting JSON for {meeting_id}: {e}")
            return False
    
    def upload_html_report(self, meeting_id: str, html_content: str) -> bool:
        """
        Upload HTML report to S3.
        
        Args:
            meeting_id: The meeting ID
            html_content: The HTML content string
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_available():
            print(f"S3 not available, skipping HTML upload for meeting {meeting_id}")
            return False
        
        try:
            # Upload HTML to S3
            key = f"meetings/{meeting_id}/index.html"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=html_content.encode('utf-8'),
                ContentType='text/html'
            )
            
            print(f"Successfully uploaded HTML report for {meeting_id} to S3")
            return True
            
        except ClientError as e:
            print(f"Error uploading HTML report for {meeting_id}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error uploading HTML report for {meeting_id}: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test S3 connection by attempting to list bucket contents.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"S3 connection test successful for bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"S3 connection test failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error testing S3 connection: {e}")
            return False

