from django.urls import path

from . import views

urlpatterns = [
    path("guests/search/", views.search_guests, name="search_guests"),
    path("meals/", views.list_meals, name="list_meals"),
    path("rsvp/submit/", views.submit_rsvp, name="submit_rsvp"),
]
