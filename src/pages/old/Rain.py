import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
import dash_bootstrap_components as dbc
import dash_bootstrap_components as dbc


alt.data_transformers.enable('data_server')

wine = pd.read_csv("data/processed/wine_quality.csv")

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = 
dbc.Container([
    html.H1('Various Features in Different Quality Factors'),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(html.H3('Wine Type')),
                color='info'),

            dcc.Checklist(
                id = "winetype",
                options = [
                    {"label": "White Wine", "value": "white"},
                    {"label": "Red Wine", "value": "red"}
                ],
                value = ["red", "white"],
                labelStyle={"display": "block"}
            )
        ]),
        dbc.Col([
            html.H3('Select your variables:'),

            html.H4('X-axis'),
            
            # dcc.Dropdown(
            #     id = "type-widget",
            #     options=[
            #         {'label': 'White', 'value': 'white'},
            #         {'label': 'Red', 'value': 'red'}],
            #     value='white', placeholder = "Select Wine Type"),
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
])

# Set up callbacks/backend
@app.callback(
     Output('scatter','srcDoc'),
     Input('xcol-widget', 'value'),
     Input('ycol-widget', 'value'),
     Input("winetype", "value")
     )

def plot_scatter(xcol,ycol, winetype):

    wine_dif = wine.loc[(wine['Wine'].isin(winetype))]

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['Wine'], bind='legend')

    base = alt.Chart(wine_dif).properties(
    width=400,
    height=400
    ).add_selection(brush)

    points = base.mark_point().encode(
    x = alt.X(xcol, scale=alt.Scale(zero=False)),
    y = alt.Y(ycol, scale=alt.Scale(zero=False)),
    color=alt.condition(brush, 'Quality_Factor:N', alt.value('lightgray')),
    opacity=alt.condition(click, alt.value(0.9), alt.value(0.2))
    )
    
    bars = alt.Chart(wine_dif, title="Percentage of Each Quality Factor").transform_joinaggregate(
    total='count(*)'
    ).transform_calculate(
    pct='1 / datum.total'
    ).mark_bar().encode(
    alt.X('sum(pct):Q', axis=alt.Axis(format='%')),
    alt.Y('Quality_Factor:N'),
    color = 'Quality_Factor:N',
    tooltip = 'count(Quality_Factor):Q'
    ).transform_filter(brush)

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
    x=alt.X('Quality',
            bin=alt.Bin(step=1), # step keeps bin size the same
            scale=alt.Scale(zero=False)),
    y=alt.Y('count()',
            stack=None),
    color=alt.Color('Quality_Factor:N'),
    tooltip = 'count(Quality):Q'
    ).transform_filter(brush)
    
    chart = (points & bars | hists).add_selection(click)
    return chart.to_html()


if __name__ == '__main__':
    app.run_server(debug=True)