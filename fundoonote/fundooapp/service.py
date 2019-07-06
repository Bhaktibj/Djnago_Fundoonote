import logging
import boto3
from botocore.exceptions import ClientError
class BotoService:
    def create_bucket(self,bucket_name, region=None):
        """Create an S3 bucket in a specified region
        If a region is not specified, the bucket is created in the S3 default
        """
        # Create bucket
        s3_client = boto3.client('s3')
        try:
            if region is None:
                s3_client.create_bucket(Bucket=bucket_name) #bucket_name: Bucket to create
            else:
                location = {'LocationConstraint': region} #String region to create bucket
                s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False  # True if bucket created, else False
        return True

    def delete_bucket(self,bucket_name):
        """Delete an empty S3 bucket
        If the bucket is not empty, the operation fails.
        """

        # Delete the bucket
        s3 = boto3.client('s3')
        try:
            s3.delete_bucket(Bucket=bucket_name) # bucket_name: string
        except ClientError as e:
            logging.error(e)
            return False  #True if the referenced bucket was deleted, otherwise False
        return True

    def bucket_exists(self,bucket_name):
        """Determine whether bucket_name exists and the user has permission to access it
        """

        s3 = boto3.client('s3')
        try:
            response = s3.head_bucket(Bucket=bucket_name) # bucket_name: string
        except ClientError as e:
            logging.debug(e)
            return False  # True if the referenced bucket_name exists, otherwise False
        return True










