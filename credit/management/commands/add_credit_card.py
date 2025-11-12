from django.core.management.base import BaseCommand
from credit.models import CreditCard
from rich.console import Console

console = Console()


class Command(BaseCommand):
    help = 'クレジットカードを追加する'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, required=True, help='カード名')
        parser.add_argument('--closing-date', type=int, required=True, help='締め日')
        parser.add_argument('--payment-date', type=int, required=True, help='引落日')
        parser.add_argument('--bank-account', type=str, default='', help='引落口座')
        parser.add_argument('--credit-limit', type=int, help='利用限度額')

    def handle(self, *args, **options):
        card = CreditCard.objects.create(
            name=options['name'],
            closing_date=options['closing_date'],
            payment_date=options['payment_date'],
            bank_account=options['bank_account'],
            credit_limit=options.get('credit_limit')
        )

        console.print(f"[green]✓ クレジットカードを追加しました。[/green]")
        console.print(f"  カード名: {card.name}")
        console.print(f"  締め日: {card.closing_date}日")
        console.print(f"  引落日: {card.payment_date}日")
        if card.bank_account:
            console.print(f"  引落口座: {card.bank_account}")
        if card.credit_limit:
            console.print(f"  利用限度額: {card.credit_limit:,}円")
