from django.urls import path
from .views import *

urlpatterns = [
    path('register/', registerUser, name = 'register'),
    path('login/', loginUser, name = 'login'),
    path('logout/', logoutUser, name = 'logout'),
    path('check/', authenticated_user, name = 'check'),
    path('create/', createBlog, name='create'),
    path('get/<int:id>/', getBlogById, name='get'),
    path('admin/', adminPage, name='admin'),
    path('normal/', normalPage, name='normal')
]
