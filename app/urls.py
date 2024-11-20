from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path('', views.dangnhap, name='dangnhap'),
    path('home/', views.home, name='home'),
    path('dangky/', views.dangky, name='dangky'),
    path('dangnhap/', views.dangnhap, name='dangnhap'),
    path('danhsachnhac/', views.danhsachnhac, name='danhsachnhac'),
    path('thuvien/', views.thuvien, name='thuvien'),
]