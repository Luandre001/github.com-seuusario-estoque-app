from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_produtos, name='lista_produtos'),
    path('importar-csv/', views.importar_csv, name='importar_csv'),
    path('adicionar-produto/', views.adicionar_produto, name='adicionar_produto'),
]
