from django.urls import path, register_converter

from . import views
from .converters import ThemeConverter

register_converter(ThemeConverter, 'theme')

app_name = 'filesystem'
urlpatterns = [
    #path('<theme:theme>/', views.index, name='index'),
    path('', views.index, name='index'),
    path('<int:pk>', views.detail, name='detail'),
    path('add_dir/', views.DirectoryCreateView.as_view(), name='add_dir'),
    path('del_dir/<int:pk>', views.DirectoryDeleteView.as_view(), name='del_dir'),
    path('add_file/', views.FileCreateView.as_view(), name='add_file'),
    path('del_file/<int:pk>', views.FileDeleteView.as_view(), name='del_file')
]
