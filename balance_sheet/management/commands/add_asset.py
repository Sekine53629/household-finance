from django.core.management.base import BaseCommand
from balance_sheet.models import Asset
from rich.console import Console

console = Console()


class Command(BaseCommand):
    help = '資産を追加する'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='資産名')
        parser.add_argument(
            '--category',
            type=str,
            required=True,
            choices=['cash', 'bank', 'investment', 'real_estate', 'vehicle', 'other'],
            help='カテゴリ'
        )
        parser.add_argument('--value', type=int, required=True, help='現在価値')
        parser.add_argument('--institution', type=str, default='', help='金融機関・管理会社')

    def handle(self, *args, **options):
        asset = Asset.objects.create(
            name=options['name'],
            category=options['category'],
            current_value=options['value'],
            institution=options['institution']
        )

        console.print(f"[green]✓ 資産を追加しました。[/green]")
        console.print(f"  資産名: {asset.name}")
        console.print(f"  カテゴリ: {asset.get_category_display()}")
        console.print(f"  現在価値: {asset.current_value:,}円")
        if asset.institution:
            console.print(f"  金融機関: {asset.institution}")
