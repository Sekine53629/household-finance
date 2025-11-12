from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from salary.models import SalaryRecord
from rich.console import Console
from rich.table import Table

console = Console()


class Command(BaseCommand):
    help = '給与明細を表示する'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='年月（YYYY-MM形式）。指定しない場合は直近3ヶ月分を表示'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=3,
            help='表示件数（デフォルト: 3）'
        )

    def handle(self, *args, **options):
        month_str = options.get('month')

        if month_str:
            # 特定月の詳細表示
            year_month = parse_date(f"{month_str}-01")
            if not year_month:
                console.print(f"[red]エラー: 無効な日付形式です。[/red]")
                return

            try:
                salary = SalaryRecord.objects.get(year_month=year_month)
                self.show_detail(salary)
            except SalaryRecord.DoesNotExist:
                console.print(f"[red]{month_str}の給与明細が見つかりません。[/red]")
        else:
            # 一覧表示
            limit = options['limit']
            salaries = SalaryRecord.objects.all()[:limit]

            if not salaries:
                console.print("[yellow]給与明細が登録されていません。[/yellow]")
                return

            table = Table(title="給与明細一覧")
            table.add_column("年月", style="cyan")
            table.add_column("基本給", justify="right")
            table.add_column("支給総額", justify="right")
            table.add_column("控除総額", justify="right")
            table.add_column("手取り額", justify="right", style="green bold")

            for salary in salaries:
                table.add_row(
                    salary.year_month.strftime('%Y年%m月'),
                    f"{salary.base_salary:,}円",
                    f"{salary.total_payment:,}円",
                    f"{salary.total_deduction:,}円",
                    f"{salary.actual_payment:,}円"
                )

            console.print(table)

    def show_detail(self, salary):
        """給与明細の詳細表示"""
        table = Table(title=f"{salary.year_month.strftime('%Y年%m月')} 給与明細詳細")
        table.add_column("項目", style="cyan")
        table.add_column("金額", justify="right", style="green")

        # 支給項目
        table.add_row("[bold]【支給】[/bold]", "", style="bold cyan")
        table.add_row("基本給", f"{salary.base_salary:,}円")
        if salary.position_allowance:
            table.add_row("役職手当", f"{salary.position_allowance:,}円")
        if salary.overtime_pay:
            table.add_row("時間外手当", f"{salary.overtime_pay:,}円")
        if salary.housing_allowance:
            table.add_row("住宅手当", f"{salary.housing_allowance:,}円")
        if salary.family_allowance:
            table.add_row("家族手当", f"{salary.family_allowance:,}円")
        table.add_row("支給総額", f"{salary.total_payment:,}円", style="bold green")

        table.add_row("", "")

        # 控除項目
        table.add_row("[bold]【控除】[/bold]", "", style="bold red")
        if salary.health_insurance:
            table.add_row("健康保険", f"-{salary.health_insurance:,}円")
        if salary.pension_insurance:
            table.add_row("厚生年金", f"-{salary.pension_insurance:,}円")
        if salary.employment_insurance:
            table.add_row("雇用保険", f"-{salary.employment_insurance:,}円")
        if salary.monthly_income_tax:
            table.add_row("所得税", f"-{salary.monthly_income_tax:,}円")
        if salary.resident_tax:
            table.add_row("住民税", f"-{salary.resident_tax:,}円")
        table.add_row("控除合計", f"-{salary.total_deduction:,}円", style="bold red")

        table.add_row("", "")
        table.add_row("[bold]手取り額[/bold]", f"{salary.actual_payment:,}円", style="bold blue")

        console.print(table)

        # 前月比
        prev = salary.get_previous_month()
        if prev:
            diff = salary.actual_payment - prev.actual_payment
            if diff > 0:
                console.print(f"\n前月比: [green]+{diff:,}円 ↑[/green]")
            elif diff < 0:
                console.print(f"\n前月比: [red]{diff:,}円 ↓[/red]")
            else:
                console.print(f"\n前月比: 変動なし")
