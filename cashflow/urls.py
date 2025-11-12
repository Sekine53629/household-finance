from django.urls import path
from django.views.generic import TemplateView

app_name = 'cashflow'

urlpatterns = [
    path('', TemplateView.as_view(template_name='cashflow/list.html'), name='list'),
]
