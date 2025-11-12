from django.urls import path
from django.views.generic import TemplateView

app_name = 'balance_sheet'

urlpatterns = [
    path('', TemplateView.as_view(template_name='balance_sheet/list.html'), name='list'),
]
