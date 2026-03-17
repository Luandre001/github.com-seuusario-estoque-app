import os
import pathlib

import pandas as pd
import streamlit as st

# Setup Django environment
BASE_DIR = pathlib.Path(__file__).resolve().parent
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'estoque_proj.settings')
import django
django.setup()

from estoque.models import Produto
from django.core.management import call_command

st.set_page_config(page_title='Estoque App', page_icon='📦', layout='wide')

st.title('📦 Estoque Streamlit')
st.write('Gerencie produtos com import CSV e cadastro rápido usando Django ORM.')

with st.expander('➕ Adicionar / Atualizar produto (acima da tabela)', expanded=True):
    with st.form('produto_form'):
        col_a1, col_a2, col_a3 = st.columns(3)
        with col_a1:
            nome = st.text_input('Nome', '')
            categoria = st.text_input('Categoria', '')
        with col_a2:
            sku = st.text_input('SKU', '')
            dimensoes = st.text_input('Dimensões', '')
        with col_a3:
            quantidade = st.number_input('Quantidade', min_value=0, value=1, step=1)

        submitted = st.form_submit_button('Salvar produto')

    if submitted:
        if not nome.strip() or not sku.strip():
            st.error('Nome e SKU são obrigatórios')
        else:
            produto, created = Produto.objects.update_or_create(
                sku=sku.strip(),
                defaults={
                    'nome': nome.strip(),
                    'categoria': categoria.strip(),
                    'dimensoes': dimensoes.strip(),
                    'quantidade': quantidade,
                }
            )
            if created:
                st.success('Produto criado com sucesso ✅')
            else:
                st.success('Produto atualizado com sucesso ✅')

st.markdown('---')

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader('Produtos cadastrados')
    produtos_qs = Produto.objects.order_by('-atualizado_em')
    produtos_df = pd.DataFrame(list(produtos_qs.values('id', 'nome', 'sku', 'categoria', 'dimensoes', 'quantidade', 'atualizado_em')))
    if not produtos_df.empty:
        produtos_df['atualizado_em'] = produtos_df['atualizado_em'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Extrair espessura de SKU ou dimensões
        import re
        def parse_espessura(row):
            sku = str(row.get('sku', ''))
            dimensoes = str(row.get('dimensoes', ''))
            m = re.search(r'([0-9]{2,3})(?:mm|MM|cm|CM)?', sku)
            if m:
                ext = m.group(1)
                if 'cm' in sku.lower():
                    return ext + 'cm'
                return ext + 'mm'
            m = re.search(r'([0-9]{2,3})x', dimensoes)
            if m:
                return m.group(1) + 'cm'
            return ''

        produtos_df['Espessura'] = produtos_df.apply(parse_espessura, axis=1)
        produtos_df['Categoria por descrição'] = produtos_df['nome']

        display_df = produtos_df.rename(columns={
            'nome': 'Nome',
            'categoria': 'Categoria',
            'dimensoes': 'Dimensões',
            'quantidade': 'Quantidade',
            'atualizado_em': 'Atualizado em',
        })
        display_df = display_df[['Nome', 'Categoria por descrição', 'Categoria', 'Espessura', 'Dimensões', 'Quantidade', 'Atualizado em']]
        st.dataframe(display_df, width='stretch')
    else:
        st.info('Nenhum produto cadastrado ainda.')
    if st.button('🔄 Recarregar produtos'):
        pass

with col2:
    st.subheader('Importar estoque.csv')
    if st.button('Importar CSV agora'):
        try:
            call_command('import_estoque_csv')
            st.success('Importação concluída com sucesso!')

        except Exception as exc:
            st.error(f'Erro ao importar CSV: {exc}')
    st.write('Use o CSV `estoque.csv` no diretório do projeto.')

st.markdown('---')

st.write('Use este app como uma interface rápida para seu estoque. Para demo, abra `streamlit run streamlit_app.py`.')
