from django.conf.urls import include,url
from . import views
from django.urls import path
from django.contrib import admin

app_name = 'Users'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', views.register, name='register'), # url for register
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.activate, name='activate'),# url activate the user registration
    url('rest_login/', views.RestLogin.as_view(), name='rest_login'),
    # urls  Notes
    url(r'^notes/$', views.note_list, name='note_list'),
    url(r'^new/$', views.note_create, name='note_new'),
    url(r'^edit/(?P<pk>\d+)$', views.note_update, name='note_edit'),
    url(r'^delete/(?P<pk>\d+)$', views.note_delete, name='note_delete'),
    # urls Labels
    url(r'^labels/$', views.label_list, name='labels_list'),
    url(r'^new_labels$', views.label_create, name='labels_new'),
    url(r'^edit_labels/(?P<pk>\d+)$', views.label_update, name='labels_edit'),
    url(r'^delete_labels/(?P<pk>\d+)$', views.label_delete, name='labels_delete'),


]

