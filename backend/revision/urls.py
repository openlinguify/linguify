from django.urls import path
from . import views

urlpatterns = [
    path('', views.revision, name='revision'),
    path('add-revision/', views.add_revision, name='add_revision'),
    path('list/', views.reviewed_vocabulaire_list, name='reviewed_vocabulaire_list'),
    path('edit/<int:revision_id>/', views.edit_revision, name='edit_revision'),
    path('delete/<int:revision_id>/', views.delete_revision, name='delete_revision'),
    path('delete_selected/', views.delete_selected_revisions, name='delete_selected_revisions'),
    path('import/', views.import_revisions, name='import_revisions'),
    path('export/', views.export_revisions, name='export_revisions'),
    path('revision-cards/', views.revision_card, name='revision_cards'),
    path('revision-list/', views.revision_list, name='revision_list'),
    path('mark-as-known/<int:revision_id>/', views.mark_as_known, name='mark_as_known'),
    path('mark-as-not-known/<int:revision_id>/', views.mark_as_not_known, name='mark_as_not_known'),
    path('reset-revisions/', views.reset_revisions, name='reset_revisions'),
]
