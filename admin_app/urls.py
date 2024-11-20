from django.urls import path
from . import views

app_name = 'admin_app'
urlpatterns = [
    path('admin_home/', views.admin_home, name='admin_home'),
    path('user/', views.user, name='user'),
    path('song/', views.song, name='song'),
    path('artist/', views.artist, name='artist'),
    path('playlist/', views.playlist, name='playlist'),
    path('category/', views.category, name='category'),
    path('delete_user/<str:user_id>/', views.delete_user, name='delete_user'),
    path('songs/delete/<str:song_id>/', views.delete_song, name='delete_song'),
    path('add_song/', views.add_song, name='add_song'),
]