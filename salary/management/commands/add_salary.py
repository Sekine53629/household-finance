from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from salary.models import SalaryRecord
from rich.console import Console
from rich.table import Table

console = Console()


class Command(BaseCommand):
    help = '給与明細を追加・更新する'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            required=True,
            help='年月（YYYY-MM形式）'
        )
        parser.add_argument('--base-salary', type=int, default=0, help='基本給')
        parser.add_argument('--position-allowance', type=int, default=0, help='役職手当')
        parser.add_argument('--overtime-pay', type=int, default=0, help='時間外手当')
        parser.add_argument('--health-insurance', type=int, default=0, help='健康保険')
        parser.add_argument('--pension-insurance', type=int, default=0, help='厚生年金')
        parser.add_argument('--resident-tax', type=int, default=0, help='住民税')

    def handle(self, *args, **options):
        month_str = options['month']

        # YYYY-MM形式からYYYY-MM-01に変換
        year_month = parse_date(f"{month_str}-01")

        if not year_month:
            console.print(f"[red]エラー: 無効な日付形式です。YYYY-MM形式で入力してください。[/red]")
            return

        # 既存レコードを取得または新規作成
        salary, created = SalaryRecord.objects.get_or_create(
            year_month=year_month,
            defaults={
                'base_salary': options['base_salary'],
                'position_allowance': options['position_allowance'],
                'overtime_pay': options['overtime_pay'],
                'health_insurance': options['health_insurance'],
                'pension_insurance': options['pension_insurance'],
                'resident_tax': options['resident_tax'],
            }
        )

        if not created:
            # 更新
            salary.base_salary = options['base_salary']
            salary.position_allowance = options['position_allowance']
            salary.overtime_pay = options['overtime_pay']
            salary.health_insurance = options['health_insurance']
            salary.pension_insurance = options['pension_insurance']
            salary.resident_tax = options['resident_tax']
            salary.save()

        # 結果を表示
        table = Table(title=f"{month_str} 給与明細")
        table.add_column("項目", style="cyan")
        table.add_column("金額", justify="right", style="green")

        table.add_row("基本給", f"{salary.base_salary:,}円")
        table.add_row("役職手当", f"{salary.position_allowance:,}円")
        table.add_row("時間外手当", f"{salary.overtime_pay:,}円")
        table.add_row("支給総額", f"{salary.total_payment:,}円", style="bold green")
        table.add_row("", "")
        table.add_row("健康保険", f"-{salary.health_insurance:,}円")
        table.add_row("厚生年金", f"-{salary.pension_insurance:,}円")
        table.add_row("住民税", f"-{salary.resident_tax:,}円")
        table.add_row("控除合計", f"-{salary.total_deduction:,}円", style="bold red")
        table.add_row("", "")
        table.add_row("手取り額", f"{salary.actual_payment:,}円", style="bold blue")

        console.print(table)

        if created:
            console.print(f"[green]✓ {month_str}の給与明細を追加しました。[/green]")
        else:
            console.print(f"[yellow]✓ {month_str}の給与明細を更新しました。[/yellow]")
