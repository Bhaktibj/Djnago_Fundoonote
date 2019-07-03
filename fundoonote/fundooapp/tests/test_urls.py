from django.urls import reverse, resolve, Resolver404
from Users.views import register

class TestUrls:
   def test_view_url_by_name(self):
        path = reverse('index')  # test the url by name.
        assert resolve(path).view_name== 'index'

   def test_view_url_by_name(self):  # test the home page status code
       response = reverse('enter')
       assert resolve(response).view_name=='enter'  # 200 is status code is True


   def test_view_url_by_name_not_valid(self): #test the User_logout url is revers or not
       try:
            path = resolve('user_logout')
            assert reverse(path).view_name=='user_logout'
       except(Resolver404):
           print(Resolver404)

   def test_signup_url_resolves_signup_view(self):
       view = resolve('/register/')
       assert (view.func, register)

       



