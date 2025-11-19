from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    path('', views.MediaListView.as_view(), name='media_list'),
    path('media/<str:media_type>/<int:pk>/', views.MediaDetailView.as_view(), name='media_detail'),
    path('media/<str:media_type>/<int:item_id>/action/', views.media_action, name='media_action'),
    path('media/create/', views.MediaCreateView.as_view(), name='media_create'),
    path('media/<str:media_type>/<int:pk>/borrow/', views.borrow_media, name='borrow_media'),
    path('media/<str:media_type>/<int:pk>/download/', views.download_media, name='download_media'),
]