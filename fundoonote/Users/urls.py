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
    # list of Notes URL
    path("Notes/List/", views.NotesList.as_view(), name="note_list"),
    path("Notes/Detail/<int:pk>/", views.NotesDetail.as_view(), name="note_detail"),
    path("Notes/Create/", views.CreateNotes.as_view(), name="note"),
    path("Notes/Delete/<int:pk>/", views.NotesDelete.as_view(),name='delete'),
    path("Notes/Trash/<int:pk>/", views.TrashView.as_view(), name='trash'),
    path("Notes/Archive/<int:pk>/", views.ArchiveNotes.as_view(), name='archive'),
    path("Notes/ArchiveList/", views.ArchiveList.as_view(), name='archive'),
    path("Notes/Reminder/<int:pk>/", views.ReminderNotes.as_view(), name='reminder'),
    path("Notes/TrashList/<trash>", views.TrashList.as_view(), name='trash_list'),
    path("Notes/Pagination/", views.NotesListPage.as_view(), name="note_list"),

    # List of label URL
    path("Label/List/", views.LabelList.as_view(), name="label_list"),
    path("Label/Detail/<int:pk>/", views.LabelDetail.as_view(), name="label_detail"),
    path("Label/Create/", views.CreateLabel.as_view(), name="label"),
    path("Label/Delete/<int:pk>/", views.LabelDelete.as_view(), name='delete'),
    url(r'^search/', views.search, name='search'),
]

