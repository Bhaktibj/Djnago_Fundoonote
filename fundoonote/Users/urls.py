from django.conf.urls import include,url
from . import views

app_name = 'Users'
urlpatterns = [
    url(r'^register/$', views.register, name='register'), # url for register
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
   views.activate, name='activate'),# url activate the user registration
    url('rest_login/', views.RestLogin.as_view(), name='rest_login'),

    # url is rest_Login user


]
