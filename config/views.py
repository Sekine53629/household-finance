from django.shortcuts import render
from django.utils import timezone
from datetime import date
from dateutil.relativedelta import relativedelta
import json

from salary.models import SalaryRecord
from balance_sheet.models import MonthlyBalanceSheet
from cashflow.models import MonthlyCashFlow


def dashboard(request):
    """ダッシュボード画面"""
    current_month = date.today().replace(day=1)

    # 最新の財務情報を取得
    try:
        balance_sheet = MonthlyBalanceSheet.objects.filter(
            year_month__lte=current_month
        ).latest('year_month')
        net_worth = balance_sheet.net_worth
    except MonthlyBalanceSheet.DoesNotExist:
        balance_sheet = None
        net_worth = 0

    # 最新のキャッシュフロー
    try:
        cashflow = MonthlyCashFlow.objects.filter(
            year_month__lte=current_month
        ).latest('year_month')
        monthly_income = cashflow.total_income
        monthly_expense = cashflow.total_expense
        net_cashflow = cashflow.net_cashflow
    except MonthlyCashFlow.DoesNotExist:
        cashflow = None
        monthly_income = 0
        monthly_expense = 0
        net_cashflow = 0

    # 最近3ヶ月の給与
    recent_salaries = SalaryRecord.objects.all()[:3]

    # 純資産推移チャート用データ（過去6ヶ月）
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month = current_month - relativedelta(months=i)
        try:
            bs = MonthlyBalanceSheet.objects.get(year_month=month)
            chart_labels.append(month.strftime('%Y年%m月'))
            chart_data.append(bs.net_worth)
        except MonthlyBalanceSheet.DoesNotExist:
            chart_labels.append(month.strftime('%Y年%m月'))
            chart_data.append(0)

    context = {
        'current_month': current_month,
        'net_worth': net_worth,
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'net_cashflow': net_cashflow,
        'balance_sheet': balance_sheet,
        'recent_salaries': recent_salaries,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }

    return render(request, 'dashboard.html', context)
