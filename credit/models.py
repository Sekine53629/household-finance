from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from dateutil.relativedelta import relativedelta


class CreditCard(models.Model):
    """
    クレジットカード マスタ
    """
    name = models.CharField(
        max_length=100,
        verbose_name="カード名",
        help_text="例: 楽天カード、三井住友カード"
    )
    card_number_last4 = models.CharField(
        max_length=4,
        verbose_name="カード番号下4桁",
        blank=True,
        help_text="識別用"
    )

    # 締め日・引落日
    closing_date = models.IntegerField(
        verbose_name="締め日",
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="月の何日締めか（例：15日締めなら15）"
    )
    payment_date = models.IntegerField(
        verbose_name="引落日",
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="月の何日引落か（例：10日引落なら10）"
    )

    # 引落口座
    bank_account = models.CharField(
        max_length=100,
        verbose_name="引落口座",
        blank=True,
        help_text="例: みずほ銀行 普通預金"
    )

    # 限度額（任意）
    credit_limit = models.IntegerField(
        verbose_name="利用限度額",
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
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
        verbose_name = "クレジットカード"
        verbose_name_plural = "クレジットカード一覧"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (締日:{self.closing_date}日 引落:{self.payment_date}日)"

    def get_current_month_usage(self, year_month=None):
        """当月の利用総額を取得"""
        if year_month is None:
            year_month = date.today().replace(day=1)

        total = self.creditusage_set.filter(
            usage_date__year=year_month.year,
            usage_date__month=year_month.month
        ).aggregate(models.Sum('amount'))['amount__sum']

        return total or 0

    def get_next_payment_amount(self):
        """次回引落予定額を取得"""
        today = date.today()

        # 締め日を過ぎているかチェック
        if today.day > self.closing_date:
            # 次月の引落対象期間
            start_date = date(today.year, today.month, self.closing_date + 1)
            next_month = today + relativedelta(months=1)
            end_date = date(next_month.year, next_month.month, self.closing_date)
        else:
            # 当月の引落対象期間
            prev_month = today - relativedelta(months=1)
            start_date = date(prev_month.year, prev_month.month, self.closing_date + 1)
            end_date = date(today.year, today.month, self.closing_date)

        total = self.creditusage_set.filter(
            usage_date__gte=start_date,
            usage_date__lte=end_date,
            is_paid=False
        ).aggregate(models.Sum('amount'))['amount__sum']

        return total or 0


class ShortTermLoan(models.Model):
    """
    短期ローン（携帯分割払い等）
    """
    name = models.CharField(
        max_length=100,
        verbose_name="ローン名",
        help_text="例: iPhone 15 分割、ドコモ光工事費"
    )

    # ローン詳細
    monthly_payment = models.IntegerField(
        verbose_name="月額支払額",
        validators=[MinValueValidator(0)]
    )
    remaining_months = models.IntegerField(
        verbose_name="残回数",
        validators=[MinValueValidator(0)],
        help_text="残り何ヶ月か"
    )
    payment_date = models.IntegerField(
        verbose_name="引落日",
        validators=[MinValueValidator(1), MaxValueValidator(31)],
        help_text="月の何日引落か"
    )

    # 開始日
    start_date = models.DateField(
        verbose_name="開始日",
        help_text="ローン開始日"
    )

    # 引落口座
    bank_account = models.CharField(
        max_length=100,
        verbose_name="引落口座",
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
        verbose_name = "短期ローン"
        verbose_name_plural = "短期ローン一覧"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} - 月額{self.monthly_payment:,}円 × 残{self.remaining_months}回"

    def total_remaining(self):
        """残債総額"""
        return self.monthly_payment * self.remaining_months

    def completion_date(self):
        """完済予定日"""
        return self.start_date + relativedelta(months=self.remaining_months)

    def update_remaining_months(self):
        """残回数を自動更新（月次バッチ用）"""
        if self.remaining_months > 0:
            self.remaining_months -= 1
            if self.remaining_months == 0:
                self.is_active = False
            self.save()


class CreditUsage(models.Model):
    """
    クレジットカード利用明細
    """
    credit_card = models.ForeignKey(
        CreditCard,
        on_delete=models.CASCADE,
        verbose_name="クレジットカード"
    )

    # 利用情報
    usage_date = models.DateField(
        verbose_name="利用日"
    )
    amount = models.IntegerField(
        verbose_name="利用金額",
        validators=[MinValueValidator(0)]
    )
    merchant = models.CharField(
        max_length=200,
        verbose_name="利用店舗",
        blank=True
    )

    # カテゴリ
    CATEGORY_CHOICES = [
        ('food', '食費'),
        ('transport', '交通費'),
        ('utility', '光熱費'),
        ('communication', '通信費'),
        ('shopping', '買い物'),
        ('entertainment', '娯楽'),
        ('medical', '医療'),
        ('other', 'その他'),
    ]
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="カテゴリ"
    )

    # 引落情報
    payment_date = models.DateField(
        verbose_name="引落予定日",
        null=True,
        blank=True,
        help_text="自動計算される"
    )
    is_paid = models.BooleanField(
        default=False,
        verbose_name="支払済み"
    )

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "クレジットカード利用明細"
        verbose_name_plural = "クレジットカード利用明細一覧"
        ordering = ['-usage_date']

    def __str__(self):
        return f"{self.usage_date} {self.credit_card.name} {self.amount:,}円 {self.merchant}"

    def calculate_payment_date(self):
        """引落予定日を計算"""
        # 締め日を過ぎているかチェック
        if self.usage_date.day > self.credit_card.closing_date:
            # 翌々月の引落
            payment_month = self.usage_date + relativedelta(months=2)
        else:
            # 翌月の引落
            payment_month = self.usage_date + relativedelta(months=1)

        # 引落日を設定
        payment_day = self.credit_card.payment_date

        # 月末日を超える場合は月末に調整
        from calendar import monthrange
        max_day = monthrange(payment_month.year, payment_month.month)[1]
        if payment_day > max_day:
            payment_day = max_day

        return date(payment_month.year, payment_month.month, payment_day)

    def save(self, *args, **kwargs):
        """保存時に引落予定日を自動計算"""
        if not self.payment_date:
            self.payment_date = self.calculate_payment_date()
        super().save(*args, **kwargs)


