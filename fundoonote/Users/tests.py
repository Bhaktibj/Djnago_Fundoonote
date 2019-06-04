from django.test import TestCase, Client, LiveServerTestCase

from django.test import SimpleTestCase
from django.urls import reverse

from .forms import *
from django.test import TestCase

class Setup_Class(TestCase): # test case is function

    def setUp(self):
        self.user = User.objects.create(username="user",email="user@mp.com", password="user")

class User_Form_Test(TestCase): # test the user_form

     # Valid Form Data
    def test_UserForm_valid(self):
        form = UserForm(data={'username':"user",'first_name':"user",'last_name':"user",'email': "user@mp.com", 'password': "user"})
        self.assertTrue(form.is_valid())

    # Invalid Form Data
    def test_UserForm_invalid(self):
        form = UserForm(data={'email': "",'password': "mp", 'first_name': "mp", 'phone': ""})
        self.assertFalse(form.is_valid())

class HomePageTests(SimpleTestCase):   # test the Views

    def test_home_page_status_code(self):  # test the home page status code
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200) # 200 is status code is True

    def test_view_url_by_name(self):
        response = self.client.get(reverse('index'))  # test the url by name.
        self.assertEquals(response.status_code, 200)

class EnterPageTests(SimpleTestCase):

    def test_about_page_status_code(self):
        response = self.client.get('/enter/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_by_name(self):                 # test the view url by name.
        response = self.client.get(reverse('enter'))
        self.assertEquals(response.status_code, 200)  # if test_view is assert equals then status_code =200

    def test_view_uses_correct_template(self):   # check the test view which template is used
        response = self.client.get(reverse('enter'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'Users/index.html')

    def test_about_page_does_not_contain_incorrect_html(self): # test the contain of page is incorrect
        response = self.client.get('/')
        self.assertNotContains(
            response, 'Hi there! I should not be on the page.')

