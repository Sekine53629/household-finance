from django.contrib import admin
from .models import SalaryRecord


@admin.register(SalaryRecord)
class SalaryRecordAdmin(admin.ModelAdmin):
    list_display = [
        'year_month',
        'base_salary',
        'total_payment',
        'total_deduction',
        'actual_payment',
        'created_at'
    ]
    list_filter = ['year_month', 'created_at']
    search_fields = ['memo']
    readonly_fields = [
        'overtime_hours',
        'total_payment',
        'taxable_amount',
        'total_deduction',
        'actual_payment',
        'net_payment',
        'difference',
        'created_at',
        'updated_at'
    ]

    fieldsets = (
        ('基本情報', {
            'fields': ('year_month', 'memo')
        }),
        ('固定給与', {
            'fields': (
                'base_salary',
                'position_allowance',
                'qualification_allowance',
                'store_qualification_allowance',
                'pharmacist_regional_allowance',
                'relocation_allowance',
                'housing_allowance',
                'adjustment_allowance',
                'family_allowance',
            )
        }),
        ('時給・残業', {
            'fields': (
                'base_hourly_wage',
                'overtime_minutes',
                'overtime_hours',
                'overtime_pay',
            )
        }),
        ('深夜・休日', {
            'fields': (
                'night_work_minutes',
                'night_work_pay',
                'holiday_work_hours',
                'holiday_work_pay',
            )
        }),
        ('その他支給', {
            'fields': (
                'parking_fee',
                'commuting_allowance',
                'taxable_commuting_allowance',
                'payment_adjustment',
                'taxable_payment',
            )
        }),
        ('支給合計', {
            'fields': ('total_payment',)
        }),
        ('計算用', {
            'fields': (
                'dependent_family_count',
                'insurance_standard_salary',
                'taxable_amount',
            )
        }),
        ('社会保険', {
            'fields': (
                'health_insurance',
                'fire_insurance',
                'pension_insurance',
                'employment_insurance',
                'matching_contribution',
            )
        }),
        ('税金', {
            'fields': (
                'monthly_income_tax',
                'resident_tax',
            )
        }),
        ('その他控除', {
            'fields': (
                'mutual_aid',
                'union_fee',
                'damage_insurance',
                'ltd_insurance',
                'company_housing_deduction',
                'year_end_adjustment',
            )
        }),
        ('控除合計', {
            'fields': ('total_deduction',)
        }),
        ('計算結果', {
            'fields': (
                'actual_payment',
                'net_payment',
                'difference',
            )
        }),
        ('メタデータ', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        """保存時に自動計算を実行"""
        obj.calculate_all()
        super().save_model(request, obj, form, change)
