
import numpy as np
import pandas as pd
import altair as alt

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pathlib
from utils import Header, make_dash_table




#------------------
# imort data

wine = pd.read_csv("src/data/wine_quality.csv")
#---------------------

def create_layout(app):

    return dbc.Container(
        [Header(app),
             # first plot (Luka)
             dbc.Row([
                dbc.Col([
                    html.H2('Luka'),
                    html.Iframe(
                        id='first_plot',
                        style={'border-width': '0', 'width': '100%', 'height': '400px'}),
                    dcc.Dropdown(
                        id='xcol-widget',
                        value='Ph',  # REQUIRED to show the plot on the first page load
                        options=[{'label': col, 'value': col} for col in wine.columns])
                    ]),
                    
                    html.H1('Various Features in Different Quality Factors'),
                    dbc.Row([
                        dbc.Col([
                            dbc.Card(
                                dbc.CardBody(html.H5('Wine Type')),
                                color='info'),

                            dcc.Checklist(
                                id = "winetype",
                                options = [
                                    {"label": "White", "value": "white"},
                                    {"label": "Red", "value": "red"}
                                ],
                                value = ["red", "white"],
                                labelStyle={"display": "block"}
                                )
                            ]),
                        dbc.Col([
                            html.H3('Select your variables:'),

                            html.H4('X-axis'),
            
           
                            dcc.Dropdown(
                                id='xcol-widget',
                                value='pH',
                                options=[{'label': col, 'value': col} for col in wine.columns],
                                clearable = False
                            ),

                            html.H4("Y-axis"),

                            dcc.Dropdown(
                                id='ycol-widget',
                                value='pH',
                                options=[{'label': col, 'value': col} for col in wine.columns],
                                clearable = False
                                ),
                            ]),

                            html.Iframe(
                                id = "scatter",
                                # srcDoc = plot_scatter(),
                                style={'border-width': '0', 'width': '120%', 'height': '700px'})

                            ])
             ]
                   
    )])