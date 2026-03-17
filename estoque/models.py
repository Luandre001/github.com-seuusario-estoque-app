from django.db import models

class Produto(models.Model):
    nome = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    dimensoes = models.CharField(max_length=120, blank=True)
    quantidade = models.PositiveIntegerField(default=0)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} ({self.sku})"
