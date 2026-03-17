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

st.title('📦 Estoque Controlo Luan')
st.write('Gerencie produtos com import CSV e cadastro rápido usando Django ORM.')

# Clear form state fields after save
if 'nome' not in st.session_state:
    st.session_state.nome = ''
if 'descricao' not in st.session_state:
    st.session_state.descricao = ''
if 'espessura' not in st.session_state:
    st.session_state.espessura = ''
if 'dimensoes' not in st.session_state:
    st.session_state.dimensoes = ''
if 'quantidade' not in st.session_state:
    st.session_state.quantidade = 1

with st.expander('➕ Adicionar / Atualizar produto (acima da tabela)', expanded=True):
    with st.form('produto_form'):
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            nome = st.text_input('Nome', value=st.session_state.nome, key='nome')
            descricao = st.text_input('Descrição', value=st.session_state.descricao, key='descricao')
        with col_a2:
            espessura = st.text_input('Espessura (ex: 19mm)', key='espessura')
            dimensoes = st.text_input('Dimensões', key='dimensoes')
            quantidade = st.number_input('Quantidade', min_value=0, step=1, key='quantidade')

        submitted = st.form_submit_button('Salvar produto')

    if submitted:
        if not nome.strip():
            st.error('Nome é obrigatório')
        else:
            sku = espessura.strip() or f"AUTO-{abs(hash(nome))%1000000}"
            produto, created = Produto.objects.update_or_create(
                sku=sku,
                defaults={
                    'nome': nome.strip(),
                    'categoria': descricao.strip(),
                    'dimensoes': dimensoes.strip(),
                    'quantidade': quantidade,
                    'preco': 0.0,
                }
            )
            if created:
                st.success('Produto criado com sucesso ✅')
            else:
                st.success('Produto atualizado com sucesso ✅')

            # Reset form fields
            st.session_state.nome = ''
            st.session_state.descricao = ''
            st.session_state.espessura = ''
            st.session_state.dimensoes = ''
            st.session_state.quantidade = 1

st.markdown('---')

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader('Produtos cadastrados')
    produtos_qs = Produto.objects.order_by('-atualizado_em')
    produtos_df = pd.DataFrame(list(produtos_qs.values('id', 'nome', 'sku', 'categoria', 'dimensoes', 'quantidade', 'atualizado_em')))
    if not produtos_df.empty:
        produtos_df['atualizado_em'] = produtos_df['atualizado_em'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # SKU/espessura já está no campo sku; categoria por descrição vem de nome
        # (não adicionamos coluna extra para evitar nomes duplicados no data_editor)
        display_df = produtos_df.rename(columns={
            'nome': 'Nome',
            'categoria': 'Descrição',
            'sku': 'Espessura',
            'dimensoes': 'Dimensões',
            'quantidade': 'Quantidade',
            'atualizado_em': 'Atualizado em',
        })
        display_df = display_df[['Nome', 'Descrição', 'Espessura', 'Dimensões', 'Quantidade', 'Atualizado em']]
        st.dataframe(display_df, width='stretch')

        st.write('### ✅ Excluir direto no editor de tabela')
        editor_df = produtos_df.rename(columns={
            'id': 'ID',
            'nome': 'Nome',
            'categoria': 'Descrição',
            'sku': 'Espessura',
            'dimensoes': 'Dimensões',
            'quantidade': 'Quantidade',
            'atualizado_em': 'Atualizado em',
        })[['ID', 'Nome', 'Descrição', 'Espessura', 'Dimensões', 'Quantidade', 'Atualizado em']]
        editor_df['Excluir'] = False

        edited = st.data_editor(editor_df, num_rows='dynamic', use_container_width=True, key='produtos_editor')
        ids_to_remove = []
        if 'Excluir' in edited.columns and 'ID' in edited.columns:
            ids_to_remove = edited.loc[edited['Excluir'] == True, 'ID'].tolist()

        if st.button('Excluir selecionados no editor'):
            if not ids_to_remove:
                st.warning('Marque pelo menos uma linha na coluna Excluir antes de apagar.')
            else:
                deleted_count, _ = Produto.objects.filter(id__in=ids_to_remove).delete()
                st.success(f'{deleted_count} produto(s) excluído(s) com sucesso.')
                st.info('Recarregue a página para ver a lista atualizada.')
    else:
        st.info('Nenhum produto cadastrado ainda.')
    if st.button('🔄 Recarregar produtos'):
        st.info('Para atualizar, recarregue a página do navegador.')

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
