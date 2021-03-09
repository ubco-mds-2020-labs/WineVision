import pandas as pd
import numpy as np
import altair as alt

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from pages import (
    Quality_factors,
    Overview,
    Wine_type,
)

# ------------------------------------------------------
# Get data
wine = pd.read_csv("data/processed/wine_quality.csv")
corr_df = pd.read_csv("data/processed/correlation.csv")


# Get a list of unique column names
variables = corr_df["level_0"].unique()
variables = np.delete(variables, np.argwhere(variables == "Quality Factor"))
# Don't want this as an option in scatterplot
variables = np.delete(variables, np.argwhere(
    variables == "Quality Factor Numeric"))


# Allow large data set
alt.data_transformers.disable_max_rows()

app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
)

server = app.server

# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Update page


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == '/WineVision/Quality-Factors':
        return Quality_factors.create_layout(app)

    elif pathname == "/WineVision/Wine-Types":
        return Wine_type.create_layout(app)

    elif pathname == "/WineVision/Full-View":
        return (
            Overview.create_layout(app),
            Wine_type.create_layout(app),
            Quality_factors.create_layout_fullview(app)
        )

    else:
        return Overview.create_layout(app)
    


# ------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------
# Rain

# Set up callbacks/backend
@app.callback(
    Output('scatter_1', 'srcDoc'),
    Input('xcol-widget', 'value'),
    Input('ycol-widget', 'value'),
    Input("winetype", "value")
)
def plot_scatter(xcol, ycol, winetype):

    wine_dif = wine.loc[(wine['Wine'].isin(winetype))]

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['Wine'], bind='legend')

    base = alt.Chart(wine_dif).properties(
        width=400,
        height=400
    ).add_selection(brush)

    points = base.mark_point().encode(
        x=alt.X(xcol, scale=alt.Scale(zero=False)),
        y=alt.Y(ycol, scale=alt.Scale(zero=False)),
        color=alt.condition(brush, 'Quality Factor:N', alt.value('lightgray')),
        opacity=alt.condition(click, alt.value(0.9), alt.value(0.2))
    )

    bars = alt.Chart(wine_dif, title="Percentage of Each Quality Factor").transform_joinaggregate(
        total='count(*)'
    ).transform_calculate(
        pct='1 / datum.total'
    ).mark_bar().encode(
        alt.X('sum(pct):Q', axis=alt.Axis(format='%')),
        alt.Y('Quality Factor:N'),
        color='Quality Factor:N',
        tooltip='count(Quality Factor):Q'
    ).transform_filter(brush)

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
        x=alt.X('Quality',
                bin=alt.Bin(step=1),  # step keeps bin size the same
                scale=alt.Scale(zero=False)),
        y=alt.Y('count()',
                stack=None),
        color=alt.Color('Quality Factor:N'),
        tooltip='count(Quality):Q'
    ).transform_filter(brush)

    chart = (points & bars | hists).add_selection(click)
    return chart.to_html()




# ------------eric-------------------------------------------------------------------------------
# Matrix plot. I couldn't figure out how to make it work at the bottom without a callback input
@app.callback(
    Output("matrix", "srcDoc"),
    Input("quality", "value"),
    Input("winetype", "value")
)
def plot_matrix(qual, winetype):
    if qual in [0, 1, 2]:
        subset = corr_df.loc[(corr_df["Quality Factor Numeric"] == qual) & (
            corr_df["Wine"].isin(winetype))]
    else:
        subset = corr_df.loc[corr_df["Wine"].isin(winetype)]
    chart = alt.Chart(subset, title="Correlation Plot for Numeric Features").mark_square().encode(
        alt.X('level_0', title=None),
        alt.Y('level_1', title=None),
        color=alt.Color('Wine', scale=alt.Scale(domain=['red', 'white'],
                                                range=['darkred', 'blue'])),
        size='abs',
        tooltip=["Wine", "corr"]
    ).configure_title(fontSize=18).properties(height=290, width=240)
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
    if qual in [0, 1, 2]:
        subset = wine.loc[(wine["Quality Factor Numeric"] ==
                           qual) & (wine["Wine"].isin(winetype))]
    else:
        subset = wine.loc[wine["Wine"].isin(winetype)]
    # Subset by wine type (red, white, or both)

    chart = alt.Chart(subset).mark_circle(size=0.25).encode(
        alt.X(xcol, scale=alt.Scale(zero=False)),
        alt.Y(ycol, scale=alt.Scale(zero=False)),
        alt.Color("Wine", scale=alt.Scale(domain=['red', 'white'],
                                          range=['darkred', 'blue']))
    ).properties(height=350, width=330)
    regression = chart.transform_regression(xcol, ycol, groupby=["Wine"],
                                            # By default lines dosn't go beyond data and are hard to read in this dense dataset
                                            extent=[min(wine[xcol]) - 1, max(wine[xcol]) + 1]).mark_line(size=5)
    chart = (chart + regression)
    return chart.to_html()

# Lukas density plot


@app.callback(
    Output("densityplot", "srcDoc"),
    Input("quality", "value"),
    Input("winetype", "value"),
    Input("densvalue", "value")
)
def plot_density(qual, winetype, xcol):
    if qual in [0, 1, 2]:
        subset = wine.loc[(wine["Quality Factor Numeric"] ==
                           qual) & (wine["Wine"].isin(winetype))]
    else:
        subset = wine.loc[wine["Wine"].isin(winetype)]
    chart = alt.Chart(subset
                      ).transform_density(
        density=xcol,
        groupby=['Wine', 'Quality Factor'],
        as_=['value', 'density'],
        steps=200,  # bandwidth=5
    ).mark_area(opacity=0.5).encode(
        alt.X('value:Q', title=xcol, axis=alt.Axis(
            labels=True, grid=True)),
        alt.Y('density:Q', title=None, axis=alt.Axis(
            labels=False, grid=False, ticks=False)),
        alt.Color("Wine", scale=alt.Scale(domain=['red', 'white'],
                                          range=['darkred', 'blue']))
    ).properties(
        height=300, width=1000,
        title=alt.TitleParams(
            text='Wine Quality Factor Distributions',
            align='left', fontSize=14)
    ).configure_view(stroke=None)

    return chart.to_html()


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
