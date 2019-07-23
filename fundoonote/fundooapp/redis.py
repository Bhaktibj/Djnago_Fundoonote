import redis
redis_obj = redis.StrictRedis(host='localhost', port=6379, db=0)

class RedisMethods:
    """This class is used to set , get , length from Redis cache"""

    def set_value(self, key, value,): # this method used to set value in redis cache
        redis_obj.set(key, value)
        print('token set')

    def get_value(self, key): # this method is used to get the value from cache
        token = redis_obj.get(key)
        return token

    def length_str(self,key): # this method is used to find the length of string
        token_len = redis_obj.strlen(key)
        return token_len

    def flush(self):
        redis_obj.flushall()
print("Redis:",RedisMethods.__doc__)
