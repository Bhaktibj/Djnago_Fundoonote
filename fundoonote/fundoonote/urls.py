from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt import views as jwt_views
from Users import views
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view
from django.urls import path


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet) # register the view_set to display the all users
schema_view = get_schema_view(title='Pastebin API')

urlpatterns = [
    url('schema/', schema_view),
    url('', include('Users.urls')), # include the all app urls in project urls
    url(r'^logout/$', views.user_logout, name='logout'), # logout url
    url(r'^register/$', views.register, name='register'),  # url for register
    url(r'^admin/', admin.site.urls), # admin login urls in rest Format
    url(r'^$', views.home, name='home'), # index url is call the template
    url(r'^enter/', views.enter, name='enter'), # enter is html template urls
    url('^', include('django.contrib.auth.urls')), # include all the reset password urls
    url('', include(router.urls)), # include the router url to use the display all users
    url('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    url('get_users/',views.get_users), # this view_url is display the all users in JSOn format
    url('social-auth/', include('social_django.urls', namespace="social")),
    url('api-auth/',include('rest_framework.urls', namespace='rest_framework')),
    url('rest_login/', views.RestLogin.as_view(), name='rest_login'),
    url(r'^docs/$', get_swagger_view(title='API Docs'), name='api_docs'), # swagger
    # url('image_upload', views.image_view, name = 'image_upload'),

]
# if settings.DEBUG:
#         urlpatterns += static(settings.MEDIA_URL,
#                               document_root=settings.MEDIA_ROOT)