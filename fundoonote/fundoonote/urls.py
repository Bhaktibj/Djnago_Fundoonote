from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt import views as jwt_views
from fundooapp import views
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet) # register the view_set to display the all users
router.register(r'elastic_search',views.NotesDocumentViewSet,basename='elastic_search')
schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    url('schema/', schema_view),
    url('', include('fundooapp.urls')), # include the all app urls in project urls
    url(r'^register/$', views.register, name='register'),  # url for register
    url(r'^admin/', admin.site.urls), # admin login urls in rest Format
    url(r'^logout/', views.user_logout, name='logout'),
    url(r'^$', views.home, name='home'), # index url is call the template
    url(r'^enter/', views.enter, name='enter'), # enter is html template urls
    url('', include(router.urls)), # include the router url to use the display all users
    url('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('get_users/',views.get_users), # this view_url is display the all users in JSOn format
    url('social-auth/', include('social_django.urls', namespace="social")),
    url('',include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/$', get_swagger_view(title='API Docs'), name='api_docs'), # swagger
    url(r'api/', include_docs_urls(title='Notes API')), # CoreApi
    url('',include('django.contrib.auth.urls')),
    url('RestAPI/register/', views.RestUserRegister.as_view(), name='rest_register'),
    url('RestAPI/login/', views.RestLogin.as_view(), name='rest_login'),
]


