from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class SalaryRecord(models.Model):
    """
    月次給与明細レコード
    Excelの各列（月）に対応
    """
    # 基本情報
    year_month = models.DateField(
        verbose_name="年月",
        unique=True,
        help_text="給与支給月（YYYY-MM-01形式）"
    )

    # ========================================
    # 支給項目（収入）
    # ========================================

    # 固定給与
    base_salary = models.IntegerField(
        verbose_name="基本給",
        default=0,
        validators=[MinValueValidator(0)]
    )
    position_allowance = models.IntegerField(
        verbose_name="役職手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    qualification_allowance = models.IntegerField(
        verbose_name="資格手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    store_qualification_allowance = models.IntegerField(
        verbose_name="店舗資格手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    pharmacist_regional_allowance = models.IntegerField(
        verbose_name="薬剤師地区手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    relocation_allowance = models.IntegerField(
        verbose_name="転勤手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    housing_allowance = models.IntegerField(
        verbose_name="住宅手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    adjustment_allowance = models.IntegerField(
        verbose_name="調整手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    family_allowance = models.IntegerField(
        verbose_name="家族手当",
        default=0,
        validators=[MinValueValidator(0)],
        help_text="2万～3.5万"
    )

    # 時給・残業関連
    base_hourly_wage = models.IntegerField(
        verbose_name="基本時給",
        default=0,
        validators=[MinValueValidator(0)]
    )
    overtime_minutes = models.IntegerField(
        verbose_name="時間外労働時間（分）",
        default=0,
        validators=[MinValueValidator(0)]
    )
    overtime_hours = models.DecimalField(
        verbose_name="時間外労働時間（時間）",
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="自動計算：分÷60"
    )
    overtime_pay = models.IntegerField(
        verbose_name="時間外手当",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # 深夜・休日
    night_work_minutes = models.IntegerField(
        verbose_name="深夜手当（分）",
        default=0,
        validators=[MinValueValidator(0)]
    )
    night_work_pay = models.IntegerField(
        verbose_name="深夜手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    holiday_work_hours = models.DecimalField(
        verbose_name="休日出勤時間",
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    holiday_work_pay = models.IntegerField(
        verbose_name="休日出勤手当",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # その他支給
    parking_fee = models.IntegerField(
        verbose_name="駐車場代",
        default=0
    )
    commuting_allowance = models.IntegerField(
        verbose_name="通勤手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    taxable_commuting_allowance = models.IntegerField(
        verbose_name="課税通勤手当",
        default=0,
        validators=[MinValueValidator(0)]
    )
    payment_adjustment = models.IntegerField(
        verbose_name="支給精算",
        default=0
    )
    taxable_payment = models.IntegerField(
        verbose_name="課税支給",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # 支給合計
    total_payment = models.IntegerField(
        verbose_name="支給総額",
        default=0,
        help_text="自動計算：全支給項目の合計"
    )

    # ========================================
    # 計算用中間項目
    # ========================================

    dependent_family_count = models.IntegerField(
        verbose_name="扶養家族",
        default=0,
        validators=[MinValueValidator(0)]
    )
    insurance_standard_salary = models.IntegerField(
        verbose_name="保険標準報酬額",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # ========================================
    # 控除項目
    # ========================================

    # 社会保険
    health_insurance = models.IntegerField(
        verbose_name="健康保険",
        default=0,
        validators=[MinValueValidator(0)]
    )
    fire_insurance = models.IntegerField(
        verbose_name="火災保険",
        default=0,
        validators=[MinValueValidator(0)]
    )
    pension_insurance = models.IntegerField(
        verbose_name="厚生年金",
        default=0,
        validators=[MinValueValidator(0)]
    )
    employment_insurance = models.IntegerField(
        verbose_name="雇用保険",
        default=0,
        validators=[MinValueValidator(0)]
    )
    matching_contribution = models.IntegerField(
        verbose_name="マッチング拠出金",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # 税金
    taxable_amount = models.IntegerField(
        verbose_name="課税対象額",
        default=0,
        help_text="自動計算"
    )
    monthly_income_tax = models.IntegerField(
        verbose_name="月次所得税",
        default=0,
        validators=[MinValueValidator(0)]
    )
    resident_tax = models.IntegerField(
        verbose_name="住民税",
        default=0,
        validators=[MinValueValidator(0)]
    )

    # その他控除
    mutual_aid = models.IntegerField(
        verbose_name="共済会",
        default=0,
        validators=[MinValueValidator(0)]
    )
    union_fee = models.IntegerField(
        verbose_name="組合費",
        default=0,
        validators=[MinValueValidator(0)]
    )
    damage_insurance = models.IntegerField(
        verbose_name="損害保険",
        default=0,
        validators=[MinValueValidator(0)]
    )
    ltd_insurance = models.IntegerField(
        verbose_name="LTD保険",
        default=0,
        validators=[MinValueValidator(0)]
    )
    company_housing_deduction = models.IntegerField(
        verbose_name="借上社宅控除",
        default=0,
        validators=[MinValueValidator(0)]
    )
    year_end_adjustment = models.IntegerField(
        verbose_name="年末調整",
        default=0
    )

    # 控除合計
    total_deduction = models.IntegerField(
        verbose_name="控除合計",
        default=0,
        help_text="自動計算：全控除項目の合計"
    )

    # ========================================
    # 計算結果
    # ========================================

    actual_payment = models.IntegerField(
        verbose_name="実支給額",
        default=0,
        help_text="自動計算：支給総額 - 控除合計"
    )
    net_payment = models.IntegerField(
        verbose_name="差引支給額",
        default=0,
        help_text="実支給額と同じ"
    )
    difference = models.IntegerField(
        verbose_name="差額",
        default=0,
        help_text="実支給額 - 差引支給額（通常0）"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        ordering = ['-year_month']
        verbose_name = "給与明細"
        verbose_name_plural = "給与明細一覧"

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} - 手取り: {self.actual_payment:,}円"

    def calculate_all(self):
        """
        全ての計算項目を自動計算
        save()時に自動的に呼び出される
        """
        # 時間外労働時間（時間） = 時間外労働時間（分） ÷ 60
        if self.overtime_minutes:
            self.overtime_hours = Decimal(self.overtime_minutes) / Decimal(60)

        # 支給総額の計算
        self.total_payment = (
            self.base_salary +
            self.position_allowance +
            self.qualification_allowance +
            self.store_qualification_allowance +
            self.pharmacist_regional_allowance +
            self.relocation_allowance +
            self.housing_allowance +
            self.adjustment_allowance +
            self.family_allowance +
            self.overtime_pay +
            self.night_work_pay +
            self.holiday_work_pay +
            self.parking_fee +
            self.commuting_allowance +
            self.taxable_commuting_allowance +
            self.payment_adjustment +
            self.taxable_payment
        )

        # 課税対象額の計算（簡易版：支給総額 - 非課税通勤手当等）
        # ※実際のロジックはExcelの数式に合わせて調整が必要
        self.taxable_amount = self.total_payment - (self.commuting_allowance - self.taxable_commuting_allowance)

        # 控除合計の計算
        self.total_deduction = (
            self.health_insurance +
            self.fire_insurance +
            self.pension_insurance +
            self.employment_insurance +
            self.matching_contribution +
            self.monthly_income_tax +
            self.resident_tax +
            self.mutual_aid +
            self.union_fee +
            self.damage_insurance +
            self.ltd_insurance +
            self.company_housing_deduction +
            self.year_end_adjustment
        )

        # 実支給額（手取り）の計算
        self.actual_payment = self.total_payment - self.total_deduction
        self.net_payment = self.actual_payment
        self.difference = self.actual_payment - self.net_payment

    def save(self, *args, **kwargs):
        """保存時に自動計算を実行"""
        self.calculate_all()
        super().save(*args, **kwargs)

    def get_previous_month(self):
        """前月の給与レコードを取得"""
        from dateutil.relativedelta import relativedelta
        previous_month = self.year_month - relativedelta(months=1)
        try:
            return SalaryRecord.objects.get(year_month=previous_month)
        except SalaryRecord.DoesNotExist:
            return None

    def get_next_month(self):
        """翌月の給与レコードを取得"""
        from dateutil.relativedelta import relativedelta
        next_month = self.year_month + relativedelta(months=1)
        try:
            return SalaryRecord.objects.get(year_month=next_month)
        except SalaryRecord.DoesNotExist:
            return None
