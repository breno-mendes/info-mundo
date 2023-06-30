import pandas as pd
import numpy as np
import geojson
import os

import plotly.express as px
import plotly.graph_objects as go

import dash 
from dash import Dash, dcc, html, Input, Output, State

import dash_bootstrap_components as dbc

import utils


# Obtém o caminho absoluto para a pasta "assets"
assets_folder = "static"

project_root = os.path.dirname(os.path.abspath(__file__))
assets_path = os.path.join(project_root, assets_folder)

app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY], assets_folder=assets_path, assets_url_path="/static")
server = app.server

# Definição de título e ícone do site
path_favicon = os.path.join(assets_path, "icons" ,"favicon.ico")

app.title='Info Mundo'
if os.path.exists(path_favicon):
    app._favicon = path_favicon

# ===================================================================
# Leitura dos datasets
info_mundo = pd.read_csv(os.path.join(server.static_folder, 'data', 'hdi_info.csv'))
regioes = pd.read_excel(os.path.join(server.static_folder, 'data', 'regioes.xlsx'))
df_populacao = pd.read_csv(os.path.join(server.static_folder, 'data', 'world_population.csv'))

# ====================================================================
# Operações com o GeoJSON
with open(os.path.join(server.static_folder, 'data', 'custom.geo.json'), "r", encoding="utf-8") as f:
    json_paises = geojson.load(f)
paises_locations = json_paises['features']

# Cria a key 'id' para cada pais
paises_iso3_excecao = ['MDV', 'MUS', 'NOR', 'FRA', 'SYC']
for pais in json_paises['features']:
    iso_a3 = pais['properties']['iso_a3']
    iso_a3_eh = pais['properties']['iso_a3_eh']
    if iso_a3_eh in paises_iso3_excecao:
        iso_a3 = iso_a3_eh
    pais['id'] = iso_a3

# Código para criar uma nova propriedade 'sigla' em todos os paises no GeoJSON, que será utilizada para buscar a imagem da bandeira no diretório
excecoes_iso_a2 = ['N. Cyprus', 'Siachen Glacier', 'Somaliland']
for i, pais in enumerate(json_paises['features']):
  sigla = pais['properties']['iso_a2']
  if(pais['properties']['iso_a2'] == '-99'):
    sigla = pais['properties']['iso_a2_eh']
    if(pais['properties']['name'] in excecoes_iso_a2):
      sigla = pais['properties']['postal']
  sigla = sigla.lower()
  pais['properties']['sigla'] = sigla


# ======================================================
# Operações nos Datasets
# Merge no dataset de regiões para plot de comparação entre o país e a região que ele pertence
info_mundo['UNDP Developing Regions'] = info_mundo['ISO3'].map(regioes.set_index('ISO Code')['UN Region'])
info_mundo.rename(columns = {'UNDP Developing Regions': 'UN Region'}, inplace=True)

# Recorte no dataset principal e dataset de população para projeção nos cards e no mapa
recorte_mundo = info_mundo.iloc[:, :5]
recorte_mundo['Gross National Income Per Capita (2021)'] = info_mundo['Gross National Income Per Capita (2021)']
recorte_mundo['Life Expectancy at Birth (2021)'] = info_mundo['Life Expectancy at Birth (2021)']

merged_df = pd.merge(recorte_mundo, df_populacao, left_on='ISO3', right_on='CCA3')

novas_colunas = ['1970 Population', '1980 Population', '1990 Population', '2000 Population', '2010 Population', '2015 Population', '2020 Population', '2022 Population', 'Capital', 'World Population Percentage', 'Area (km²)']
recorte_mundo[novas_colunas] = merged_df[novas_colunas]

recorte_mundo['Human Development Index (2021)'] = info_mundo['Human Development Index (2021)']


# =======================================================
# Definição de listas para dropdowns
# Lista dos países para ser utilizado no Dropdown de Países
dropdown_paises = [{'label': country, 'value': country} for country in info_mundo['Country']]
dropdown_paises.insert(0, {'label': 'Mundo', 'value': 'Mundo'})

dropdown_opcoes_mapa = [
    {'label': ' IDH', 'value': 'idh'},
    {'label': ' População', 'value': 'populacao'},
    {'label': ' Renda', 'value': 'renda'},
    {'label': ' Expectativa de Vida', 'value': 'expectativa_vida'}
]

# ======================================================
# Criação do mapa
fig_mapa = px.choropleth_mapbox(info_mundo, locations='ISO3', geojson=json_paises, color="Human Development Index (2021)",
                            center={"lat": 14.778986, "lon": -15.723305}, zoom=2,
                            color_continuous_scale='ylgn', opacity=0.4,
                            hover_data={"Country": True,"Human Development Groups": True}
                            )
