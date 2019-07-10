import logging
import boto3
from botocore.exceptions import ClientError
class BotoService:
    """ This class is contains the bucket operations"""
    def __init__(self):
        self.s3 = boto3.client('s3')

    def create_bucket(self, bucket_name, region=None):
        """ This method is used to create the AWS bucket"""
        try:
            s3_client = boto3.client('s3', region_name=region) # call s3 clint object
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False  #True if the referenced bucket, otherwise False
        return True


    def delete_bucket(self,bucket_name):
        """ This method is used to create the AWS bucket"""
        # Delete the bucket
        try:
            s3 = boto3.client('s3')
            s3.delete_bucket(Bucket=bucket_name) # bucket_name: string
        except ClientError as e:
            logging.error(e)
            return False  #True if the referenced bucket was deleted, otherwise False
        return True

    def bucket_exists(self, bucket_name):
        """Determine whether bucket_name exists and the user has permission to access it
        """
        try:
            self.s3.head_bucket(Bucket=bucket_name)  # bucket_name: string
        except ClientError as e:
            logging.debug(e)
            return False  # True if the referenced bucket_name exists, otherwise False
        return True



# *************************************************************************************


