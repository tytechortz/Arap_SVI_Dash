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
        ], width=2)
    ]),
])


@app.callback(
        Output('variable-dropdown', 'options'),
        Input('category-radio', 'value')
)
def category_options(selected_value):
    print(selected_value)
    # variables = list(lambda x: x, col_list)
    variables = [{'label': i, 'value': i} for i in list(filter(lambda x: x.startswith(selected_value), col_list))]
    # print([{'label': i, 'value': i} for i in col_list[filter(lambda x: x.startswith(selected_value))]])
    return variables 


@app.callback(
    Output('ct-map', 'figure'),
    Input('category-radio', 'value'),
    Input('variable-dropdown', 'value'))
def get_figure(category, variable):

    selection=variable
    print(variable)

    df['FIPS'] = df["FIPS"].astype(str)

    tgdf = gdf_2020.merge(df, on='FIPS')
    tgdf = tgdf.set_index('FIPS')
    # print(list(tgdf.columns))

    fig=go.Figure()

    if variable:
        

        fig.add_trace(go.Choroplethmapbox(
            geojson=eval(tgdf['geometry'].to_json()),
                            locations=tgdf.index,
                            z=tgdf[selection],
                            # coloraxis='coloraxis',
                            # marker={'opacity':opacity},
                            # colorscale=([0,'rgba(0,0,0,0)'],[1, colors[i]]),
                            zmin=0,
                            zmax=1,
                            showlegend=True,
        ))

    # else:
    #     fig.add_trace(go.Scattermapbox(
    #         mode="lines",

    #     ))
        


        # fig.update_layout(mapbox_style="carto-positron", 
        #                 mapbox_zoom=10.4,
        #                 mapbox_center={"lat": 39.65, "lon": -104.8},
        #                 margin={"r":0,"t":0,"l":0,"b":0},
        #                 uirevision='constant')


        # return fig
    
    else:
        fig = go.Figure(go.Scattermapbox(
            mode = "markers",
            lon = [-73.605], lat = [45.51],
            # marker = {'size': 20, 'color': ["cyan"]},
            showlegend=True
            ))

        # fig.update_layout(mapbox_style="carto-positron", 
        #                 mapbox_zoom=10.4,
        #                 mapbox_center={"lat": 39.65, "lon": -104.8},
        #                 margin={"r":0,"t":0,"l":0,"b":0},
        #                 uirevision='constant')


        # return fig

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