fig_mapa.update_layout(
    paper_bgcolor="#d4dadc",
    autosize=True, # Preenche o tamanho inteiro da tela, ou ROW em que está inserido
    margin=go.Margin(l=0, r=0, t=0, b=0), # Define a margem do mapa
    showlegend=False,
    mapbox_style='carto-positron'
)
fig_mapa.update_coloraxes(colorbar=dict(len=0.5, yanchor='bottom', y=0))
fig_mapa.update_layout(
    coloraxis_colorbar=dict(
        xanchor="left",  # Ancora a escala de cores à esquerda
        yanchor="top",  # Ancora a escala de cores no topo
        x=0.02,  # Define a posição horizontal da escala de cores em relação ao mapa
        y=0.98  # Define a posição vertical da escala de cores em relação ao mapa
    )
)

# ==================================================================================
# App Layout

app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            dbc.Row([
                html.Img(id='logo', src=app.get_asset_url("icons/header.png"))
            ], className='header'),

            dbc.Row([
                html.Div([
                    dbc.Button('Mundo', color="primary", id="location-button", size='lg', className='align-items-center'),
                ], className='d-flex justify-content-center align-items-center')
            ], className='d-flex justify-content-center'),
    
            html.P('Informe o país desejado:', className="input-label", style={'margin-top': '0px'}),
            html.Div(id='div-test', children=[
                dcc.Dropdown(
                    id='paises-dropdown',
                    options=dropdown_paises,
                    value='Mundo',
                    placeholder='Selecione um país',
                    className="dropdown"
                ),
            ]),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span('Bandeira'),
                            html.H3(style={'color': '#adfc92'}, id='bandeira-text'),
                            html.Img(id='bandeira-pais', style={'max-width': '100%', 'height': 'auto', 'box-shadow': '4px 4px 4px 4px rgba(66, 65, 65, 0.15)'})
                        ])
                    ], color='light', outline=True, className="info-card")
                ], md=4),                
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span('População'),
                            html.H3(id='populacao-text', className="info-destaque"),
                            html.Span("% da População Mundial"),
                            html.H5(id='porcentagem-populacao-text', className='info-menor'),
                        ])
                    ], color='light', outline=True, className="info-card")
                ], md=5),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Span('Ranking IDH'),
                            html.H3(id='idh-rank-text', className="info-destaque"),
                            html.Span('IDH'),
                            html.H5(id='idh-text', className='info-menor'),
                        ])
                    ], color='light', outline=True, className="info-card")
                ], md=3),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.Span('Capital:', className='tipo-info-adicional'),
                                html.Span(id='capital-text', className='info-adicional-text'),                            
                            ], className='card-info-adicional'),                            
                            html.Div([
                                html.Span('Renda Média (ano):', className='tipo-info-adicional'),
                                html.Span(id='renda-text', className='info-adicional-text'),                            
                            ], className='card-info-adicional'),                            
                            html.Div([
                                html.Span('Exp. Vida:', className='tipo-info-adicional'),
                                html.Span(id='expectativa-text', className='info-adicional-text'),    
                            ], className='card-info-adicional'),                            
                            html.Div([
                                html.Span('Área:', className='tipo-info-adicional'),
                                html.Span(id='area-text', className='info-adicional-text'),    
                            ], className='card-info-adicional'),
                        ], className='info-adicional')
                    ], color='light', outline=True, className="info-card")
                ], md=12),              
            ], className="info-row"),

            html.Div([
                html.P('Selecione o tipo de dado que deseja visualizar', className="input-label", style={'margin-top': '10px'}),
                dcc.Dropdown(
                    id='graficos-dropdown',
                    value="",
                    placeholder='Escolha o gráfico',
                    className="dropdown"
                ),

                html.Br(),

                html.Div([
                    dcc.Graph(id='grafico-selecionado', figure={})
                ], className='grafico-container')
            ], className="chart-container")
        ], md=5, className="sidebar"),

        dbc.Col([
            html.Div([
                dcc.RadioItems(
                        id='radio-items',
                        options=dropdown_opcoes_mapa,
                        value='idh',   
                        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
                ),
            ], className='radio-container'),
            dcc.Loading(id='loading', type='default', children=[dcc.Graph(id='choropleth-map', figure=fig_mapa, className='mapa')])        
        ], md=7, className='map-col')
    ], className="main-row"),
    fluid=True, style={'width': '100%', 'height': '100vh'}
)

