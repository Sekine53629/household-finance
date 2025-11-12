from django.contrib import admin
from .models import CreditCard, ShortTermLoan, CreditUsage, PaymentSchedule


@admin.register(CreditCard)
class CreditCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'closing_date', 'payment_date', 'bank_account', 'credit_limit', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'bank_account']
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'card_number_last4', 'is_active')
        }),
        ('締め日・引落日', {
            'fields': ('closing_date', 'payment_date', 'bank_account')
        }),
        ('限度額', {
            'fields': ('credit_limit',)
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
    )


@admin.register(ShortTermLoan)
class ShortTermLoanAdmin(admin.ModelAdmin):
    list_display = ['name', 'monthly_payment', 'remaining_months', 'total_remaining', 'payment_date', 'is_active']
    list_filter = ['is_active', 'start_date']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'is_active')
        }),
        ('ローン詳細', {
            'fields': ('monthly_payment', 'remaining_months', 'payment_date', 'start_date')
        }),
        ('引落先', {
            'fields': ('bank_account',)
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(CreditUsage)
class CreditUsageAdmin(admin.ModelAdmin):
    list_display = ['usage_date', 'credit_card', 'amount', 'merchant', 'category', 'payment_date', 'is_paid']
    list_filter = ['credit_card', 'category', 'is_paid', 'usage_date']
    search_fields = ['merchant', 'memo']
    date_hierarchy = 'usage_date'
    readonly_fields = ['payment_date', 'created_at', 'updated_at']

    fieldsets = (
        ('利用情報', {
            'fields': ('credit_card', 'usage_date', 'amount', 'merchant', 'category')
        }),
        ('引落情報', {
            'fields': ('payment_date', 'is_paid')
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """保存時に引落予定日を自動計算"""
        if not obj.payment_date:
            obj.payment_date = obj.calculate_payment_date()
        super().save_model(request, obj, form, change)


@admin.register(PaymentSchedule)
class PaymentScheduleAdmin(admin.ModelAdmin):
    list_display = ['year_month', 'total_credit_payment', 'total_loan_payment', 'total_payment', 'risk_level']
    list_filter = ['risk_level', 'year_month']
    readonly_fields = [
        'credit_card_payments',
        'total_credit_payment',
        'loan_payments',
        'total_loan_payment',
        'total_payment',
        'risk_level',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('年月', {
            'fields': ('year_month',)
        }),
        ('クレジットカード引落', {
            'fields': ('credit_card_payments', 'total_credit_payment')
        }),
        ('ローン支払', {
            'fields': ('loan_payments', 'total_loan_payment')
        }),
        ('合計', {
            'fields': ('total_payment', 'risk_level')
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
