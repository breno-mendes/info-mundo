import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

def busca_pais_pelo_iso3(df, sigla_pais):
    pais = df[df['ISO3'] == sigla_pais]
    nome_pais = pais['Country'].values[0]
    return nome_pais

def buscar_pais_pelo_nome(df, nome_pais):
    pais = df[df['Country'] == nome_pais]
    iso3_pais = pais['ISO3'].values[0]
    return iso3_pais

def padronizar_grafico(fig):
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="#f7f5f6",
        plot_bgcolor="#f7f5f6",
        autosize=True,
        width=900,
        height=500,
        title={
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        },
    )
    return fig

def padronizar_grafico_pais(fig, metrica, nome_pais):
    fig.update_layout(
        template="simple_white",
        paper_bgcolor="#f7f5f6",
        plot_bgcolor="#f7f5f6",
        autosize=True,
        width=900,
        height=500,
        title_font_size=24,
        title={
            'text': f"Evolução {metrica}: <span style='color: #34ce00'>{nome_pais}</span>",
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(color="#16350a", size=18),
        ),
        yaxis=dict(
            title_font=dict(size=20),
            tickfont=dict(color="#16350a", size=18),
        )
    )
    return fig

# Função para extração do ANO das colunas, relevante para IDH, Expectativa de Vida e outras.
def extrair_ano(coluna):
    # Extrai o ano da coluna
    ano = coluna.split('(')[1].split(')')[0]
    return int(ano)

def plot_idh_pais(recorte_idh, nome_pais):
    # Filtra o DataFrame apenas para o país especificado
    df_pais = recorte_idh[recorte_idh['Country'] == nome_pais]

    # Criar uma lista de anos e uma lista de valores de IDH
    anos = []
    idh_valores = []

    # Percorrer as colunas do dataframe
    for coluna in df_pais.columns:
        if coluna.startswith('Human Development Index'):
            # Extrair o ano da coluna
            ano = extrair_ano(coluna)
            # Obter o valor de IDH para o ano correspondente
            idh = df_pais[coluna].values[0]
            # Adicionar o ano e o valor de IDH às listas
            anos.append(ano)
            idh_valores.append(idh)

    # Criar o dataframe com os dados de IDH
    df_idh = pd.DataFrame({'Ano': anos, 'Valor': idh_valores})

    # Cria o line plot
    fig = px.line(df_idh, x='Ano', y='Valor', title=f'Evolução do IDH: {nome_pais}', color_discrete_sequence=['#258c03'])
    fig.update_yaxes(title = 'IDH')
    fig = padronizar_grafico_pais(fig, 'do IDH',nome_pais)
    return fig

def plot_expectativa_vida_pais(recorte_expectativa_vida, nome_pais):
    # Filtra o DataFrame apenas para o país especificado
    df_pais = recorte_expectativa_vida[recorte_expectativa_vida['Country'] == nome_pais]

    # Criar uma lista de anos e uma lista de valores de IDH
    anos = []
    expectativa_valores = []

    # Percorrer as colunas do dataframe
    for coluna in df_pais.columns:
        if coluna.startswith('Life Expectancy at Birth'):
            # Extrair o ano da coluna
            ano = extrair_ano(coluna)
            # Obter o valor de IDH para o ano correspondente
            expectativa = df_pais[coluna].values[0]
            # Adicionar o ano e o valor de IDH às listas
            anos.append(ano)
            expectativa_valores.append(expectativa)

    # Criar o dataframe com os dados de IDH
    df_expectativa = pd.DataFrame({'Ano': anos, 'Valor': expectativa_valores})

    # Cria o line plot
    fig = px.line(df_expectativa, x='Ano', y='Valor', title=f'Expectativa de vida: {nome_pais}', color_discrete_sequence=['#258c03'])
    fig.update_yaxes(title = 'Expectativa de Vida')
    fig = padronizar_grafico_pais(fig, 'da Expectativa de Vida',nome_pais)
    return fig

def obter_caminho_bandeira(sigla_pais):
    # Diretório onde as bandeiras estão localizadas
    pasta_bandeira = "bandeiras/"

    # Caminho completo para o arquivo da bandeira
    caminho_bandeira = os.path.join(pasta_bandeira, f"{sigla_pais}.png")

    return caminho_bandeira


def obter_paises_vizinhos(df, nome_pais):
    # Obter a região do país
    regiao = df.loc[df['Country'] == nome_pais, 'UN Region'].values[0]

    # Filtrar os países da mesma região
    df_regiao = df[df['UN Region'] == regiao]

    return df_regiao

