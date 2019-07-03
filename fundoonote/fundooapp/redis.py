# import boto3
import redis
# s3 = boto3.client('s3')  # Connection for S3
# def upload_image(file, tag_file, valid_image):
#     """This method is used to upload the images to Amazon s3 bucket"""
#     try:
#         if valid_image:  # If Image is Valid
#             key = tag_file  # Assign the Key
#             s3.upload_fileobj(file, 'django-s3-assets1', Key=key)  # Upload the image in a S3
#             # print("Filesss", type(str(file)))
#     except Exception as e:
#         print(e)
#
#
# def delete_from_s3(key):
#     try:
#         print('Keey', key)
#         """This method is used to delete any object from s3 bucket """
#         if key:  # If Key
#             s3.delete_object(Bucket='django-s3-assets1', Key=key)  # Delete the image in a S3
#     except Exception as e:
#         print(e)



r = redis.StrictRedis(host='localhost', port=6379, db=0)


"""This class is used to set , get , length from Redis cache"""

class redis_methods:

    """ this method is used to  add the data to redis"""
    def set_value(self, key, value,):
        r.set(key, value)
        print('token set')
    """this method is used to  get the data out of redis"""

    def get_value(self, key):
        token = r.get(key)
        return token

    """ This method is used to display the length of value"""
    def length_str(self,key):
        token_len = r.strlen(key)
        return token_len

    """ this method is used to delete data from redis"""
    def flush(self):
        r.flushall()
print(redis_methods.__doc__)
