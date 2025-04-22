from django.contrib import admin
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
]
from django.contrib import admin
from django.urls import path
from .views import CompanyView, UserView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/companies/', CompanyView.as_view()),
    path('api/users/', UserView.as_view()),
]
