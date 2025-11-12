from django.contrib import admin
from .models import FixedExpense, Income, VariableExpense, MonthlyCashFlow


@admin.register(FixedExpense)
class FixedExpenseAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'monthly_amount', 'payment_date', 'is_loan', 'remaining_months', 'is_active']
    list_filter = ['category', 'is_active', 'is_loan']
    search_fields = ['name']
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'category', 'monthly_amount', 'payment_date', 'is_active')
        }),
        ('ローン情報', {
            'fields': ('is_loan', 'remaining_months', 'start_date', 'end_date')
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
    )


@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ['year_month', 'category', 'amount', 'source', 'received_date']
    list_filter = ['category', 'year_month']
    search_fields = ['source']
    date_hierarchy = 'year_month'


@admin.register(VariableExpense)
class VariableExpenseAdmin(admin.ModelAdmin):
    list_display = ['year_month', 'category', 'amount', 'expense_date', 'description']
    list_filter = ['category', 'year_month']
    search_fields = ['description']
    date_hierarchy = 'year_month'


@admin.register(MonthlyCashFlow)
class MonthlyCashFlowAdmin(admin.ModelAdmin):
    list_display = ['year_month', 'total_income', 'total_expense', 'net_cashflow', 'closing_balance', 'risk_level']
    list_filter = ['risk_level', 'year_month']
    readonly_fields = [
        'salary_net', 'total_income', 'total_fixed_expense', 'total_credit_payment',
        'total_variable_expense', 'total_expense', 'net_cashflow', 'monthly_change',
        'risk_level', 'risk_message', 'created_at', 'updated_at'
    ]

    fieldsets = (
        ('年月', {
            'fields': ('year_month',)
        }),
        ('口座残高', {
            'fields': ('opening_balance', 'mid_month_balance', 'closing_balance', 'monthly_change', 'savable_amount')
        }),
        ('収入', {
            'fields': ('salary_net', 'bonus', 'side_income', 'rent_income', 'temporary_income', 'refund', 'other_income', 'total_income')
        }),
        ('固定費', {
            'fields': ('housing_loan', 'other_loans', 'insurance', 'subscription', 'utilities', 'communication', 'rent', 'total_fixed_expense')
        }),
        ('クレジットカード', {
            'fields': ('credit_card_payments', 'total_credit_payment')
        }),
        ('変動費', {
            'fields': ('food', 'daily_goods', 'clothing', 'social', 'transport', 'medical', 'education', 'entertainment', 'other_variable', 'total_variable_expense')
        }),
        ('合計', {
            'fields': ('total_expense', 'net_cashflow')
        }),
        ('リスク判定', {
            'fields': ('risk_level', 'risk_message')
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """保存時に自動計算"""
        obj.calculate_all()
        super().save_model(request, obj, form, change)
