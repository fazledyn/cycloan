from django.urls import path, include
from views import loginView

# lcoalhost:5000/login

urlpatterns = [
    path('login/', loginView ),
]
