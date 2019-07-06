
import redis
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
