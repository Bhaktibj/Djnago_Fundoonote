import logging
import boto3
from django.conf import settings
from botocore.exceptions import ClientError
class BotoService:
    """ This class is contains the bucket operations"""
    def __init__(self):
        self.access_key = settings.AWS_ACCESS_KEY_ID # get access key from setting
        self.secret_key = settings.AWS_SECRET_ACCESS_KEY # get secrete access key from setting
        self.s3 = boto3.client('s3') # create boto3 object
        self.default_bucket = "django-assets" # initial bucket name
    def create_bucket(self, bucket_name, region=None):
        """ This method is used to create the AWS bucket"""

        try:
            if region is None:  # if region is none
                region = 'ap-south-1'
            if not self.bucket_exists(bucket_name):
                if region is None:
                    self.s3.create_bucket(Bucket=bucket_name)
                    print(bucket_name) # print bucket name
                else:
                    s3_client = boto3.client('s3', region_name=region) # call s3 clint object
                    location = {'LocationConstraint': region}
                    s3_client.create_bucket(Bucket=bucket_name,
                                            CreateBucketConfiguration=location)
            else:
                print("Already Exist..") # bucket is already exist
                return False
        except ClientError as e:
            logging.error(e)
            print("Bucket Already Exist")
            return False
        return True
    def delete_bucket(self,bucket_name):
        """ This method is used to create the AWS bucket"""

        # Delete the bucket
        s3 = boto3.client('s3')
        try:
            s3.delete_bucket(Bucket=bucket_name) # bucket_name: string
        except ClientError as e:
            logging.error(e)
            return False  #True if the referenced bucket was deleted, otherwise False
        return True

    def bucket_exists(self, bucket_name):
        """Determine whether bucket_name exists and the user has permission to access it
        """

        s3 = boto3.client('s3')
        try:
            response = s3.head_bucket(Bucket=bucket_name)  # bucket_name: string
        except ClientError as e:
            logging.debug(e)
            return False  # True if the referenced bucket_name exists, otherwise False
        return True



# *************************************************************************************
    """ this method is used the download the file from bucket"""
    # def GetFile(self, bucket_name, object_name):
    #     try:
    #         # Get the object by calling get_object METHOD
    #         response = self.s3.get_object(Bucket=bucket_name, Key=object_name)
    #     except ClientError as e:
    #         # AllAccessDisabled error == bucket or object not found
    #         logging.error(e)
    #         return None
    #     # Return an open StreamingBody object
    #     return response[ 'Body' ]
    #
    # def DeleteFile(self, Bucket_name, File_name): # this method is used to delete the object
    #     try:
    #         self.s3.delete_object(Bucket=Bucket_name, Key=File_name)
    #     except ClientError as e:
    #         logging.error(e)
    #         return False
    #     # RETURN TRUE IF DELETED
    #     return True

    # def uploadto_aws(request, uploaded_file):
    #     """ this method is used to upload a pic aws s3 bucket"""
    #     try:
    #         if request.method == 'POST':
    #             uploaded_file = request.FILES['document']   # taking the file from local
    #             uploaded_file = open(path, 'rb')  # image to upload with read access
    #             file_name = image+".jpg"
    #             print("filename", file_name)
    #             s3 = boto3.client('s3')     # using boto to upload file in aws s3 bucket
    #             s3.upload_fileobj(uploaded_file, 'django-s3-assets2', Key=file_name)
    #     except:
    #         return HttpResponse("Inavlid")


