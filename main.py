from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from dash_bootstrap_templates import load_figure_template
import dash_auth

pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pref = pd.read_csv('preferentie_dashboard.csv')

pref = pref.sort_values(by=['DAG_pref', 'MAAND_pref', 'JAAR_pref'], ascending=True)

print(pref.columns)



load_figure_template('bootstrap')

# ========================================== APP ==================================================================================

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
auth = dash_auth.BasicAuth(app,
                           {'ebian':'brill'})

app.layout = dbc.Container([

    dbc.Row([
        html.H1('WELKOM OP HET PREFERENTIE DASHBOARD VAN DE AG APOTHEKEN', style={'textAlign': 'center'})                                      # de titel van het dashboard
    ]),

    dbc.Row([
       html.H4('Selecteer in de dropdowns hieronder een:', style={'textAlign': 'center'})
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col([
            html.H5('Apotheek'),
            dcc.Dropdown(id='selecteer apotheek',                                                   # Input 1: apotheek selectie
                         options=pref['APOTHEEK_pref'].unique(),
                         value= pref['APOTHEEK_pref'].min())

        ]),
        dbc.Col([
            html.H5('Verzekeraar'),
            dcc.Dropdown(id='selecteer verzekeraar',                                                # Input 2: Verzekeraar selectie
                         options=pref['ZORGVERZEKERAARS GROEP_pref'].unique(),
                         value=pref['ZORGVERZEKERAARS GROEP_pref'].min())

        ]),
        dbc.Col([
            html.H5('Herhaalservice includeren?'),
            dcc.Dropdown(id='herhaalservice ja/nee?',                                               # Input 3: herhaalservice selectie
                         options=[{'label':'Ja', 'value':'Ja'},
                                  {'label':'Nee', 'value':'Nee'}],
                         value='Ja')
        ])
    ]),
    html.Br(),

    dbc.Row([
        dbc.Col([], width=3),
        dbc.Col([
            html.H5('Preferent op voorraad?'),
            dcc.Dropdown(id='voorraad mosadex?',                                                    # Input 4: Voorraad selectie
                         options=[{'label':'Ja', 'value':'Ja'},
                                  {'label':'Nee', 'value':'Nee'}],
                         value='Ja')
        ]),
        dbc.Col([
            html.H5('Maand van het jaar'),
            dcc.Dropdown(id='kies een maand-jaar',                                                  # Input 5: Maand selectie
                         options=pref['MAAND-JAAR_pref'].unique(),
                         value=pref['MAAND-JAAR_pref'].min(),
                         )
        ]),
        dbc.Col([], width=3)
    ]),
    html.Br(),
    html.Br(),

    dbc.Row([
        html.H3('Gemist aantal preferente verstrekkingen per medewerker in geselecteerde maand'),
        dcc.Graph(id='gemiste preferente verstrekkingen medewerker')                                 # Output 1: gemiste verstrekkingen per medewerker
    ]),
    html.Br(),
    html.Br(),
    html.Br(),

    dbc.Row([
        html.H3('Gemist aantal verstrekkingen per preferent product (selecteer top-gemiste producten op verstrekking)'),
        html.Br(),
        html.Br(),
        dcc.RadioItems(id='top gemiste producten',                                                  # Input 6: Top-zoveel selectie producten
                       options=[10, 20, 30, 40, 50, 100],
                       value=10,
                       inline=True),
        html.Br(),
        html.Br(),

        dcc.Graph(id='gemiste verstrekkingen per product')                                          # Output 2: gemiste verstrekkingen per product
    ]),
    dbc.Row([
       html.H2('TABEL WEERGAVE VAN GEMISTE PREFERENTE VERSTREKKINGEN', style={'textALign':'center'})
    ]),

    dbc.Row([
        html.Div(id='tabel gemiste verstrekkingen')

    ]),
    html.Br(),
    html.Br(),
    dbc.Row([
        html.H6('De data (1 jan tm 3 april 2024) in dit dashboard bevatten geen: distributierecepten, recepten die contant worden afgerekend of op rekening worden verstrekt aan de patiënt')
    ])

], className='dbc')

@callback(
    Output('gemiste preferente verstrekkingen medewerker', 'figure'),
    Output('gemiste verstrekkingen per product', 'figure'),
    Output('tabel gemiste verstrekkingen', 'children'),
    Input('selecteer apotheek', 'value'),
    Input('selecteer verzekeraar', 'value'),
    Input('herhaalservice ja/nee?', 'value'),
    Input('voorraad mosadex?', 'value'),
    Input('kies een maand-jaar', 'value'),
    Input('top gemiste producten', 'value'),



)

def function(apotheek, verzekeraar, herhaalservice, voorraad, maand, top_gemist):

    if herhaalservice == 'Ja':
        pref1 = pref


    else:
        pref1 = pref.loc[pref['RECEPTHERKOMST_rec'] != 'H']


    pref2 = pref1.loc[(pref1['APOTHEEK_rec']== apotheek) & (pref1['ZORGVERZEKERAARS GROEP_pref'] == verzekeraar) & (pref1['OP VOORRAAD MOSADEX?_pref'] == voorraad) & (pref1['MAAND-JAAR_pref'] == maand)]


    mw = pref2.groupby(by=['MAAND-JAAR_pref', 'MW_rec'])['MW_rec'].count().to_frame(name='GEMISTE PREFERENTE VERSTREKKINGEN PER MEDEWERKER').reset_index()
    mw = mw.sort_values(by=['GEMISTE PREFERENTE VERSTREKKINGEN PER MEDEWERKER'], ascending=False)

    grafiek_1_medewerker = px.bar(mw,                                                                                                                   # GRAFIEK 1: in dashboard
                                  x='MW_rec',
                                  y='GEMISTE PREFERENTE VERSTREKKINGEN PER MEDEWERKER',
                                  text_auto=True)

    prod = pref2.groupby(by=['MAAND-JAAR_pref', 'ETIKETNAAM PREF_pref', 'ZI PREF_pref', 'APOTHEEK_pref'])['ETIKETNAAM PREF_pref'].count().to_frame(name='GEMIST PER PREF PRODUCT').reset_index()



    prod1 = prod.nlargest(columns=['GEMIST PER PREF PRODUCT'], n= top_gemist)

    prod1 = prod1.sort_values(by=['GEMIST PER PREF PRODUCT'], ascending=False)



    # probeer prod1 te mergen met pref en dan de kolom [ZI PREF_pref toevoegen] en [MIN/MAX vrd toevoegen], dit zodat je deze kolommen als hover_date kan toevoegen

    grafiek_2_product = px.bar(prod1,
                               x='ETIKETNAAM PREF_pref',
                               y='GEMIST PER PREF PRODUCT',
                               text_auto=True,
                               hover_data='ZI PREF_pref')



    tabel3 = pref2.groupby(by=['ZI PREF_pref', 'ETIKETNAAM PREF_pref','APOTHEEK_pref', 'MIN/MAX VRD_assort', 'CF(JA/NEE'])['ZI PREF_pref'].count().to_frame(name='AANTAL GEMISTE VERSTREKKING/PREF PRODUCT').reset_index()


    tabel_pref = dash_table.DataTable(
        columns=[{'name': i, 'id': i} for i in tabel3.columns],
        sort_action = 'native',
        export_format='xlsx',
        data=tabel3.to_dict('records')
    )



    return grafiek_1_medewerker, grafiek_2_product, tabel_pref


if __name__ == '__main__':
    app.run_server(debug=True)