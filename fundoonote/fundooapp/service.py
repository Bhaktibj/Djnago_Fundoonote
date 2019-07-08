import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
class BotoService:
    def __init__(self):
        # GET AWS ACCESS KEY FROM SETTING
        self.access_key = settings.AWS_ACCESS_KEY_ID
        # GET AWS SECRET KEY FROM SETTING
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY
        # CREATE BOTO3 CLIENT OBJECT
        self.s3 = boto3.client('s3')
        # SET DEFAULT BUCKET NAME
        self.default_bucket = "django-assets"

    def create_bucket(self, bucket_name, region=None):
        try:
            # REGION NOT PASS THEN ASSIGN DEFAULT REGION
            if region is None:
                region = 'ap-south-1'
            # CHECK EXIST THE BUCKET BEFORE CREATING IF NOT THEN CREATE NEW
            if not self.bucket_exists(bucket_name):
                if region is None:
                    self.s3.create_bucket(Bucket=bucket_name)
                    print(bucket_name)
                else:
                    s3_client = boto3.client('s3', region_name=region)
                    location = {'LocationConstraint': region}
                    s3_client.create_bucket(Bucket=bucket_name,
                                            CreateBucketConfiguration=location)
            # IF BUCKET EXIST THEN PRINT MESSAGE AND RETURN FALSE
            else:
                print("Already Exist..")
                return False
        except ClientError as e:
            logging.error(e)
            print("Bucket Already Exist")
            return False
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

    # THIS METHOD USED TO DOWNLOAD THE FILE FROM THE BUCKET
    def GetFile(self, bucket_name, object_name):
        try:
            # GET THE OBJECT BY CALLING get_object METHOD
            response = self.s3.get_object(Bucket=bucket_name, Key=object_name)
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            logging.error(e)
            return None
        # Return an open StreamingBody object
        return response[ 'Body' ]

    # THIS METHOD IS USED TO DELETE OBJECT FROM THE BUCKET
    def DeleteFile(self, Bucket_name, File_name):
        try:
            # DELETE OBJECT FROM BUCKET BY CALLING delete_object METHOD
            self.s3.delete_object(Bucket=Bucket_name, Key=File_name)
        except ClientError as e:
            logging.error(e)
            return False
        # RETURN TRUE IF DELETED
        return True

    def uploadto_aws(request, uploaded_file):
        """ this method is used to upload a pic aws s3 bucket"""
        try:
            if request.method == 'POST':
                uploaded_file = request.FILES['document']   # taking the file from local
                uploaded_file = open(path, 'rb')  # image to upload with read access
                file_name = image+".jpg"
                print("filename", file_name)
                s3 = boto3.client('s3')     # using boto to upload file in aws s3 bucket
                s3.upload_fileobj(uploaded_file, 'django-s3-assets2', Key=file_name)
        except:
            return HttpResponse("Hello")