def plot_idh_por_regiao(df_regiao, nome_regiao, nome_pais):
    fig = px.line(title=f'Evolução do IDH na região: {nome_regiao}')
    scatter_obj = 0

    for _, linha in df_regiao.iterrows():
        pais = linha['Country']
        valores_idh = []
        anos = []

        for coluna in linha.index:
            if coluna.startswith('Human Development Index'):
                # Extrair o ano da coluna
                ano = extrair_ano(coluna)
                # Obter o valor de IDH para o ano correspondente
                idh = linha[coluna]
                # Adicionar o ano e o valor de IDH às listas
                anos.append(ano)
                valores_idh.append(idh)

        if pais == nome_pais:
            # Destacar a linha do país selecionado
            scatter_obj =  go.Scatter(x=anos, y=valores_idh, name=pais, line=dict(width=3, color='green'),  hovertemplate=f"{pais}: %{{y:.2f}}")
        else:
            fig.add_scatter(x=anos, y=valores_idh, mode='lines', line=dict(color='lightgray'), hovertemplate=f"{pais}: %{{y:.2f}}", showlegend=False)

    if scatter_obj is not None:
        fig.update_layout(legend=dict(x=0, y=1, xanchor='left', yanchor='top'), xaxis_title='Ano', yaxis_title='IDH')  # Posicionar a legenda no canto superior esquerdo
    fig.add_trace(scatter_obj)
    fig = padronizar_grafico_pais(fig, 'do IDH {}'.format(nome_regiao), nome_pais)
    return fig

def evolucao_populacao(df, nome_pais):
    anos = ['1970', '1980', '1990', '2000', '2010', '2015', '2020', '2022']

    df_pais = df[df['Country'] == nome_pais]

    # Cria um dataframe com as informações de população por ano
    df_grafico = df_pais[['ISO3'] + [ano + ' Population' for ano in anos]].copy()

    # Renomeia as colunas para mostrar apenas o ano
    df_grafico.columns = ['ISO3'] + [ano[:4] for ano in anos]

    # Melt do dataframe para transformar as colunas de população em uma única coluna
    df_grafico = df_grafico.melt(id_vars='ISO3', var_name='Ano', value_name='População')

    fig = px.bar(df_grafico, x='Ano', y='População', color='ISO3', title='População por Ano', color_discrete_sequence=['#258c03'])

    fig = padronizar_grafico_pais(fig, 'da População', nome_pais)

    return fig

def evolucao_renda(df, nome_pais):
    # Filtra o DataFrame apenas para o país especificado
    df_pais = df[df['Country'] == nome_pais]

    # Criar uma lista de anos e uma lista de valores com a renda
    anos = []
    renda_valores = []

    # Percorrer as colunas do dataframe
    for coluna in df_pais.columns:
        if coluna.startswith('Gross National Income Per Capita '):
            # Extrair o ano da coluna
            ano = extrair_ano(coluna)
            # Obter o valor da renda no país para o ano correspondente
            renda = df_pais[coluna].values[0]
            # Adicionar o ano e o valor da renda às listas
            anos.append(ano)
            renda_valores.append(renda)

    # Criar o dataframe com os dados das rendas
    df_renda = pd.DataFrame({'Ano': anos, 'Valor': renda_valores})

    # Cria o line plot
    fig = px.line(df_renda, x='Ano', y='Valor', title=f'Evolução da Renda: {nome_pais}', color_discrete_sequence=['#258c03'])

    fig.update_yaxes(title = 'Renda Per Capita')
    fig = padronizar_grafico_pais(fig, 'da Renda', nome_pais)

    return fig

def distribuicao_populacao_mundo(df):
    # Hong Kong é o único país sem uma definição de UN Region no dataset
    pais_sem_regiao = df.loc[(df['Country'] == 'Hong Kong') & (df['UN Region'].isnull())]

    # Atualizar o valor de 'UN Region' para 'Asia'
    df.loc[pais_sem_regiao.index, 'UN Region'] = 'Asia'

    fig = px.sunburst(df, path=['UN Region', 'Country'], values='2022 Population', color='UN Region', hover_data=['2022 Population'], title='População do mundo divida por região', template='simple_white')

    fig = padronizar_grafico(fig)
    fig.update_layout(autosize=False, width=900, height=800)

    fig.update_traces(textinfo='label+value', texttemplate='%{label}: %{value:,}')

    return fig

def correlacao_idh_expectativa(df):

    fig = px.scatter(df, x='Human Development Index (2021)', y='Life Expectancy at Birth (2021)', title='Correlação entre o IDH e Expectativa de Vida', color='UN Region', hover_data=['Life Expectancy at Birth (2021)', 'Country'])
    fig = padronizar_grafico(fig)
    fig.update_xaxes(title = 'IDH')
    fig.update_yaxes(title = 'Expectativa de Vida')
    # fig.update_layout(autosize=False, width=800, height=500)

    return fig

def correlacao_renda_expectativa(df):

    fig = px.scatter(df, x='Gross National Income Per Capita (2021)', y='Life Expectancy at Birth (2021)', title='Correlação entre a Renda Per Capita e Expectativa de Vida', color='UN Region', hover_data=['Life Expectancy at Birth (2021)', 'Country'])

    fig = padronizar_grafico(fig)
    fig.update_layout(autosize=False, width=900, height=500)
    fig.update_xaxes(title = 'Renda Per Capita')
    fig.update_yaxes(title = 'Expectativa de Vida')

    return fig

def formatar_area(area_valor):
    if area_valor < 1000:
        area_formatada = f"{area_valor / 1000}"
        return f'0.{area_valor} km²'
    else:
        area_formatada = f"{area_valor:,}".replace(",", ".")
        return f'{area_formatada} km²'