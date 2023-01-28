from django.urls import path
from . import views

urlpatterns = [
    path("", views.getRoutes, name=""),
    path("rooms/", views.getRooms, name=""),
    path("rooms/<str:pk>/", views.getRoom, name=""),
]
 