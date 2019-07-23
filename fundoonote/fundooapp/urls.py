from allauth.account.views import ConfirmEmailView
from django.conf.urls import include,url

from . import views
from django.urls import path
from django.contrib import admin

app_name = 'fundooapp'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^register/$', views.register, name='register'), # url for register
    url(r'user_login/', views.user_login, name='login'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.activate, name='activate'),# url activate the user registration
    path(r'Notes/List/', views.NotesList.as_view(), name="note_list"),
    path(r'Notes/Detail/<int:pk>/', views.NotesDetail.as_view(), name="note_detail"),
    path(r'Notes/Create/', views.CreateNotes.as_view(), name="note_create"),
    path(r'Notes/Delete/<int:pk>/', views.NotesDelete.as_view(),name='note_delete'),
    path(r'Notes/Update/<int:pk>/', views.NotesUpdate.as_view(), name='note_update'),
    path(r'Notes/Trash/<int:pk>/', views.TrashView.as_view(), name='note_trash'),
    path(r'Notes/Archive/<int:pk>/', views.ArchiveNotes.as_view(), name='note_archive'),
    path(r'Notes/ArchiveList/', views.ArchiveList.as_view(), name='note_archive_list'),
    path(r'Notes/Reminder/<int:pk>/', views.ReminderNotes.as_view(), name='note_reminder'),
    path(r'Notes/TrashList/', views.TrashList.as_view(), name='trash_list'),
    path(r'Notes/Pagination/', views.NotesListPage.as_view(), name="note_page"),
    path(r'Label/List/', views.LabelList.as_view(), name="label_list"),
    path(r'Label/Detail/<int:pk>/', views.LabelUpdateDetail.as_view(), name="label_detail"),
    path(r'Label/Create/', views.CreateLabel.as_view(), name="label_create"),
    path(r'Label/Delete/<int:pk>/', views.LabelDelete.as_view(), name='delete_label'),
    path(r'Label/Pagination/',views.LabelListPage.as_view(), name="label_page"),
    path(r'Label/get_label_note/<int:pk>/', views.LabelFromNotes.as_view(), name="label_page"),
    path(r'aws/create/', views.CreateBucket.as_view(), name='create_bucket'),
    path(r'aws/delete/<int:pk>/', views.DeleteBucket.as_view(), name='delete_bucket'),
    path(r'aws/List/', views.BucketList.as_view(), name="bucket_list"),
    path(r'aws/upload_s3/<int:pk>/', views.s3_upload, name='upload_image'),
    path(r'aws/object/<int:pk>/', views.GetBucketObject.as_view(), name='get_object'),
    path(r'Search/user/', views.UserListView.as_view(), name="user"),
    path(r'Search/notes/',views.NotesListView.as_view(), name="note"),
    path(r'search/', views.search, name='search'),
    path(r'rest-auth/', include('rest_auth.urls')),
    path(r'rest-auth/',ConfirmEmailView.as_view(),name="view"),
    path(r'rest_api/register/', views.RestUserRegister.as_view(), name='rest_register'),
    path(r'rest_api/login/', views.Login.as_view(), name='rest_login'),
]

