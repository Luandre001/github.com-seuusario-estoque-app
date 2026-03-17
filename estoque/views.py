import subprocess
import sys
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Produto


def lista_produtos(request):
    produtos = Produto.objects.order_by('-atualizado_em')
    return render(request, 'estoque/lista_produtos.html', {'produtos': produtos})


def importar_csv(request):
    try:
        result = subprocess.run([
            sys.executable,
            'manage.py',
            'import_estoque_csv'
        ], capture_output=True, text=True, check=True)
        messages.success(request, 'Importação concluída com sucesso!')
        messages.info(request, result.stdout or 'CSV importado.')
    except subprocess.CalledProcessError as exc:
        messages.error(request, f'Falha na importação: {exc.stderr or exc.stdout or str(exc)}')
    except Exception as exc:
        messages.error(request, f'Falha na importação: {exc}')
    return redirect('lista_produtos')


def adicionar_produto(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        sku = request.POST.get('sku', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        dimensoes = request.POST.get('dimensoes', '').strip()
        quantidade = request.POST.get('quantidade', '0')
        preco = request.POST.get('preco', '0')

        if not nome or not sku:
            messages.error(request, 'Nome e SKU são obrigatórios para adicionar produto.')
            return redirect('lista_produtos')

        try:
            quantidade = int(float(quantidade))
        except Exception:
            quantidade = 0

        preco_parsed = 0.0
        try:
            preco_parsed = float(str(preco).replace('R$', '').replace(',', '.').strip())
        except Exception:
            preco_parsed = 0.0

        Produto.objects.create(
            nome=nome,
            sku=sku,
            categoria=categoria,
            dimensoes=dimensoes,
            quantidade=quantidade,
            preco=preco_parsed,
        )
        messages.success(request, 'Produto adicionado com sucesso.')
    return redirect('lista_produtos')
