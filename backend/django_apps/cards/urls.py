# cards/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.CardListView.as_view(),
        name="card_list"
    ),
    path(
        "new/",
        views.CardCreateView.as_view(),
        name="card_create"
    ),
    path(
        "edit/<int:pk>/",
        views.CardUpdateView.as_view(),
        name="card_update"
    ),
]