from django.urls import path
from user.views import Register, Profile, UserLogin

urlpatterns = [
    path('register/', Register.as_view()),
    path('manage/', Profile.as_view()),
    path('login/', UserLogin.as_view()),
]