# ================================================================
# Conexão dos componentes com a geração dos gráficos
@app.callback(
    [
        Output(component_id='location-button', component_property='children'),
        Output(component_id='populacao-text', component_property='children'),
        Output(component_id='porcentagem-populacao-text', component_property='children'),
        Output(component_id='idh-rank-text', component_property='children'),
        Output(component_id='idh-text', component_property='children'),
        Output(component_id='graficos-dropdown', component_property='value'),
        Output(component_id='graficos-dropdown', component_property='options'),
        Output(component_id='bandeira-pais', component_property='src'),
        Output(component_id='capital-text', component_property='children'),
        Output(component_id='renda-text', component_property='children'),
        Output(component_id='expectativa-text', component_property='children'),
        Output(component_id='area-text', component_property='children')
    ],
    [Input(component_id='paises-dropdown', component_property='value')],
)
def selecionar_pais(pais):
    global pais_atual
    global grafico

    if pais is not None:
        if pais == 'Mundo':
            populacao_total = recorte_mundo['2022 Population'].sum()
            populacao_formatada = '{:,}'.format(populacao_total).replace(',', '.')
            porcentagem_populacao = '100%'
            idh_rank = ' '
            idh = ' '
            grafico_atual = ''
            caminho_bandeira = app.get_asset_url('bandeiras/world.png')
            capital = ''

            renda_valor = recorte_mundo['Gross National Income Per Capita (2021)'].sum()/len(info_mundo)
            renda = "${:,.2f} USD".format(renda_valor)

            expectativa_vida_valor = recorte_mundo['Life Expectancy at Birth (2021)'].sum()/len(info_mundo)
            expectativa_vida = "{} anos".format(int(expectativa_vida_valor))

            area = utils.formatar_area(510100000)

            opcoes_dropdown_mundo = [
                {'label': 'Distribuição da População Mundial por Região', 'value': 'mundo-populacao'},
                {'label': 'Correlação entre o IDH e a expectativa de vida', 'value': 'mundo-idh-expectativa'},
                {'label': 'Correlação entre a renda e a expectativa de vida', 'value': 'mundo-renda-expectativa'},
            ]
            return (pais, populacao_formatada, porcentagem_populacao, idh_rank, idh, grafico_atual,opcoes_dropdown_mundo, caminho_bandeira, capital,  renda, expectativa_vida, area) 
        else:
            if grafico.startswith('mundo'):
                grafico = ''         
            pais_atual = pais
        
            pais_selecionado = recorte_mundo[recorte_mundo['Country'] == pais]

            populacao_total = f'{pais_selecionado["2022 Population"].values[0]:,}'.replace(",", ".")

            porcentagem_populacao = f'{pais_selecionado["World Population Percentage"].values[0]:.2f}%'
            idh_rank = pais_selecionado['HDI Rank (2021)'].values[0]
            idh = pais_selecionado['Human Development Index (2021)'].values[0]

            capital = pais_selecionado['Capital'].values[0]

            renda_valor = pais_selecionado['Gross National Income Per Capita (2021)'].values[0]
            renda = "${:,.2f} USD".format(renda_valor)

            expectativa_vida_valor = pais_selecionado['Life Expectancy at Birth (2021)'].values[0]
            expectativa_vida = "{} anos".format(int(expectativa_vida_valor))

            area_valor = pais_selecionado['Area (km²)'].values[0]
            area =  utils.formatar_area(area_valor)         

            # Criação de uma variável global para renderizar o mesmo gráfico quando o pais for trocado
            grafico_atual = grafico

            # Busca a sigla do país para retornar o path da sua bandeira
            nome_pais = pais_selecionado['Country'].values[0]
            iso3_pais_selecionado = utils.buscar_pais_pelo_nome(recorte_mundo, nome_pais)
            filtro_json = [feature for feature in json_paises['features'] if feature['id'] == iso3_pais_selecionado]
            sigla_pais = filtro_json[0]['properties']['sigla']
            bandeira_pais = utils.obter_caminho_bandeira(sigla_pais)
            caminho_bandeira = app.get_asset_url(bandeira_pais)

            opcoes_dropdown_pais = [
                                        {'label': 'Evolução da População', 'value': 'evolucao_populacao'},
                                        {'label': 'Evolução do IDH', 'value': 'evolucao_idh'},
                                        {'label': 'Comparação da evolução do IDH pela região', 'value': 'comparacao_idh'},    
                                        {'label': 'Evolução da Expectativa de Vida', 'value': 'evolucao_expectativa_vida'},
                                        {'label': 'Evolução da Renda', 'value': 'evolucao_renda'},
                                        ]

            return (pais, populacao_total, porcentagem_populacao, idh_rank, idh, grafico_atual, opcoes_dropdown_pais, caminho_bandeira, capital, renda, expectativa_vida, area)
    else:
        return dash.no_update

