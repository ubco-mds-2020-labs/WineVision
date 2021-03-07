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

# Correlation Data

# Get correlations for each wine type
corr_df_white = wine.loc[wine['type'] == 'white'].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
corr_df_white["type"] = "white"

corr_df_red = wine.loc[wine['type'] == 'red'].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
corr_df_red["type"] = "red"

# Bind them together
corr_df = corr_df_white.append(corr_df_red)
corr_df["quality_factor"] = 3 # For all qualities

# Subset by quality and for each and bind
for i in [0,1,2]:
    #Create white df at ith quality
    corr_df_white = wine.loc[(wine['type'] == 'white') & (wine["quality_factor"] == i)].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
    corr_df_white["type"] = "white"
    corr_df_white["quality_factor"] = i
    #create red df at ith quality
    corr_df_red = wine.loc[(wine['type'] == 'red') & (wine["quality_factor"] == i)].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
    corr_df_red["type"] = "red"
    corr_df_red["quality_factor"] = i
    # bind to main df
    corr_df = corr_df.append(corr_df_red)
    corr_df = corr_df.append(corr_df_white)

#Remove full correlations on diag
corr_df.loc[corr_df['corr'] == 1, 'corr'] = 0
# Add column for absolute corr 
corr_df['abs'] = corr_df['corr'].abs()

# Get a list of unique column names
variables = corr_df["level_0"].unique()
variables = np.delete(variables, np.argwhere(variables == "quality_factor")) #Don't want this as an option in scatterplot

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
                value = "alcohol",
                clearable = False
                ),

            html.H5("y-axis"),

            dcc.Dropdown(
                id = "y-axis",
                options=[{"label": i, "value": i} for i in variables],
                value = "chlorides",
                clearable = False),
     
        ])
    ]),
    dbc.Row([
    html.Iframe(
        id = "histogram",
        style={'border-width': '0', 'width': '1200px', 'height': '400px'}
    ),
    ]),

    dcc.Dropdown(
            id = "histvalue",
            options=[{"label": i, "value": i} for i in variables],
            value = "chlorides",
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
        subset = corr_df.loc[(corr_df["quality_factor"] == qual) & (corr_df["type"].isin(winetype))]
    else:
        subset = corr_df.loc[corr_df["type"].isin(winetype)]
    chart = alt.Chart(subset,title="Correlation Plot for Numeric Features").mark_square().encode(
        alt.X('level_0', title = None),
        alt.Y('level_1', title = None),
        color=alt.Color('type', scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue'])),
        size='abs',
        tooltip=["type", "corr"]
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
        subset = wine.loc[(wine["quality_factor"] == qual) & (wine["type"].isin(winetype))]
    else:
        subset = wine.loc[wine["type"].isin(winetype)]
    # Subset by wine type (red, white, or both)

    chart = alt.Chart(subset).mark_circle(size = 0.25).encode(
    alt.X(xcol, scale = alt.Scale(zero = False)),
    alt.Y(ycol, scale = alt.Scale(zero = False)),
    alt.Color("type", scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue']))
    )
    regression = chart.transform_regression(xcol,ycol, groupby = ["type"],
                                        # By default lines don't go beyond data and are hard to read in this dense dataset
                                       extent = [min(wine[xcol]) - 1, max(wine[xcol]) + 1]).mark_line(size = 5)
    chart = (chart + regression)
    return chart.to_html()


# Make Histogram

@app.callback(
    Output("histogram", "srcDoc"),
    Input("quality", "value"),
    Input("winetype", "value"),
    Input("histvalue", "value")
)
def plot_histogram(qual, winetype, histvalue):
    if qual in [0,1,2]:
        subset = wine.loc[(wine["quality_factor"] == qual) & (wine["type"].isin(winetype))]
    else:
        subset = wine.loc[wine["type"].isin(winetype)]

    chart = alt.Chart(subset).mark_bar().encode(
        alt.X(histvalue, type = "quantitative", bin=alt.Bin(maxbins=30)),
        alt.Y("count()"),
        alt.Color("type", scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue']))
    ).properties(height=300, width=1000)
    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)

