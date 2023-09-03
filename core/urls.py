from django.urls import path
from core.views import Index

urlpatterns = [
    path("", view=Index.as_view(), name="index")
]
