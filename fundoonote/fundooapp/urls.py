from allauth.account.views import ConfirmEmailView
from django.conf.urls import include,url

from . import views
from django.urls import path
from django.contrib import admin

app_name = 'fundooapp'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', views.register, name='register'), # url for register
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.activate, name='activate'),# url activate the user registration
    url('RestAPI/register/', views.RestUserRegister.as_view(), name='rest_register'),
    url('RestAPI/login/', views.RestLogin.as_view(), name='rest_login'),

    # list of Notes URL
    path("Notes/List/", views.NotesList.as_view(), name="note_list"),
    path("Notes/Detail/<int:pk>/", views.NotesDetail.as_view(), name="note_detail"),
    path("Notes/Create/", views.CreateNotes.as_view(), name="note"),
    path("Notes/Delete/<int:pk>/", views.NotesDelete.as_view(),name='delete'),
    path("Notes/Trash/<int:pk>/", views.TrashView.as_view(), name='trash'),
    path("Notes/Archive/<int:pk>/", views.ArchiveNotes.as_view(), name='archive'),
    path("Notes/ArchiveList/", views.ArchiveList.as_view(), name='archive'),
    path("Notes/Reminder/<int:pk>/", views.ReminderNotes.as_view(), name='reminder'),
    path("Notes/TrashList/", views.TrashList.as_view(), name='trash_list'),
    path("Notes/Pagination/", views.NotesListPage.as_view(), name="note_page"),
    # List of label URL
    path("Label/List/", views.LabelList.as_view(), name="label_list"),
    path("Label/Detail/<int:pk>/", views.LabelDetail.as_view(), name="label_detail"),
    path("Label/Create/", views.CreateLabel.as_view(), name="label"),
    path("Label/Delete/<int:pk>/", views.LabelDelete.as_view(), name='delete'),
    path("Label/Pagination/",views.LabelListPage.as_view(), name="label_page"),
    path("up/",views.upload_s3,name="upload"),
    path("create/", views.create_aws_bucket, name='create'),
    path("delete/", views.delete_aws_bucket, name='delete'),
    path("load/", views.aws_exist_bucket, name='delete'),

    # Urls for Search Filter
    path("Search/user/", views.UserListView.as_view(), name="user"),
    path("Search/notes/",views.NotesListView.as_view(), name="note"),
    url(r'^search/', views.search, name='search'),
    # Urls for Rest fundooapp
    path('RestUsers/', include('rest_auth.urls')),
    path('RestUsers/registration/', include('rest_auth.registration.urls')),
    path('RestUsers/',ConfirmEmailView.as_view(),name="view"),

]

