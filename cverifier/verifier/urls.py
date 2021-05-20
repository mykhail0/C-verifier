from django.urls import path

from . import views

app_name = 'verifier'
urlpatterns = [
    path('', views.index, name='index'),
    path('dirform/', views.DirectoryCreateView.as_view(), name='dirform'),
    path('fileform/', views.FileCreateView.as_view(), name='fileform'),
    path('delete_dir/<int:pk>', views.DirectoryDelete.as_view(), name='delete_dir'),
    path('delete_file/<int:pk>', views.FileDelete.as_view(), name='delete_file'),
    path('code/<int:pk>', views.code, name='code'),
]
