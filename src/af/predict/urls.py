from django.urls import path
from .views import trigger, result


urlpatterns = [
    path("trigger", trigger),
    path("result/<str:id>", result),
]
