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

    def list_bucket_objects(self,bucket_name):
        """List the objects in an Amazon S3 bucket
        """
        # Retrieve the list of bucket objects
        s3 = boto3.client('s3')
        try:
            response = s3.list_objects_v2(Bucket=bucket_name)
        except ClientError as e:
            # AllAccessDisabled error == bucket not found
            logging.error(e)
            return None
        return response[ 'Contents' ]

    def delete_object(self,bucket_name, object_name):
        """Delete an object from an S3 bucket
        :param bucket_name: string
        :param object_name: string
        :return: True if the referenced object was deleted, otherwise False
        """

        # Delete the object
        s3 = boto3.client('s3')
        try:
            s3.delete_object(Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            logging.error(e)
            return False
        return True
# *************************************************************************************


