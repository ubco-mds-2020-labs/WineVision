import pandas as pd
import numpy as np
import altair as alt

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

# Allow large data set
alt.data_transformers.enable('data_server')

# Get data
wine = pd.read_csv("/data/processed/wine_quality.csv")

corr_df = pd.read_csv("/data/processed/correlation.csv")

# Get a list of unique column names
variables = corr_df["level_0"].unique()
variables = np.delete(variables, np.argwhere(variables == "Quality Factor"))
variables = np.delete(variables, np.argwhere(variables == "Quality Factor Numeric")) #Don't want this as an option in scatterplot

# Setup app

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Iframe(
                id = "matrix",
                style={'border-width': '0', 'width': '100%', 'height': '400px'}),

            html.H5("Wine Type"),

            dcc.Checklist(
                id = "winetype",
                options = [
                    {"label": "White Wines", "value": "white"},
                    {"label": "Red Wines", "value": "red"}
                ],
                value = ["red", "white"],
                labelStyle={"display": "block"}
            ),

            html.H5("Quality"),

            dcc.Slider(
                id = "quality",
                min=0,
                max=3,
                step=1,
                value = 1,
                marks={
                    0: "below average",
                    1: "average",
                    2: "above average",
                    3: "any"
                }
            )

        ]),
        dbc.Col([
            html.Iframe(
                id = "scatter",
                style={'border-width': '0', 'width': '100%', 'height': '400px'}),
                
            html.H5("x-axis:"),

            dcc.Dropdown(
                id = "x-axis",
                options=[{"label": i, "value": i} for i in variables],
                value = "Alcohol (%)",
                clearable = False
                ),

            html.H5("y-axis"),

            dcc.Dropdown(
                id = "y-axis",
                options=[{"label": i, "value": i} for i in variables],
                value = "Chlorides (g/dm^3)",
                clearable = False),
     
        ])
    ]),
    dbc.Row([
    html.Iframe(
        id = "densityplot",
        style={'border-width': '0', 'width': '1200px', 'height': '400px'}
    ),
    ]),

    dcc.Dropdown(
            id = "densvalue",
            options=[{"label": i, "value": i} for i in variables],
            value = "Chlorides (g/dm^3)",
            clearable = False)

])

# Matrix plot. I couldn't figure out how to make it work at the bottom without a callback input
@app.callback(
    Output("matrix", "srcDoc"),
    Input("quality", "value"),
    Input("winetype", "value")
)
def plot_matrix(qual, winetype):
    if qual in [0,1,2]:
        subset = corr_df.loc[(corr_df["Quality Factor Numeric"] == qual) & (corr_df["Wine"].isin(winetype))]
    else:
        subset = corr_df.loc[corr_df["Wine"].isin(winetype)]
    chart = alt.Chart(subset,title="Correlation Plot for Numeric Features").mark_square().encode(
        alt.X('level_0', title = None),
        alt.Y('level_1', title = None),
        color=alt.Color('Wine', scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue'])),
        size='abs',
        tooltip=["Wine", "corr"]
    ).configure_title(fontSize=18).properties(height=250, width=250)
    return chart.to_html()


# Make scatterplot

@app.callback(
    Output("scatter", "srcDoc"),
    Input("x-axis", "value"),
    Input("y-axis", "value"), 
    Input("quality", "value"),
    Input("winetype", "value")
)
def plot_scatter(xcol, ycol, qual, winetype):
    # Subset by quality
    if qual in [0,1,2]:
        subset = wine.loc[(wine["Quality Factor Numeric"] == qual) & (wine["Wine"].isin(winetype))]
    else:
        subset = wine.loc[wine["Wine"].isin(winetype)]
    # Subset by wine type (red, white, or both)

    chart = alt.Chart(subset).mark_circle(size = 0.25).encode(
    alt.X(xcol, scale = alt.Scale(zero = False)),
    alt.Y(ycol, scale = alt.Scale(zero = False)),
    alt.Color("Wine", scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue']))
    )
    regression = chart.transform_regression(xcol,ycol, groupby = ["Wine"],
                                        # By default lines don't go beyond data and are hard to read in this dense dataset
                                       extent = [min(wine[xcol]) - 1, max(wine[xcol]) + 1]).mark_line(size = 5)
    chart = (chart + regression)
    return chart.to_html()

# Lukas density plot
@app.callback(
     Output('densityplot', 'srcDoc'),
     Input('densvalue', 'value')
)
def plot_altair(xcol):
        
    chart = alt.Chart(wine
            ).transform_density(
                density=xcol,
                groupby=['Wine', 'Quality Factor'],
                as_=['value', 'density'],
                steps=200, # bandwidth=5
            ).mark_area(opacity=0.5).encode(
                alt.X('value:Q', title=xcol, axis=alt.Axis(labels=True, grid=True)),
                alt.Y('density:Q', title=None, axis=alt.Axis(labels=False, grid=False, ticks=False)),
                alt.Color('Wine', scale=alt.Scale(range=['darkred', '#ff9581'])),
                alt.Facet('Quality Factor:N', columns = 1)
            ).properties(
                height=200, width=400,
                title = alt.TitleParams(
                text='Wine Quality Factor Distributions', 
                align='left', fontSize=14,
                subtitle='Reds and Whites superimposed', subtitleFontSize=12)
            ).configure_view(stroke=None).configure_headerFacet(title=None, labelAlign='right',labelAnchor='end',  labelFontWeight=600, labelFontSize=12
            ).interactive()
      
    return chart.to_html()



# Make Histogram

# @app.callback(
#     Output("histogram", "srcDoc"),
#     Input("quality", "value"),
#     Input("winetype", "value"),
#     Input("histvalue", "value")
# )
# def plot_histogram(qual, winetype, histvalue):
#     if qual in [0,1,2]:
#         subset = wine.loc[(wine["Quality Factor Numeric"] == qual) & (wine["Wine"].isin(winetype))]
#     else:
#         subset = wine.loc[wine["Wine"].isin(winetype)]

#     chart = alt.Chart(subset).mark_bar().encode(
#         alt.X(histvalue, type = "quantitative", bin=alt.Bin(maxbins=30)),
#         alt.Y("count()"),
#         alt.Color("Wine", scale=alt.Scale(domain=['red', 'white'],
#                 range=['darkred', 'blue']))
#     ).properties(height=300, width=1000)
#     return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)

