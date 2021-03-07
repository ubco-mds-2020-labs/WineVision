import pandas as pd
import numpy as np
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import altair as alt
import dash_bootstrap_components as dbc


alt.data_transformers.enable('data_server')

white_wine = pd.read_csv('winequality-white.csv', sep=';')
red_wine = pd.read_csv('winequality-red.csv', sep=';')

white_wine["type"] = "white"
red_wine["type"] = "red"
wine = red_wine.append(white_wine)

# wine_df.loc[0] = ['g/dm3','g/dm3','g/dm3','g/dm3','g/dm3','mg/dm3','mg/dm3','g/cm3', np.nan,'g/dm3','%vol', np.nan, np.nan]
# wine_df.to_csv('wine_new.csv', index=False)

# wine = pd.read_csv('wine_new.csv', header=[0,1])
# wine.columns = wine.columns.map(' in '.join)
# wine = wine.rename(columns = {'pH in Unnamed: 8_level_1':'pH', 'quality in Unnamed: 11_level_1':'quality', 'type in Unnamed: 12_level_1': 'type'})
wine['quality_factor'] = np.where(wine['quality']<6, 'Below Average', (np.where(wine['quality']>6.5, 'Above Average', 'Average')))


# Setup app and layout/frontend

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
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

    wine_dif = wine.loc[(wine['type'].isin(winetype))]

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['type'], bind='legend')

    base = alt.Chart(wine_dif).properties(
    width=400,
    height=400
    ).add_selection(brush)

    points = base.mark_point().encode(
    x = alt.X(xcol, scale=alt.Scale(zero=False)),
    y = alt.Y(ycol, scale=alt.Scale(zero=False)),
    color=alt.condition(brush, 'quality_factor:N', alt.value('lightgray')),
    opacity=alt.condition(click, alt.value(0.9), alt.value(0.2))
    )
    
    bars = alt.Chart(wine_dif, title="Percentage of Each Quality Factor").transform_joinaggregate(
    total='count(*)'
    ).transform_calculate(
    pct='1 / datum.total'
    ).mark_bar().encode(
    alt.X('sum(pct):Q', axis=alt.Axis(format='%')),
    alt.Y('quality_factor:N'),
    color = 'quality_factor:N',
    tooltip = 'count(quality_factor):Q'
    ).transform_filter(brush)

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
    x=alt.X('quality',
            bin=alt.Bin(step=1), # step keeps bin size the same
            scale=alt.Scale(zero=False)),
    y=alt.Y('count()',
            stack=None),
    color=alt.Color('quality_factor:N'),
    tooltip = 'count(quality):Q'
    ).transform_filter(brush)
    
    chart = (points & bars | hists).add_selection(click)
    return chart.to_html()


if __name__ == '__main__':
    app.run_server(debug=True)


