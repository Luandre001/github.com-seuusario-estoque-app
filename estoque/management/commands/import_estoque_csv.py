import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from estoque.models import Produto


class Command(BaseCommand):
    help = 'Importa produtos de estoque.csv para o modelo Produto'

    def add_arguments(self, parser):
        parser.add_argument('--path', default=settings.BASE_DIR / 'estoque.csv', help='Caminho para o arquivo CSV')

    def handle(self, *args, **options):
        path = options['path']
        self.stdout.write(f'Importando arquivo: {path}')
        imported = 0
        updated = 0

        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sku = row.get('sku') or row.get('SKU')
                nome = row.get('nome_produto') or row.get('nome')
                descricao = row.get('descricao', '')
                categoria = row.get('categoria', '')
                dimensoes = row.get('dimensoes', '')
                quantidade = row.get('quantidade', row.get('Quantidade', '0'))
                preco_raw = row.get('preco', row.get('Preço (R$)', '0'))
                preco = 0.0
                if isinstance(preco_raw, str):
                    preco_raw = preco_raw.replace('R$', '').replace('r$', '').replace(',', '.').strip()
                try:
                    preco = float(preco_raw)
                except Exception:
                    preco = 0.0

                if not (sku and nome):
                    self.stdout.write(self.style.WARNING(f'Ignorado registro sem SKU ou nome: {row}'))
                    continue

                quantidade_int = 0
                try:
                    quantidade_int = int(float(quantidade))
                except Exception:
                    quantidade_int = 0

                produto, created = Produto.objects.update_or_create(
                    sku=sku,
                    defaults={
                        'nome': nome,
                        'descricao': descricao,
                        'categoria': categoria,
                        'dimensoes': dimensoes,
                        'quantidade': quantidade_int,
                        'preco': preco,
                    }
                )
                if created:
                    imported += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f'Importação concluída: {imported} criados, {updated} atualizados.'))
