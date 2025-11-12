from django.contrib import admin
from .models import Asset, Liability, MonthlyBalanceSheet


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'current_value',
        'institution',
        'is_active',
        'updated_at'
    ]
    list_filter = ['category', 'is_active', 'institution']
    search_fields = ['name', 'institution', 'account_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'category', 'current_value', 'is_active')
        }),
        ('取得情報', {
            'fields': ('acquisition_date', 'acquisition_cost')
        }),
        ('詳細情報', {
            'fields': ('institution', 'account_number')
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'category',
        'current_balance',
        'monthly_payment',
        'remaining_months',
        'lender',
        'is_active'
    ]
    list_filter = ['category', 'is_active', 'lender']
    search_fields = ['name', 'lender', 'account_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'category', 'is_active')
        }),
        ('負債詳細', {
            'fields': (
                'current_balance',
                'original_amount',
                'interest_rate',
                'monthly_payment',
                'remaining_months'
            )
        }),
        ('日付情報', {
            'fields': ('start_date', 'maturity_date', 'payment_date')
        }),
        ('金融機関情報', {
            'fields': ('lender', 'account_number')
        }),
        ('メモ', {
            'fields': ('memo',)
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(MonthlyBalanceSheet)
class MonthlyBalanceSheetAdmin(admin.ModelAdmin):
    list_display = [
        'year_month',
        'total_assets',
        'total_liabilities',
        'net_worth',
        'net_worth_change',
        'financial_health'
    ]
    list_filter = ['financial_health', 'year_month']
    readonly_fields = [
        # 資産
        'cash', 'bank_deposits', 'current_assets',
        'stocks', 'bonds', 'investment_trusts', 'crypto', 'investment_assets',
        'real_estate', 'vehicles', 'other_assets', 'fixed_assets',
        'total_assets',
        # 負債
        'credit_card_debt', 'short_term_loans', 'current_liabilities',
        'housing_loan', 'car_loan', 'student_loan', 'other_loans', 'long_term_liabilities',
        'total_liabilities',
        # 純資産
        'net_worth', 'net_worth_change', 'net_worth_change_ratio',
        # 指標
        'debt_ratio', 'liquidity_ratio',
        'financial_health', 'health_message',
        'created_at', 'updated_at'
    ]

    fieldsets = (
        ('年月', {
            'fields': ('year_month',)
        }),
        ('資産 - 流動資産', {
            'fields': ('cash', 'bank_deposits', 'current_assets')
        }),
        ('資産 - 投資資産', {
            'fields': ('stocks', 'bonds', 'investment_trusts', 'crypto', 'investment_assets')
        }),
        ('資産 - 固定資産', {
            'fields': ('real_estate', 'vehicles', 'other_assets', 'fixed_assets')
        }),
        ('資産合計', {
            'fields': ('total_assets',)
        }),
        ('負債 - 短期負債', {
            'fields': ('credit_card_debt', 'short_term_loans', 'current_liabilities')
        }),
        ('負債 - 長期負債', {
            'fields': ('housing_loan', 'car_loan', 'student_loan', 'other_loans', 'long_term_liabilities')
        }),
        ('負債合計', {
            'fields': ('total_liabilities',)
        }),
        ('純資産', {
            'fields': ('net_worth', 'net_worth_change', 'net_worth_change_ratio')
        }),
        ('財務指標', {
            'fields': ('debt_ratio', 'liquidity_ratio')
        }),
        ('健全性評価', {
            'fields': ('financial_health', 'health_message')
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
