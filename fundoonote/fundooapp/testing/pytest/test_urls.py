from django.contrib.auth.models import User
from django.urls import reverse, resolve, Resolver404
import pytest
class TestUrls:

   def test_view_url_by_name_not_valid(self): #test the User_logout url is revers or not
       try:
            path = resolve('user_logout')
            assert reverse(path).view_name=='user_logout'
       except(Resolver404):
           print(Resolver404)

   def test_hello_world(self):
       assert "hello_world" == "hello_world"


   def test_url_by_name(self):
       try:
           path = resolve('logout')
           assert reverse(path).view_name=='user_logout'
       except(Resolver404):
           print(Resolver404)