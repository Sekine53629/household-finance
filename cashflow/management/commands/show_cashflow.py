from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from cashflow.models import MonthlyCashFlow
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class Command(BaseCommand):
    help = '月次キャッシュフローを表示する'

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
            help='キャッシュフローを更新してから表示'
        )

    def handle(self, *args, **options):
        month_str = options['month']
        year_month = parse_date(f"{month_str}-01")

        if not year_month:
            console.print(f"[red]エラー: 無効な日付形式です。[/red]")
            return

        # 更新オプション
        if options['update']:
            cashflow = MonthlyCashFlow.update_or_create_for_month(year_month)
            console.print(f"[green]✓ {month_str}のキャッシュフローを更新しました。[/green]\n")
        else:
            try:
                cashflow = MonthlyCashFlow.objects.get(year_month=year_month)
            except MonthlyCashFlow.DoesNotExist:
                console.print(f"[yellow]{month_str}のキャッシュフローが見つかりません。[/yellow]")
                console.print("[yellow]--update オプションでキャッシュフローを作成できます。[/yellow]")
                return

        # 収入セクション
        income_table = Table(title="収入", show_header=False)
        income_table.add_column("項目", style="cyan")
        income_table.add_column("金額", justify="right", style="green")

        if cashflow.salary_net:
            income_table.add_row("給与手取り", f"{cashflow.salary_net:,}円")
        if cashflow.bonus:
            income_table.add_row("賞与", f"{cashflow.bonus:,}円")
        if cashflow.side_income:
            income_table.add_row("事業所得", f"{cashflow.side_income:,}円")
        if cashflow.rent_income:
            income_table.add_row("家賃収入", f"{cashflow.rent_income:,}円")
        if cashflow.other_income:
            income_table.add_row("その他収入", f"{cashflow.other_income:,}円")

        income_table.add_row("", "")
        income_table.add_row("[bold]収入合計[/bold]", f"{cashflow.total_income:,}円", style="bold green")

        console.print(income_table)
        console.print()

        # 支出セクション
        expense_table = Table(title="支出", show_header=False)
        expense_table.add_column("項目", style="cyan")
        expense_table.add_column("金額", justify="right", style="red")

        # 固定費
        if cashflow.total_fixed_expense:
            expense_table.add_row("[bold]固定費[/bold]", f"{cashflow.total_fixed_expense:,}円")
            if cashflow.housing_loan:
                expense_table.add_row("  住宅ローン", f"{cashflow.housing_loan:,}円")
            if cashflow.insurance:
                expense_table.add_row("  保険料", f"{cashflow.insurance:,}円")
            if cashflow.utilities:
                expense_table.add_row("  光熱費", f"{cashflow.utilities:,}円")
            if cashflow.communication:
                expense_table.add_row("  通信費", f"{cashflow.communication:,}円")

        # クレジットカード
        if cashflow.total_credit_payment:
            expense_table.add_row("[bold]クレジットカード[/bold]", f"{cashflow.total_credit_payment:,}円")

        # 変動費
        if cashflow.total_variable_expense:
            expense_table.add_row("[bold]変動費[/bold]", f"{cashflow.total_variable_expense:,}円")
            if cashflow.food:
                expense_table.add_row("  食費", f"{cashflow.food:,}円")
            if cashflow.transport:
                expense_table.add_row("  交通費", f"{cashflow.transport:,}円")
            if cashflow.entertainment:
                expense_table.add_row("  趣味娯楽", f"{cashflow.entertainment:,}円")

        expense_table.add_row("", "")
        expense_table.add_row("[bold]支出合計[/bold]", f"{cashflow.total_expense:,}円", style="bold red")

        console.print(expense_table)
        console.print()

        # 純キャッシュフロー
        net_cf_color = "green" if cashflow.net_cashflow >= 0 else "red"
        console.print(Panel(
            f"[bold {net_cf_color}]{cashflow.net_cashflow:,}円[/bold {net_cf_color}]",
            title="純キャッシュフロー",
            border_style=net_cf_color
        ))

        # 口座残高
        if cashflow.closing_balance:
            console.print(f"\n期末残高: {cashflow.closing_balance:,}円")

        # リスク評価
        risk_color = {
            'safe': 'green',
            'warning': 'yellow',
            'danger': 'red'
        }.get(cashflow.risk_level, 'white')

        console.print(f"リスクレベル: [{risk_color}]{cashflow.get_risk_level_display()}[/{risk_color}]")
        if cashflow.risk_message:
            console.print(f"[{risk_color}]{cashflow.risk_message}[/{risk_color}]")
