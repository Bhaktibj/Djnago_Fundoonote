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

    # list of Notes URL
    path("Notes/List/", views.NotesList.as_view(), name="note_list"),
    path("Notes/Detail/<int:pk>/", views.NotesDetail.as_view(), name="note_detail"),
    path("Notes/Create/", views.CreateNotes.as_view(), name="note_create"),
    path("Notes/Delete/<int:pk>/", views.NotesDelete.as_view(),name='note_delete'),
    path("Notes/Update/<int:pk>/", views.NotesUpdate.as_view(), name='note_update'),
    path("Notes/Trash/<int:pk>/", views.TrashView.as_view(), name='note_trash'),
    path("Notes/Archive/<int:pk>/", views.ArchiveNotes.as_view(), name='note_archive'),
    path("Notes/ArchiveList/", views.ArchiveList.as_view(), name='note_archive_list'),
    path("Notes/Reminder/<int:pk>/", views.ReminderNotes.as_view(), name='note_reminder'),
    path("Notes/TrashList/", views.TrashList.as_view(), name='trash_list'),
    path("Notes/Pagination/", views.NotesListPage.as_view(), name="note_page"),

    # List of label URL
    path("Label/List/", views.LabelList.as_view(), name="label_list"),
    path("Label/Detail/<int:pk>/", views.LabelUpdateDetail.as_view(), name="label_detail"),
    path("Label/Create/", views.CreateLabel.as_view(), name="label_create"),
    path("Label/Delete/<int:pk>/", views.LabelDelete.as_view(), name='delete_label'),
    path("Label/Pagination/",views.LabelListPage.as_view(), name="label_page"),

    # List of the AWS bucket url
    path("bucket_aws/create/", views.create_aws_bucket.as_view(), name='create_bucket'),
    path("bucket_aws/delete/<int:pk>/", views.delete_aws_bucket.as_view(), name='delete_bucket'),
    path("bucket_aws/List/", views.Bucket_List.as_view(), name="bucket_list"),
    path("upload/", views.upload_s3, name="upload"),

    # search operations url
    path("Search/user/", views.UserListView.as_view(), name="user"),
    path("Search/notes/",views.NotesListView.as_view(), name="note"),
    path("search/", views.search, name='search'),

    path('Rest-auth/', include('rest_auth.urls')),
    path('Rest-auth/',ConfirmEmailView.as_view(),name="view"),
]