class PaymentSchedule(models.Model):
    """
    月次支払いスケジュール（統合ビュー）
    クレカ＋ローンの引落予定を一元管理
    """
    year_month = models.DateField(
        verbose_name="年月",
        unique=True,
        help_text="支払い月（YYYY-MM-01形式）"
    )

    # クレジットカード引落予定
    credit_card_payments = models.JSONField(
        verbose_name="クレカ引落予定",
        default=dict,
        help_text="{'カード名': 金額} の辞書"
    )
    total_credit_payment = models.IntegerField(
        verbose_name="クレカ合計",
        default=0
    )

    # ローン支払い予定
    loan_payments = models.JSONField(
        verbose_name="ローン支払予定",
        default=dict,
        help_text="{'ローン名': 金額} の辞書"
    )
    total_loan_payment = models.IntegerField(
        verbose_name="ローン合計",
        default=0
    )

    # 合計
    total_payment = models.IntegerField(
        verbose_name="支払総額",
        default=0,
        help_text="クレカ + ローンの合計"
    )

    # リスク判定
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

    # メタデータ
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    memo = models.TextField(blank=True, verbose_name="メモ")

    class Meta:
        verbose_name = "支払いスケジュール"
        verbose_name_plural = "支払いスケジュール一覧"
        ordering = ['-year_month']

    def __str__(self):
        return f"{self.year_month.strftime('%Y年%m月')} - 合計{self.total_payment:,}円 [{self.get_risk_level_display()}]"

    def calculate_all(self):
        """
        クレカ・ローンの引落予定を集計
        """
        # クレジットカード集計
        credit_payments = {}
        for card in CreditCard.objects.filter(is_active=True):
            # 該当月に引落がある利用明細を取得
            amount = CreditUsage.objects.filter(
                credit_card=card,
                payment_date__year=self.year_month.year,
                payment_date__month=self.year_month.month,
                is_paid=False
            ).aggregate(models.Sum('amount'))['amount__sum'] or 0

            if amount > 0:
                credit_payments[card.name] = amount

        self.credit_card_payments = credit_payments
        self.total_credit_payment = sum(credit_payments.values())

        # ローン集計
        loan_payments = {}
        for loan in ShortTermLoan.objects.filter(is_active=True):
            # 該当月に支払いがあるか判定
            # （簡易版：毎月支払いがある前提）
            loan_payments[loan.name] = loan.monthly_payment

        self.loan_payments = loan_payments
        self.total_loan_payment = sum(loan_payments.values())

        # 合計
        self.total_payment = self.total_credit_payment + self.total_loan_payment

        # リスクレベルの判定（簡易版）
        # ※実際はSalaryRecordと照らし合わせて判定
        self.risk_level = self._calculate_risk_level()

    def _calculate_risk_level(self):
        """リスクレベルを判定"""
        # 簡易版：金額ベースで判定
        # TODO: 給与データと照らし合わせて判定
        if self.total_payment < 100000:
            return 'safe'
        elif self.total_payment < 200000:
            return 'warning'
        else:
            return 'danger'

    def save(self, *args, **kwargs):
        """保存時に自動計算"""
        self.calculate_all()
        super().save(*args, **kwargs)

    @classmethod
    def update_or_create_for_month(cls, year_month):
        """
        指定月のスケジュールを作成/更新
        """
        schedule, created = cls.objects.update_or_create(
            year_month=year_month,
            defaults={}
        )
        schedule.calculate_all()
        schedule.save()
        return schedule
