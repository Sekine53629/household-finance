from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import SalaryRecord


class SalaryListView(ListView):
    """給与明細一覧"""
    model = SalaryRecord
    template_name = 'salary/list.html'
    context_object_name = 'salaries'
    paginate_by = 12


class SalaryDetailView(DetailView):
    """給与明細詳細"""
    model = SalaryRecord
    template_name = 'salary/detail.html'
    context_object_name = 'salary'
