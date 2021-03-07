import pandas as pd
import numpy as np
import altair as alt

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# Allow large data set
alt.data_transformers.enable('data_server')

# Data Wrangling
whitewine = pd.read_csv('Data/winequality-white.csv', sep=';')
redwine = pd.read_csv('Data/winequality-red.csv', sep=';')

whitewine["type"] = "white"
redwine["type"] = "red"

wine = redwine.append(whitewine)

# Correlation Data

# Get correlations for each wine type
corr_df_white = wine.loc[wine['type'] == 'white'].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
corr_df_white["type"] = "white"

corr_df_red = wine.loc[wine['type'] == 'red'].select_dtypes('number').corr('spearman').stack().reset_index(name='corr')
corr_df_red["type"] = "red"

# Bind them together
corr_df = corr_df_white.append(corr_df_red)

#Remove full correlations on diag
corr_df.loc[corr_df['corr'] == 1, 'corr'] = 0
# Add column for absolute corr 
corr_df['abs'] = corr_df['corr'].abs()

# Get a list of unique column names
variables = corr_df["level_0"].unique()

# Matrix plot. I couldn't figure out how to make it work at the bottom without a callback input
def plot_matrix():
    click = alt.selection_multi(fields=['type'], bind='legend') 
    chart = alt.Chart(corr_df,title="Correlation Plot for Numeric Features").mark_square().encode(
        color=alt.Color('type', scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue'])),
        x='level_0',
        y='level_1',
        size='abs',
        opacity=alt.condition(click, alt.value(0.7), alt.value(0)),
        tooltip=["type", "corr"]
    ).configure_title(fontSize=18).properties(height=250, width=250).add_selection(click)
    return chart.to_html()

# Setup app

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id = "type-widget",
        options=[
            {'label': 'White Wine', 'value': 'white'},
            {'label': 'Red Wine', 'value': 'red'}],
        value='white', placeholder = "Select Wine Type"),

    dcc.Dropdown(
        id = "x-axis",
        options=[{"label": i, "value": i} for i in variables],
        value = "alcohol",
        clearable = False
    ),

    dcc.Dropdown(
        id = "y-axis",
        options=[{"label": i, "value": i} for i in variables],
        value = "chlorides",
        clearable = False
    ),

    html.Iframe(
        id = "matrix",
        srcDoc = plot_matrix(),
        style={'border-width': '0', 'width': '100%', 'height': '400px'}),

    html.Iframe(
        id = "scatter",
        style={'border-width': '0', 'width': '100%', 'height': '400px'}
    )
    ]) 

# Make scatterplot

@app.callback(
    Output("scatter", "srcDoc"),
    Input("x-axis", "value"),
    Input("y-axis", "value")
)
def plot_scatter(xcol, ycol):
    click = alt.selection_multi(fields=['type'], bind='legend') 
    chart = alt.Chart(wine).mark_point().encode(
    alt.X(xcol, scale = alt.Scale(zero = False)),
    alt.Y(ycol, scale = alt.Scale(zero = False)),
    alt.Color("type", scale=alt.Scale(domain=['red', 'white'],
                range=['darkred', 'blue'])),
    opacity=alt.condition(click, alt.value(0.5), alt.value(0)),
    )
    regression = chart.transform_regression(xcol,ycol, groupby = ["type"],
                                        # By default lines don't go beyond data and are hard to read in this dense dataset
                                       extent = [min(wine[xcol]) - 1, max(wine[xcol]) + 1]).mark_line(size = 5)
    chart = (chart + regression).add_selection(click)
    return chart.to_html()

if __name__ == '__main__':
    app.run_server(debug=True)
