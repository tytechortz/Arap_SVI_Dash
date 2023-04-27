from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import geopandas as gpd
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from urllib.request import urlopen
import json

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])

header = html.Div("Arapahoe Census Tract SVI Data", className="h2 p-2 text-white bg-primary text-center")

bgcolor = "#f3f3f1"  # mapbox light map land color

template = {"layout": {"paper_bgcolor": bgcolor, "plot_bgcolor": bgcolor}}

gdf_2020 = gpd.read_file('2020_CT/ArapahoeCT.shp')

df_SVI_2020 = pd.read_csv('Colorado_SVI_2020.csv')
df_SVI_2020['YEAR'] = 2020
df = df_SVI_2020.loc[df_SVI_2020['COUNTY'] == 'Arapahoe']
# print(df['FIPS'])

Arap_outline = gpd.read_file("/Users/jamesswank/Python_Projects/Arap_SVI_Dash/us-county-boundaries")


col_list = list(df_SVI_2020)

def blank_fig(height):
    """
    Build blank figure with the requested height
    """
    return {
        "data": [],
        "layout": {
            "height": height,
            "template": template,
            "xaxis": {"visible": False},
            "yaxis": {"visible": False},
        },
    }

app.layout = dbc.Container([
    header,
    dbc.Row(dcc.Graph(id='ct-map', figure=blank_fig(500))),
    dbc.Row([
        dbc.Col([
            dcc.RadioItems(
                id='category-radio',
                options=[
                    {'label': 'Total', 'value': 'E_'},
                    {'label': 'Pct.', 'value': 'EP_'},
                    {'label': 'Percentile', 'value': 'EPL_'},
                    {'label': 'Flag', 'value': 'F_'},
                ],
                value='E_' 
            ),
        ], width=3),
        dbc.Col([
            dcc.Dropdown(
                id='variable-dropdown',
            ),
        ], width=2),
        dbc.Col([
            dcc.Slider(0, 1, value=1,
                marks={
                    0: {'label': 'Light', 'style': {'color': 'white'}},
                    1: {'label': 'Dark', 'style': {'color': 'white'}},
                },
                id = 'opacity',
            ),
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.RangeSlider(
                id='pct-slider',
                min=0,
                max=20,
                step=1,
                value=[0,20],
                # options=[
                #     {'label': 'Total', 'value': 'E_'},
                #     {'label': 'Pct.', 'value': 'EP_'},
                #     {'label': 'Percentile', 'value': 'EPL_'},
                #     {'label': 'Flag', 'value': 'F_'},
                # ],
            ),
        ], width=3),
        
    ]),
    dcc.Store(id='pct-data', storage_type='session'),
])


@app.callback(
        Output('variable-dropdown', 'options'),
        Input('category-radio', 'value'))
def category_options(selected_value):
    
    variables = [{'label': i, 'value': i} for i in list(filter(lambda x: x.startswith(selected_value), col_list))]

    return variables 

@app.callback(
        Output('pct-data', 'data'),
        Input('pct-slider', 'value'),
        Input('variable-dropdown', 'value'))
def category_options(pct, variable):
    print(pct[1])


    df_pct = df.loc[(df[variable] >= pct[0]) & (df[variable] <= pct[1])]
    print(df_pct)

    return df_pct.to_json()

@app.callback(
    Output('ct-map', 'figure'),
    Input('category-radio', 'value'),
    Input('opacity', 'value'),
    Input('pct-slider', 'value'),
    Input('pct-data', 'data'),
    Input('variable-dropdown', 'value'))
def get_figure(category, opacity, pct, data, variable):
    
    selection=variable

    df_sel = pd.read_json(data)

    df_sel['FIPS'] = df_sel["FIPS"].astype(str)

    tgdf = gdf_2020.merge(df_sel, on='FIPS')
    tgdf = tgdf.set_index('FIPS')
   
    fig=go.Figure()


    # colorscale=[pctile[0], 'rgb(240,248,255)'],[pctile[1], 'rgb(255, 255, 0)']

    if variable:
        fig.add_trace(go.Choroplethmapbox(
            geojson=eval(tgdf['geometry'].to_json()),
                            locations=tgdf.index,
                            z=tgdf[selection],
                            coloraxis='coloraxis',
                            marker={'opacity':opacity},
                            # colorscale=([0, 'rgb(240,248,255)'],[1, 'rgb(255, 255, 0)']),
                            # colorscale = colorscale,
                            zmin=0,
                            zmax=1,
                            # showlegend=True,
        ))

    else:
        fig = go.Figure(go.Scattermapbox(
            mode = "markers",
            lon = [-73.605], lat = [45.51],
            # showlegend=True
            ))

    layer = [
        {
            "source": Arap_outline["geometry"].__geo_interface__,
            "type": "line",
            "color": "black"
        }
    ]

    fig.update_layout(mapbox_style="carto-positron", 
                        mapbox_zoom=10.4,
                        mapbox_layers=layer,
                        mapbox_center={"lat": 39.65, "lon": -104.8},
                        margin={"r":0,"t":0,"l":0,"b":0},
                        uirevision='constant')


    return fig



if __name__ == "__main__":
    app.run_server(debug=True, port=8000)