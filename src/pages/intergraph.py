
import numpy as np
import pandas as pd
import altair as alt

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pathlib
from utils import Header, make_dash_table


# ------------------
# imort data


# wine = pd.read_csv("src/data/wine_quality.csv")
# Data Wrangling
whitewine = pd.read_csv('Data/winequality-white.csv', sep=';')
redwine = pd.read_csv('Data/winequality-red.csv', sep=';')

whitewine["type"] = "white"
redwine["type"] = "red"

wine = redwine.append(whitewine)

# Add column for factored quality
conditions = [
    wine["quality"] < 6,
    wine["quality"] == 6,
    wine["quality"] > 6
]

values = [0, 1, 2]

wine["quality_factor"] = np.select(conditions, values)
# ---------------------


def create_layout(app):

    return dbc.Container([Header(app),

                          dbc.Row([
                              html.H3(
                                  'Various Features in Different Quality Factors'),
                              html.Div(
                                  dbc.Row([
                                      dbc.Col([
                                          dbc.Card(
                                              dbc.CardBody(
                                                  html.H6('Wine Type')),
                                              color='info'),


                                          dcc.Checklist(
                                              id="winetype",
                                              options=[
                                                  {"label": "White",
                                                      "value": "white"},
                                                  {"label": "Red", "value": "red"}
                                              ],
                                              value=["red", "white"],

                                              labelStyle={"display": "block"},
                                              style={"margin-left": "15px"}
                                          )
                                      ]),

                                      dbc.Col([
                                          html.H4('Select your variables:'),

                                          html.H4('X-axis'),


                                          dcc.Dropdown(
                                              id='xcol-widget',
                                              value='pH',
                                              options=[{'label': col, 'value': col}
                                                       for col in wine.columns],
                                              clearable=False
                                          ),

                                          html.H4("Y-axis"),

                                          dcc.Dropdown(
                                              id='ycol-widget',
                                              value='pH',
                                              options=[{'label': col, 'value': col}
                                                       for col in wine.columns],
                                              clearable=False
                                          ),

                                      ]),

                                      html.Iframe(
                                          id="scatter_1",
                                          # srcDoc = plot_scatter(),
                                          style={'border-width': '0',
                                                 'width': '120%', 'height': '700px'},

                                      ),
                                      dbc.Col([
                                          html.H2('Luka'),
                                          html.Iframe(
                                              id='first_plot',
                                              style={'border-width': '0', 'width': '100%', 'height': '400px'}),
                                          dcc.Dropdown(
                                              id='xcol-widget_dens',
                                              value='pH',  # REQUIRED to show the plot on the first page load
                                              options=[{'label': col, 'value': col} for col in wine.columns])
                                      ]),

                                  ]),
                                  className="twelve columns"

                              )

                          ])

                          ])
