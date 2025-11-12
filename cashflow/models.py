from django.db import models
from django.core.validators import MinValueValidator
from datetime import date


class FixedExpense(models.Model):
    """
    固定費マスタ
    ローン、サブスク、保険など毎月固定で発生する支出
    """
    CATEGORY_CHOICES = [
        ('loan', 'ローン'),
        ('insurance', '保険'),
        ('subscription', 'サブスク'),
        ('utility', '光熱費'),
        ('communication', '通信費'),
        ('rent', '家賃'),
        ('other', 'その他固定費'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="費目名",
        help_text="例: 住宅ローン、Netflix、ahamo"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="カテゴリ"
    )
    monthly_amount = models.IntegerField(
        verbose_name="月額",
        validators=[MinValueValidator(0)]
    )
    payment_date = models.IntegerField(
        verbose_name="支払日",
        validators=[MinValueValidator(1)],
        null=True,
        blank=True,
        help_text="月の何日に支払うか"
    )

    # ローンの場合
    is_loan = models.BooleanField(
        default=False,
        verbose_name="ローンか"
    )
    remaining_months = models.IntegerField(
        verbose_name="残回数",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # ステータス
    is_active = models.BooleanField(
        default=True,
        verbose_name="有効"
    )
    start_date = models.DateField(
        verbose_name="開始日",
        null=True,
        blank=True
    )
    end_date = models.DateField(
        verbose_name="終了日",
        null=True,
        blank=True,
        help_text="ローン完済日など"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "固定費"
        verbose_name_plural = "固定費一覧"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.monthly_amount:,}円/月"

    def total_remaining(self):
        """残債総額（ローンの場合）"""
        if self.is_loan and self.remaining_months:
            return self.monthly_amount * self.remaining_months
        return 0


class Income(models.Model):
    """
    収入記録
    給与以外の副収入・臨時収入を管理
    """
    CATEGORY_CHOICES = [
        ('side_business', '事業所得'),
        ('rent_income', '家賃収入'),
        ('investment', '投資収入'),
        ('refund', '還付金'),
        ('bonus', '賞与'),
        ('temporary', '臨時収入'),
        ('other', 'その他'),
    ]

    year_month = models.DateField(
        verbose_name="年月",
        help_text="収入月（YYYY-MM-01形式）"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="カテゴリ"
    )
    amount = models.IntegerField(
        verbose_name="金額",
        validators=[MinValueValidator(0)]
    )
    source = models.CharField(
        max_length=200,
        verbose_name="収入源",
        blank=True,
        help_text="例: ○○株式会社、マイニング、還付金"
    )
    received_date = models.DateField(
        verbose_name="入金日",
        null=True,
        blank=True
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "収入"
        verbose_name_plural = "収入一覧"
        ordering = ['-year_month', '-received_date']

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} {self.get_category_display()} {self.amount:,}円"


class VariableExpense(models.Model):
    """
    変動費記録
    月ごとに変動する支出
    """
    CATEGORY_CHOICES = [
        ('food', '食費'),
        ('daily_goods', '日用品'),
        ('clothing', '衣服美容'),
        ('social', '交際費'),
        ('transport', '交通費'),
        ('medical', '医療費'),
        ('education', '教養・教育'),
        ('entertainment', '趣味娯楽'),
        ('other', 'その他'),
    ]

    year_month = models.DateField(
        verbose_name="年月",
        help_text="支出月（YYYY-MM-01形式）"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="カテゴリ"
    )
    amount = models.IntegerField(
        verbose_name="金額",
        validators=[MinValueValidator(0)]
    )
    expense_date = models.DateField(
        verbose_name="支出日",
        null=True,
        blank=True
    )
    description = models.CharField(
        max_length=200,
        verbose_name="内容",
        blank=True
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "変動費"
        verbose_name_plural = "変動費一覧"
        ordering = ['-year_month', '-expense_date']

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} {self.get_category_display()} {self.amount:,}円"


class MonthlyCashFlow(models.Model):
    """
    月次キャッシュフロー統合
    収入・支出・口座残高をすべて統合管理
    """
    year_month = models.DateField(
        verbose_name="年月",
        unique=True,
        help_text="対象月（YYYY-MM-01形式）"
    )

    # ========================================
    # 口座残高
    # ========================================

    opening_balance = models.IntegerField(
        verbose_name="口座残高（期首）",
        default=0,
        help_text="月初の残高"
    )
    mid_month_balance = models.IntegerField(
        verbose_name="口座残高（27日）",
        default=0,
        blank=True
    )
    closing_balance = models.IntegerField(
        verbose_name="口座残高（期末）",
        default=0,
        help_text="月末の残高"
    )
    monthly_change = models.IntegerField(
        verbose_name="月変動値",
        default=0,
        help_text="期末 - 期首"
    )
    savable_amount = models.IntegerField(
        verbose_name="預金可能額",
        default=0
    )

    # ========================================
    # 収入
    # ========================================

    salary_net = models.IntegerField(
        verbose_name="給与手取り",
        default=0,
        help_text="SalaryRecordから自動取得"
    )
    bonus = models.IntegerField(
        verbose_name="賞与",
        default=0
    )
    side_income = models.IntegerField(
        verbose_name="事業所得",
        default=0
    )
    rent_income = models.IntegerField(
        verbose_name="家賃収入",
        default=0
    )
    temporary_income = models.IntegerField(
        verbose_name="臨時収入",
        default=0
    )
    refund = models.IntegerField(
        verbose_name="還付金",
        default=0
    )
    other_income = models.IntegerField(
        verbose_name="その他収入",
        default=0
    )
    total_income = models.IntegerField(
        verbose_name="収入合計",
        default=0
    )

    # ========================================
    # 固定費
    # ========================================

    housing_loan = models.IntegerField(
        verbose_name="住宅ローン",
        default=0
    )
    other_loans = models.IntegerField(
        verbose_name="その他ローン",
        default=0
    )
    insurance = models.IntegerField(
        verbose_name="保険料",
        default=0
    )
    subscription = models.IntegerField(
        verbose_name="サブスク",
        default=0
    )
    utilities = models.IntegerField(
        verbose_name="光熱費",
        default=0
    )
    communication = models.IntegerField(
        verbose_name="通信費",
        default=0
    )
    rent = models.IntegerField(
        verbose_name="家賃",
        default=0
    )
    total_fixed_expense = models.IntegerField(
        verbose_name="固定費合計",
        default=0
    )

    # ========================================
    # クレジットカード
    # ========================================

    credit_card_payments = models.JSONField(
        verbose_name="クレカ引落",
        default=dict,
        help_text="{'カード名': 金額}"
    )
    total_credit_payment = models.IntegerField(
        verbose_name="クレカ合計",
        default=0
    )

    # ========================================
    # 変動費
    # ========================================

    food = models.IntegerField(
        verbose_name="食費",
        default=0
    )
    daily_goods = models.IntegerField(
        verbose_name="日用品",
        default=0
    )
    clothing = models.IntegerField(
        verbose_name="衣服美容",
        default=0
    )
    social = models.IntegerField(
        verbose_name="交際費",
        default=0
    )
    transport = models.IntegerField(
        verbose_name="交通費",
        default=0
    )
    medical = models.IntegerField(
        verbose_name="医療費",
        default=0
    )
    education = models.IntegerField(
        verbose_name="教養・教育",
        default=0
    )
    entertainment = models.IntegerField(
        verbose_name="趣味娯楽",
        default=0
    )
    other_variable = models.IntegerField(
        verbose_name="その他変動費",
        default=0
    )
    total_variable_expense = models.IntegerField(
        verbose_name="変動費合計",
        default=0
    )

    # ========================================
    # 合計
    # ========================================

    total_expense = models.IntegerField(
        verbose_name="支出総額",
        default=0,
        help_text="固定費 + クレカ + 変動費"
    )
    net_cashflow = models.IntegerField(
        verbose_name="純キャッシュフロー",
        default=0,
        help_text="収入 - 支出"
    )

    # ========================================
    # リスク判定
    # ========================================

    RISK_CHOICES = [
        ('safe', '安全'),
        ('warning', '注意'),
        ('danger', '危険'),
    ]
    risk_level = models.CharField(
        max_length=10,
        choices=RISK_CHOICES,
        default='safe',
        verbose_name="リスクレベル"
    )
    risk_message = models.TextField(
        blank=True,
        verbose_name="リスクメッセージ"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "月次キャッシュフロー"
        verbose_name_plural = "月次キャッシュフロー一覧"
        ordering = ['-year_month']

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} - 純CF:{self.net_cashflow:,}円 [{self.get_risk_level_display()}]"

    def calculate_all(self):
        """
        すべての項目を集計・計算
        """
        # SalaryRecordから給与取得
        from salary.models import SalaryRecord
        try:
            salary = SalaryRecord.objects.get(year_month=self.year_month)
            self.salary_net = salary.actual_payment
        except SalaryRecord.DoesNotExist:
            self.salary_net = 0

        # 副収入の集計
        side_incomes = Income.objects.filter(
            year_month=self.year_month,
            category='side_business'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.side_income = side_incomes

        rent_incomes = Income.objects.filter(
            year_month=self.year_month,
            category='rent_income'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.rent_income = rent_incomes

        temp_incomes = Income.objects.filter(
            year_month=self.year_month,
            category='temporary'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.temporary_income = temp_incomes

        refunds = Income.objects.filter(
            year_month=self.year_month,
            category='refund'
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        self.refund = refunds

        # 収入合計
        self.total_income = (
            self.salary_net +
            self.bonus +
            self.side_income +
            self.rent_income +
            self.temporary_income +
            self.refund +
            self.other_income
        )

        # 固定費の集計
        fixed_expenses = FixedExpense.objects.filter(is_active=True)

        housing_loans = fixed_expenses.filter(
            category='loan',
            name__icontains='住宅'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.housing_loan = housing_loans

        other_loans = fixed_expenses.filter(
            category='loan'
        ).exclude(name__icontains='住宅').aggregate(
            models.Sum('monthly_amount')
        )['monthly_amount__sum'] or 0
        self.other_loans = other_loans

        insurance_total = fixed_expenses.filter(
            category='insurance'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.insurance = insurance_total

        subscription_total = fixed_expenses.filter(
            category='subscription'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.subscription = subscription_total

        utilities_total = fixed_expenses.filter(
            category='utility'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.utilities = utilities_total

        communication_total = fixed_expenses.filter(
            category='communication'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.communication = communication_total

        rent_total = fixed_expenses.filter(
            category='rent'
        ).aggregate(models.Sum('monthly_amount'))['monthly_amount__sum'] or 0
        self.rent = rent_total

        self.total_fixed_expense = (
            self.housing_loan +
            self.other_loans +
            self.insurance +
            self.subscription +
            self.utilities +
            self.communication +
            self.rent
        )

        # クレジットカードの集計
        from credit.models import PaymentSchedule
        try:
            payment_schedule = PaymentSchedule.objects.get(year_month=self.year_month)
            self.credit_card_payments = payment_schedule.credit_card_payments
            self.total_credit_payment = payment_schedule.total_credit_payment
        except PaymentSchedule.DoesNotExist:
            self.credit_card_payments = {}
            self.total_credit_payment = 0

        # 変動費の集計
        variable_expenses = VariableExpense.objects.filter(year_month=self.year_month)

        self.food = variable_expenses.filter(category='food').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.daily_goods = variable_expenses.filter(category='daily_goods').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.clothing = variable_expenses.filter(category='clothing').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.social = variable_expenses.filter(category='social').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.transport = variable_expenses.filter(category='transport').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.medical = variable_expenses.filter(category='medical').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.education = variable_expenses.filter(category='education').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.entertainment = variable_expenses.filter(category='entertainment').aggregate(
            models.Sum('amount'))['amount__sum'] or 0
        self.other_variable = variable_expenses.filter(category='other').aggregate(
            models.Sum('amount'))['amount__sum'] or 0

        self.total_variable_expense = (
            self.food +
            self.daily_goods +
            self.clothing +
            self.social +
            self.transport +
            self.medical +
            self.education +
            self.entertainment +
            self.other_variable
        )

        # 支出合計
        self.total_expense = (
            self.total_fixed_expense +
            self.total_credit_payment +
            self.total_variable_expense
        )

        # 純キャッシュフロー
        self.net_cashflow = self.total_income - self.total_expense

        # 月変動値
        self.monthly_change = self.closing_balance - self.opening_balance

        # リスク判定
        self.risk_level = self._calculate_risk_level()

    def _calculate_risk_level(self):
        """リスクレベルを判定"""
        # 純キャッシュフローがマイナス
        if self.net_cashflow < 0:
            self.risk_message = "赤字です。支出を見直してください。"
            return 'danger'

        # 期末残高が10万円未満
        if self.closing_balance < 100000:
            self.risk_message = "残高が少なくなっています。"
            return 'warning'

        # 収入に対する支出比率が80%以上
        if self.total_income > 0:
            expense_ratio = (self.total_expense / self.total_income) * 100
            if expense_ratio >= 80:
                self.risk_message = f"支出比率が高いです（{expense_ratio:.1f}%）"
                return 'warning'

        self.risk_message = "健全な状態です。"
        return 'safe'

    def save(self, *args, **kwargs):
        """保存時に自動計算"""
        self.calculate_all()
        super().save(*args, **kwargs)

    @classmethod
    def update_or_create_for_month(cls, year_month):
        """
        指定月のキャッシュフローを作成/更新
        """
        cashflow, created = cls.objects.update_or_create(
            year_month=year_month,
            defaults={}
        )
        cashflow.calculate_all()
        cashflow.save()
        return cashflow
