from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from credit.models import PaymentSchedule
from rich.console import Console
from rich.table import Table

console = Console()


class Command(BaseCommand):
    help = '月次支払いスケジュールを表示する'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            required=True,
            help='年月（YYYY-MM形式）'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='スケジュールを更新してから表示'
        )

    def handle(self, *args, **options):
        month_str = options['month']
        year_month = parse_date(f"{month_str}-01")

        if not year_month:
            console.print(f"[red]エラー: 無効な日付形式です。[/red]")
            return

        # 更新オプション
        if options['update']:
            schedule = PaymentSchedule.update_or_create_for_month(year_month)
            console.print(f"[green]✓ {month_str}のスケジュールを更新しました。[/green]\n")
        else:
            try:
                schedule = PaymentSchedule.objects.get(year_month=year_month)
            except PaymentSchedule.DoesNotExist:
                console.print(f"[yellow]{month_str}のスケジュールが見つかりません。[/yellow]")
                console.print("[yellow]--update オプションでスケジュールを作成できます。[/yellow]")
                return

        # クレジットカード引落
        if schedule.credit_card_payments:
            table = Table(title=f"{month_str} クレジットカード引落予定")
            table.add_column("カード名", style="cyan")
            table.add_column("金額", justify="right", style="yellow")

            for card_name, amount in schedule.credit_card_payments.items():
                table.add_row(card_name, f"{amount:,}円")

            table.add_row("", "")
            table.add_row("[bold]合計[/bold]", f"{schedule.total_credit_payment:,}円", style="bold yellow")
            console.print(table)
        else:
            console.print(f"[yellow]{month_str}はクレジットカード引落がありません。[/yellow]")

        console.print()

        # ローン支払い
        if schedule.loan_payments:
            table = Table(title=f"{month_str} ローン支払予定")
            table.add_column("ローン名", style="cyan")
            table.add_column("金額", justify="right", style="red")

            for loan_name, amount in schedule.loan_payments.items():
                table.add_row(loan_name, f"{amount:,}円")

            table.add_row("", "")
            table.add_row("[bold]合計[/bold]", f"{schedule.total_loan_payment:,}円", style="bold red")
            console.print(table)
        else:
            console.print(f"[yellow]{month_str}はローン支払いがありません。[/yellow]")

        console.print()

        # 支払総額とリスクレベル
        console.print(f"[bold]支払総額: {schedule.total_payment:,}円[/bold]")

        risk_color = {
            'safe': 'green',
            'warning': 'yellow',
            'danger': 'red'
        }.get(schedule.risk_level, 'white')

        console.print(f"リスクレベル: [{risk_color}]{schedule.get_risk_level_display()}[/{risk_color}]")
