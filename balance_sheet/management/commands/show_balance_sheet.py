from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from balance_sheet.models import MonthlyBalanceSheet
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


class Command(BaseCommand):
    help = '月次バランスシートを表示する'

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
            help='バランスシートを更新してから表示'
        )

    def handle(self, *args, **options):
        month_str = options['month']
        year_month = parse_date(f"{month_str}-01")

        if not year_month:
            console.print(f"[red]エラー: 無効な日付形式です。[/red]")
            return

        # 更新オプション
        if options['update']:
            bs = MonthlyBalanceSheet.update_or_create_for_month(year_month)
            console.print(f"[green]✓ {month_str}のバランスシートを更新しました。[/green]\n")
        else:
            try:
                bs = MonthlyBalanceSheet.objects.get(year_month=year_month)
            except MonthlyBalanceSheet.DoesNotExist:
                console.print(f"[yellow]{month_str}のバランスシートが見つかりません。[/yellow]")
                console.print("[yellow]--update オプションでバランスシートを作成できます。[/yellow]")
                return

        # 資産セクション
        asset_table = Table(title="資産", show_header=False)
        asset_table.add_column("項目", style="cyan")
        asset_table.add_column("金額", justify="right", style="green")

        # 流動資産
        asset_table.add_row("[bold]流動資産[/bold]", f"{bs.current_assets:,}円")
        if bs.cash:
            asset_table.add_row("  現金", f"{bs.cash:,}円")
        if bs.bank_deposits:
            asset_table.add_row("  預金", f"{bs.bank_deposits:,}円")

        # 投資資産
        if bs.investment_assets:
            asset_table.add_row("[bold]投資資産[/bold]", f"{bs.investment_assets:,}円")
            if bs.stocks:
                asset_table.add_row("  株式", f"{bs.stocks:,}円")
            if bs.investment_trusts:
                asset_table.add_row("  投資信託", f"{bs.investment_trusts:,}円")
            if bs.crypto:
                asset_table.add_row("  暗号資産", f"{bs.crypto:,}円")

        # 固定資産
        if bs.fixed_assets:
            asset_table.add_row("[bold]固定資産[/bold]", f"{bs.fixed_assets:,}円")
            if bs.real_estate:
                asset_table.add_row("  不動産", f"{bs.real_estate:,}円")
            if bs.vehicles:
                asset_table.add_row("  車両", f"{bs.vehicles:,}円")

        asset_table.add_row("", "")
        asset_table.add_row("[bold]資産合計[/bold]", f"{bs.total_assets:,}円", style="bold green")

        console.print(asset_table)
        console.print()

        # 負債セクション
        liability_table = Table(title="負債", show_header=False)
        liability_table.add_column("項目", style="cyan")
        liability_table.add_column("金額", justify="right", style="red")

        # 短期負債
        if bs.current_liabilities:
            liability_table.add_row("[bold]短期負債[/bold]", f"{bs.current_liabilities:,}円")
            if bs.credit_card_debt:
                liability_table.add_row("  クレジットカード", f"{bs.credit_card_debt:,}円")
            if bs.short_term_loans:
                liability_table.add_row("  短期ローン", f"{bs.short_term_loans:,}円")

        # 長期負債
        if bs.long_term_liabilities:
            liability_table.add_row("[bold]長期負債[/bold]", f"{bs.long_term_liabilities:,}円")
            if bs.housing_loan:
                liability_table.add_row("  住宅ローン", f"{bs.housing_loan:,}円")
            if bs.car_loan:
                liability_table.add_row("  自動車ローン", f"{bs.car_loan:,}円")
            if bs.student_loan:
                liability_table.add_row("  奨学金", f"{bs.student_loan:,}円")

        liability_table.add_row("", "")
        liability_table.add_row("[bold]負債合計[/bold]", f"{bs.total_liabilities:,}円", style="bold red")

        console.print(liability_table)
        console.print()

        # 純資産
        net_worth_color = "green" if bs.net_worth >= 0 else "red"
        console.print(Panel(
            f"[bold {net_worth_color}]{bs.net_worth:,}円[/bold {net_worth_color}]",
            title="純資産",
            border_style=net_worth_color
        ))

        # 前月比
        if bs.net_worth_change != 0:
            change_color = "green" if bs.net_worth_change > 0 else "red"
            arrow = "↑" if bs.net_worth_change > 0 else "↓"
            console.print(f"前月比: [{change_color}]{bs.net_worth_change:+,}円 {arrow}[/{change_color}]")

        # 財務指標
        console.print(f"\n負債比率: {bs.debt_ratio:.1f}%")
        if bs.current_liabilities > 0:
            console.print(f"流動比率: {bs.liquidity_ratio:.1f}%")

        # 健全性評価
        health_color = {
            'excellent': 'green',
            'good': 'green',
            'fair': 'yellow',
            'warning': 'yellow',
            'danger': 'red'
        }.get(bs.financial_health, 'white')

        console.print(f"\n財務健全性: [{health_color}]{bs.get_financial_health_display()}[/{health_color}]")
        if bs.health_message:
            console.print(f"[{health_color}]{bs.health_message}[/{health_color}]")
