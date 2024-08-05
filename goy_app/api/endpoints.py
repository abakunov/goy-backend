from django.urls import path, include
from rest_framework.generics import CreateAPIView
from .views import *

api_urls = [
    path('hello/', CreateUserView.as_view()),
    # path('test/', TestView.as_view()),
]