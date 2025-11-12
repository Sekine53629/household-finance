from django.db import models
from django.core.validators import MinValueValidator
from datetime import date


class Asset(models.Model):
    """
    資産マスタ
    現金、預金、投資、不動産などの資産を管理
    """
    CATEGORY_CHOICES = [
        ('cash', '現金'),
        ('bank', '預金'),
        ('investment', '投資'),
        ('real_estate', '不動産'),
        ('vehicle', '車両'),
        ('other', 'その他資産'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="資産名",
        help_text="例: みずほ銀行普通預金、楽天証券、自宅マンション"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="カテゴリ"
    )
    current_value = models.IntegerField(
        verbose_name="現在価値",
        validators=[MinValueValidator(0)],
        help_text="最新の評価額"
    )

    # 取得情報
    acquisition_date = models.DateField(
        verbose_name="取得日",
        null=True,
        blank=True
    )
    acquisition_cost = models.IntegerField(
        verbose_name="取得原価",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # ステータス
    is_active = models.BooleanField(
        default=True,
        verbose_name="有効"
    )

    # 追加情報
    account_number = models.CharField(
        max_length=100,
        verbose_name="口座番号・識別番号",
        blank=True
    )
    institution = models.CharField(
        max_length=100,
        verbose_name="金融機関・管理会社",
        blank=True,
        help_text="例: みずほ銀行、楽天証券"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "資産"
        verbose_name_plural = "資産一覧"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.current_value:,}円 [{self.get_category_display()}]"

    def unrealized_gain(self):
        """含み損益"""
        if self.acquisition_cost:
            return self.current_value - self.acquisition_cost
        return 0

    def unrealized_gain_ratio(self):
        """含み損益率（%）"""
        if self.acquisition_cost and self.acquisition_cost > 0:
            return ((self.current_value - self.acquisition_cost) / self.acquisition_cost) * 100
        return 0


class Liability(models.Model):
    """
    負債マスタ
    住宅ローン、カードローン、借入金などの負債を管理
    """
    CATEGORY_CHOICES = [
        ('housing_loan', '住宅ローン'),
        ('car_loan', '自動車ローン'),
        ('card_loan', 'カードローン'),
        ('student_loan', '奨学金'),
        ('personal_loan', '個人借入'),
        ('other', 'その他負債'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name="負債名",
        help_text="例: フラット35住宅ローン、三井住友カードローン"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="カテゴリ"
    )
    current_balance = models.IntegerField(
        verbose_name="現在残高",
        validators=[MinValueValidator(0)],
        help_text="最新の残債額"
    )

    # ローン詳細
    original_amount = models.IntegerField(
        verbose_name="借入総額",
        validators=[MinValueValidator(0)]
    )
    interest_rate = models.DecimalField(
        verbose_name="金利（%）",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="年利"
    )
    monthly_payment = models.IntegerField(
        verbose_name="月額返済額",
        validators=[MinValueValidator(0)]
    )
    remaining_months = models.IntegerField(
        verbose_name="残回数",
        validators=[MinValueValidator(0)],
        help_text="残り何ヶ月か"
    )

    # 日付情報
    start_date = models.DateField(
        verbose_name="借入開始日"
    )
    maturity_date = models.DateField(
        verbose_name="完済予定日",
        null=True,
        blank=True
    )
    payment_date = models.IntegerField(
        verbose_name="返済日",
        validators=[MinValueValidator(1)],
        help_text="月の何日に返済するか"
    )

    # 金融機関情報
    lender = models.CharField(
        max_length=100,
        verbose_name="貸主・金融機関",
        help_text="例: みずほ銀行、住宅金融支援機構"
    )
    account_number = models.CharField(
        max_length=100,
        verbose_name="口座番号・契約番号",
        blank=True
    )

    # ステータス
    is_active = models.BooleanField(
        default=True,
        verbose_name="有効"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "負債"
        verbose_name_plural = "負債一覧"
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - 残債{self.current_balance:,}円 [{self.get_category_display()}]"

    def total_interest(self):
        """総利息額（概算）"""
        total_payment = self.monthly_payment * self.remaining_months
        return total_payment - self.current_balance

    def repayment_ratio(self):
        """返済進捗率（%）"""
        if self.original_amount > 0:
            return ((self.original_amount - self.current_balance) / self.original_amount) * 100
        return 0


class MonthlyBalanceSheet(models.Model):
    """
    月次バランスシート
    毎月の資産・負債・純資産のスナップショット
    """
    year_month = models.DateField(
        verbose_name="年月",
        unique=True,
        help_text="対象月（YYYY-MM-01形式）"
    )

    # ========================================
    # 資産
    # ========================================

    # 流動資産
    cash = models.IntegerField(
        verbose_name="現金",
        default=0,
        validators=[MinValueValidator(0)]
    )
    bank_deposits = models.IntegerField(
        verbose_name="預金",
        default=0,
        validators=[MinValueValidator(0)]
    )
    current_assets = models.IntegerField(
        verbose_name="流動資産合計",
        default=0
    )

    # 投資資産
    stocks = models.IntegerField(
        verbose_name="株式",
        default=0,
        validators=[MinValueValidator(0)]
    )
    bonds = models.IntegerField(
        verbose_name="債券",
        default=0,
        validators=[MinValueValidator(0)]
    )
    investment_trusts = models.IntegerField(
        verbose_name="投資信託",
        default=0,
        validators=[MinValueValidator(0)]
    )
    crypto = models.IntegerField(
        verbose_name="暗号資産",
        default=0,
        validators=[MinValueValidator(0)]
    )
    investment_assets = models.IntegerField(
        verbose_name="投資資産合計",
        default=0
    )

    # 固定資産
    real_estate = models.IntegerField(
        verbose_name="不動産",
        default=0,
        validators=[MinValueValidator(0)]
    )
    vehicles = models.IntegerField(
        verbose_name="車両",
        default=0,
        validators=[MinValueValidator(0)]
    )
    other_assets = models.IntegerField(
        verbose_name="その他資産",
        default=0,
        validators=[MinValueValidator(0)]
    )
    fixed_assets = models.IntegerField(
        verbose_name="固定資産合計",
        default=0
    )

    # 資産合計
    total_assets = models.IntegerField(
        verbose_name="資産合計",
        default=0
    )

    # ========================================
    # 負債
    # ========================================

    # 短期負債
    credit_card_debt = models.IntegerField(
        verbose_name="クレジットカード債務",
        default=0,
        validators=[MinValueValidator(0)]
    )
    short_term_loans = models.IntegerField(
        verbose_name="短期ローン",
        default=0,
        validators=[MinValueValidator(0)]
    )
    current_liabilities = models.IntegerField(
        verbose_name="短期負債合計",
        default=0
    )

    # 長期負債
    housing_loan = models.IntegerField(
        verbose_name="住宅ローン",
        default=0,
        validators=[MinValueValidator(0)]
    )
    car_loan = models.IntegerField(
        verbose_name="自動車ローン",
        default=0,
        validators=[MinValueValidator(0)]
    )
    student_loan = models.IntegerField(
        verbose_name="奨学金",
        default=0,
        validators=[MinValueValidator(0)]
    )
    other_loans = models.IntegerField(
        verbose_name="その他ローン",
        default=0,
        validators=[MinValueValidator(0)]
    )
    long_term_liabilities = models.IntegerField(
        verbose_name="長期負債合計",
        default=0
    )

    # 負債合計
    total_liabilities = models.IntegerField(
        verbose_name="負債合計",
        default=0
    )

    # ========================================
    # 純資産
    # ========================================

    net_worth = models.IntegerField(
        verbose_name="純資産",
        default=0,
        help_text="資産合計 - 負債合計"
    )

    # 前月比
    net_worth_change = models.IntegerField(
        verbose_name="純資産増減",
        default=0,
        help_text="前月との差額"
    )
    net_worth_change_ratio = models.DecimalField(
        verbose_name="純資産増減率（%）",
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="前月比の変動率"
    )

    # ========================================
    # 財務指標
    # ========================================

    debt_ratio = models.DecimalField(
        verbose_name="負債比率（%）",
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="負債 / 資産 × 100"
    )
    liquidity_ratio = models.DecimalField(
        verbose_name="流動比率（%）",
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="流動資産 / 短期負債 × 100"
    )

    # 健全性評価
    HEALTH_CHOICES = [
        ('excellent', '非常に良好'),
        ('good', '良好'),
        ('fair', '普通'),
        ('warning', '注意'),
        ('danger', '危険'),
    ]
    financial_health = models.CharField(
        max_length=10,
        choices=HEALTH_CHOICES,
        default='fair',
        verbose_name="財務健全性"
    )
    health_message = models.TextField(
        blank=True,
        verbose_name="健全性メッセージ"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "月次バランスシート"
        verbose_name_plural = "月次バランスシート一覧"
        ordering = ['-year_month']

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} - 純資産{self.net_worth:,}円 [{self.get_financial_health_display()}]"

    def calculate_all(self):
        """
        すべての項目を集計・計算
        """
        # Assetモデルから資産を集計
        assets = Asset.objects.filter(is_active=True)

        self.cash = assets.filter(category='cash').aggregate(
            models.Sum('current_value'))['current_value__sum'] or 0
        self.bank_deposits = assets.filter(category='bank').aggregate(
            models.Sum('current_value'))['current_value__sum'] or 0
        self.current_assets = self.cash + self.bank_deposits

        self.stocks = assets.filter(
            category='investment',
            name__icontains='株'
        ).aggregate(models.Sum('current_value'))['current_value__sum'] or 0
        self.investment_trusts = assets.filter(
            category='investment',
            name__icontains='投資信託'
        ).aggregate(models.Sum('current_value'))['current_value__sum'] or 0
        self.crypto = assets.filter(
            category='investment',
            name__icontains='暗号'
        ).aggregate(models.Sum('current_value'))['current_value__sum'] or 0
        self.investment_assets = self.stocks + self.bonds + self.investment_trusts + self.crypto

        self.real_estate = assets.filter(category='real_estate').aggregate(
            models.Sum('current_value'))['current_value__sum'] or 0
        self.vehicles = assets.filter(category='vehicle').aggregate(
            models.Sum('current_value'))['current_value__sum'] or 0
        self.other_assets = assets.filter(category='other').aggregate(
            models.Sum('current_value'))['current_value__sum'] or 0
        self.fixed_assets = self.real_estate + self.vehicles + self.other_assets

        self.total_assets = self.current_assets + self.investment_assets + self.fixed_assets

        # Liabilityモデルから負債を集計
        liabilities = Liability.objects.filter(is_active=True)

        # クレジットカードは短期負債
        from credit.models import PaymentSchedule
        try:
            payment_schedule = PaymentSchedule.objects.get(year_month=self.year_month)
            self.credit_card_debt = payment_schedule.total_credit_payment
        except PaymentSchedule.DoesNotExist:
            self.credit_card_debt = 0

        self.short_term_loans = liabilities.filter(
            remaining_months__lte=12
        ).exclude(category='housing_loan').aggregate(
            models.Sum('current_balance'))['current_balance__sum'] or 0
        self.current_liabilities = self.credit_card_debt + self.short_term_loans

        self.housing_loan = liabilities.filter(category='housing_loan').aggregate(
            models.Sum('current_balance'))['current_balance__sum'] or 0
        self.car_loan = liabilities.filter(category='car_loan').aggregate(
            models.Sum('current_balance'))['current_balance__sum'] or 0
        self.student_loan = liabilities.filter(category='student_loan').aggregate(
            models.Sum('current_balance'))['current_balance__sum'] or 0
        self.other_loans = liabilities.filter(category='other').aggregate(
            models.Sum('current_balance'))['current_balance__sum'] or 0
        self.long_term_liabilities = (
            self.housing_loan + self.car_loan + self.student_loan + self.other_loans
        )

        self.total_liabilities = self.current_liabilities + self.long_term_liabilities

        # 純資産
        self.net_worth = self.total_assets - self.total_liabilities

        # 前月比計算
        previous_month = self.get_previous_month()
        if previous_month:
            self.net_worth_change = self.net_worth - previous_month.net_worth
            if previous_month.net_worth != 0:
                self.net_worth_change_ratio = (
                    self.net_worth_change / previous_month.net_worth
                ) * 100
            else:
                self.net_worth_change_ratio = 0
        else:
            self.net_worth_change = 0
            self.net_worth_change_ratio = 0

        # 財務指標
        if self.total_assets > 0:
            self.debt_ratio = (self.total_liabilities / self.total_assets) * 100
        else:
            self.debt_ratio = 0

        if self.current_liabilities > 0:
            self.liquidity_ratio = (self.current_assets / self.current_liabilities) * 100
        else:
            self.liquidity_ratio = 0

        # 健全性評価
        self.financial_health = self._evaluate_health()

    def _evaluate_health(self):
        """財務健全性を評価"""
        messages = []

        # 純資産がマイナス（債務超過）
        if self.net_worth < 0:
            self.health_message = "債務超過です。早急に負債を削減してください。"
            return 'danger'

        # 負債比率が高い
        if self.debt_ratio > 50:
            messages.append(f"負債比率が高いです（{self.debt_ratio:.1f}%）")
            if self.debt_ratio > 70:
                self.health_message = "。".join(messages)
                return 'danger'
            self.health_message = "。".join(messages)
            return 'warning'

        # 流動比率が低い（短期負債に対して現金が不足）
        if self.current_liabilities > 0 and self.liquidity_ratio < 100:
            messages.append(f"流動比率が低いです（{self.liquidity_ratio:.1f}%）")
            self.health_message = "。".join(messages)
            return 'warning'

        # 純資産が増加傾向
        if self.net_worth_change > 0:
            messages.append(f"純資産が増加しています（+{self.net_worth_change:,}円）")
            self.health_message = "。".join(messages)
            return 'excellent'

        self.health_message = "健全な財務状態です。"
        return 'good'

    def get_previous_month(self):
        """前月のバランスシートを取得"""
        from dateutil.relativedelta import relativedelta
        previous_month = self.year_month - relativedelta(months=1)
        try:
            return MonthlyBalanceSheet.objects.get(year_month=previous_month)
        except MonthlyBalanceSheet.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """保存時に自動計算"""
        self.calculate_all()
        super().save(*args, **kwargs)

    @classmethod
    def update_or_create_for_month(cls, year_month):
        """
        指定月のバランスシートを作成/更新
        """
        balance_sheet, created = cls.objects.update_or_create(
            year_month=year_month,
            defaults={}
        )
        balance_sheet.calculate_all()
        balance_sheet.save()
        return balance_sheet
