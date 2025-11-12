from django.urls import path
from . import views

app_name = 'salary'

urlpatterns = [
    path('', views.SalaryListView.as_view(), name='list'),
    path('<int:pk>/', views.SalaryDetailView.as_view(), name='detail'),
]
