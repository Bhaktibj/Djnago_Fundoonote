
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)



class redis_methods:
    """This class is used to set , get , length from Redis cache"""

    def set_value(self, key, value,): # this method used to set value in redis cache
        r.set(key, value)
        print('token set')

    def get_value(self, key): # this method is used to get the value from cache
        token = r.get(key)
        return token

    def length_str(self,key): # this method is used to find the length of string
        token_len = r.strlen(key)
        return token_len

    def flush(self):
        r.flushall()
print("Redis:",redis_methods.__doc__)
