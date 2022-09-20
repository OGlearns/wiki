from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("search_results/", views.search_results, name="search_results"),
    path("new_page/", views.new_page, name="new_page"),
    path("<str:title>/", views.entry_page, name="title"),
    path("<str:title>/edit_page/", views.edit_page, name="edit_page"),
    path("/random/", views.random, name="random"),
    ]
