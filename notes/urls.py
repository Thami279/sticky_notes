from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/notes', views.NoteViewSet, basename='api-notes')
router.register(r'api/tags', views.TagViewSet, basename='api-tags')
urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('new/', views.note_create, name='note_create'),
    path('<int:pk>/', views.note_detail, name='note_detail'),
    path('<int:pk>/edit/', views.note_update, name='note_update'),
    path('<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('export/csv/', views.export_notes_csv, name='export_notes_csv'),
    path('import/csv/', views.import_notes_csv, name='import_notes_csv'),
    path('', include(router.urls)),
]