@app.callback(
    Output(component_id="grafico-selecionado", component_property="figure"),
    [Input(component_id='graficos-dropdown', component_property='value'),],
    [State(component_id='paises-dropdown', component_property='value'),
    ],
)
def mostrar_grafico_selecionado(tipo_grafico, pais):
    global pais_atual
    global grafico

    # Define uma figura vazia como valor padrão, caso contrário ao compilar o código, um erro será gerado, pois estamos tentando renderizar uma figura que não foi plotada, além disso, ao carregar a página, já plota um gráfico vazio padronizado.
    fig=go.Figure()

    grafico = tipo_grafico

    pais_atual = pais
    if tipo_grafico == "":
        fig = utils.padronizar_grafico(fig)
    else:
        fig = utils.padronizar_grafico(fig)
        if pais_atual is not None:
            copia_info_mundo = info_mundo.copy()

            if tipo_grafico == 'evolucao_idh':
                recorte_idh = copia_info_mundo.iloc[:,:37]
                fig_idh = utils.plot_idh_pais(recorte_idh, pais_atual)
                fig = fig_idh
            elif tipo_grafico == 'evolucao_expectativa_vida':
                recorte_expectativa_vida = copia_info_mundo.iloc[:, list(range(2)) + list(range(36,69))]
                fig_expectativa_vida = utils.plot_expectativa_vida_pais(recorte_expectativa_vida, pais_atual)
                fig = fig_expectativa_vida
            elif tipo_grafico == 'comparacao_idh':
                nome_regiao = recorte_mundo.loc[recorte_mundo['Country'] == pais_atual, 'UN Region'].values[0]
                recorte_idh = copia_info_mundo.iloc[:,:37]
                df_regiao = utils.obter_paises_vizinhos(recorte_idh, pais_atual)
                fig = utils.plot_idh_por_regiao(df_regiao, nome_regiao, pais_atual)
            elif tipo_grafico == 'evolucao_populacao':
                copia_info_populacao = recorte_mundo.copy()
                fig_populacao = utils.evolucao_populacao(copia_info_populacao, pais_atual)
                fig = fig_populacao
            elif tipo_grafico == 'evolucao_renda':
                fig_renda = utils.evolucao_renda(info_mundo, pais_atual)
                fig = fig_renda
            elif tipo_grafico == 'mundo-populacao':
                copia_info_populacao = recorte_mundo.copy()
                fig_populacao_mundo = utils.distribuicao_populacao_mundo(recorte_mundo)
                fig = fig_populacao_mundo
            elif tipo_grafico == 'mundo-idh-expectativa':
                fig_idh_expectativa = utils.correlacao_idh_expectativa(copia_info_mundo)
                fig = fig_idh_expectativa
            elif tipo_grafico == 'mundo-renda-expectativa':
                fig_renda_expectativa = utils.correlacao_renda_expectativa(copia_info_mundo)
                fig = fig_renda_expectativa
        else:
            return dash.no_update
        
    return fig

@app.callback(
    Output('paises-dropdown', 'value'),
    [Input('choropleth-map', 'clickData')]
)
def update_location(click_data):
    changed_id = [p['prop_id'] for p in  dash.callback_context.triggered][0]

    if click_data is not None and changed_id != 'location-button.n_clicks':
        pais_iso3 = click_data['points'][0]['location']
        pais_nome = utils.busca_pais_pelo_iso3(recorte_mundo, pais_iso3)
        return pais_nome
    else:
        return None

@app.callback(
    [Output(component_id='choropleth-map', component_property='figure')],
    [Input(component_id='radio-items', component_property='value')],
)
def update_map(opcao_mapa):
    if opcao_mapa is not None:
        if opcao_mapa == 'idh':
            opcao_escolhida = "Human Development Index (2021)"
        elif opcao_mapa == 'populacao':
            opcao_escolhida = "2022 Population"
        elif opcao_mapa == 'renda':
            opcao_escolhida = "Gross National Income Per Capita (2021)"
        elif opcao_mapa == 'expectativa_vida':
            opcao_escolhida = "Life Expectancy at Birth (2021)"

        mapa = px.choropleth_mapbox(recorte_mundo, locations='ISO3', geojson=json_paises, color=opcao_escolhida,
                                center={"lat": 14.778986, "lon": -15.723305}, zoom=2,
                                color_continuous_scale='ylgn', opacity=0.4,
                                hover_data={"Country": True}
                                )
        mapa.update_layout(
            paper_bgcolor="#d4dadc",
            autosize=True, # Preenche o tamanho inteiro da tela, ou ROW em que está inserido
            margin=go.Margin(l=0, r=0, t=0, b=0), # Define a margem do mapa
            showlegend=False,
            mapbox_style='carto-positron'
        )
        mapa.update_coloraxes(colorbar=dict(len=0.5, yanchor='bottom', y=0))
        mapa.update_layout(
            coloraxis_colorbar=dict(
                xanchor="left",  # Ancora a escala de cores à esquerda
                yanchor="top",  # Ancora a escala de cores no topo
                x=0.02,  # Define a posição horizontal da escala de cores em relação ao mapa
                y=0.98  # Define a posição vertical da escala de cores em relação ao mapa
            )
        )

        return [mapa]
    else:
        return dash.no_update

# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)