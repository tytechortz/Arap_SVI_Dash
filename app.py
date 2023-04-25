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
        ], width=2)
    ]),
])



@app.callback(
    Output('ct-map', 'figure'),
    Input('category-radio', 'value'),
    Input('variable-dropdown', 'value'))
def get_figure(category, variable):

    selection=category

    df['FIPS'] = df["FIPS"].astype(str)

    tgdf = gdf_2020.merge(df, on='FIPS')
    tgdf = tgdf.set_index('FIPS')

    fig = px.choropleth_mapbox(tgdf, 
                                geojson=tgdf.geometry, 
                                color=variable,                               
                                locations=tgdf.index, 
                                # featureidkey="properties.TRACTCE20",
                                # opacity=opacity)
    )

    fig.update_layout(mapbox_style="carto-positron", 
                      mapbox_zoom=10.4,
                      mapbox_center={"lat": 39.65, "lon": -104.8},
                      margin={"r":0,"t":0,"l":0,"b":0},
                      uirevision='constant')


    return fig



if __name__ == "__main__":
    app.run_server(debug=True, port=8000)