#import os
# os.chdir('../../')

import numpy as np
import pandas as pd
import altair as alt
import pathlib

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from utils import Header, make_dash_table  # src.utils for heroku


# Allow large data set
# testing to fix NoSuchEntryPoint error
from altair_data_server import data_server
alt.data_transformers.enable('data_server')

# Get data
wine = pd.read_csv("data/processed/wine_quality.csv")

corr_df = pd.read_csv("data/processed/correlation.csv")

# Get a list of unique column names
variables = corr_df["level_0"].unique()
variables = np.delete(variables, np.argwhere(variables == "Quality Factor"))
# Don't want this as an option in scatterplot
variables = np.delete(variables, np.argwhere(
    variables == "Quality Factor Numeric"))


# Matrix plot. I couldn't figure out how to make it work at the bottom without a callback input
def plot_matrix():
    click = alt.selection_multi(fields=['type'], bind='legend')
    chart = alt.Chart(corr_df, title="Correlation Plot for Numeric Features").mark_square().encode(
        color=alt.Color('type', scale=alt.Scale(domain=['red', 'white'],
                                                range=['darkred', 'blue'])),
        x='level_0',
        y='level_1',
        size='abs',
        opacity=alt.condition(click, alt.value(0.7), alt.value(0)),
        tooltip=["type", "corr"]
    ).configure_title(fontSize=18).properties(height=250, width=250).add_selection(click)
    return chart.to_html()


def create_layout(app):
    # Page layouts
    layout = html.Div(
        [html.Div([Header(app)]),


            # page 1
            html.Div(
                [  # Row 3
                    html.Div(

                        [html.H3('Motivation'),
                            # html.Br([]),
                            html.H6(
                                "\
                                    Wine is a multi billion dollar global industry. \
                                With 36 billion bottles of wine produced each year 1,producers are constantly looking for ways to outperform \
                                the competition and create the best wines they can. \
                                Portugal in particular is second in the world for per-capita wine \
                                consumption 2 and eleventh for wine production, creating over 600,000 \
                                litres per year 3.Physicochemical components are fundamental to a wine’s quality \
                                and those who understand this aspect of wine will have a greater edge into crafting an enjoyable \
                                and profitable product.Wine quality evaluation is the main part of the certification process to \
                                improve wine making. It is generally assessed by physicochemical tests and sensory analysis. \
                                The relationship between physicochemical structure and subjective quality is complex. \
                                No individual component can be used to accurately predict a wine’s quality, and interactions \
                                are as important as the components themselves. For example, perhaps higher alcohol content only  \
                                improves a wine within a certain range of sulphate content, and wines outside this range are made \
                                worse by higher alcohol content. Trained wine tasting experts are able to reliably score wine on a \
                                scale ranging from 0 (very bad) to 10 (excellent), and those scores can be used to determine how these \
                                physicochemical properties affect quality.Our interactive dashboard will allow users to explore a number \
                                of physicochemical variables and how they interact to determine the subjective quality of a wine. \
                                Our visualizations will allow users to test and discover for themselves these relationships. \
                                Wine producers, wine enthusiasts, and curious individuals can all make use of this dashboard.",
                            style={'color': "#FFFFFF"},
                            className="row",
                        ),
                        ],
                        className="product"
                    ),



                ],

            className="twelve columns"),
         dcc.Markdown('''

# This is an <h1> tag

## This is an <h2> tag

###### This is an <h6> tag
'''),


         ]
    )
    return layout
