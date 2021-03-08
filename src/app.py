# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import altair as alt
from dash.dependencies import Input, Output
from pages import (
    intergraph,
    overview
)
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


wine = pd.read_csv("src/data/wine_quality.csv")
# corr_df=pd.read_csv("")


# wine['Taste'] = np.where(wine['quality']<6, 'Below average', (np.where(wine['quality']>6.5, 'Above average', 'Average')))

# -------------------------eric data cleaning#------------------------------------------------------------------------------------------------

# Allow large data set
alt.data_transformers.enable('data_server')


app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
    # external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server


# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

# Update page


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == '/WineVison/src/intergraph':
        return intergraph.create_layout(app)

    elif pathname == "/WineVison/src/modelling":
        return modelling.create_layout(app)

    elif pathname == "/WineVision/src/full-view":
        return (
            overview.create_layout(app),
            intergraph.create_layout(app),
            modelling.create_layout(app)
        )

    else:
        return overview.create_layout(app)
    
#------------------------------------------------------------------------------------------------


 # first plot   Luka
#------------------------------------------------------------------------------------------------
@app.callback(
    Output('first_plot', 'srcDoc'),
    Input('xcol-widget_dens', 'value'))
def plot_altair(xcol):
    units = {'Fixed Acidity': '(g/dm3)', 'Volatile Acidity': '(g/dm3)', 'Citric Acid': '(g/dm3)',
             'Residual Sugar': '(g/dm3)', 'Chlorides': '(g/dm3)', 'Density': '(g/dm3)', 'Sulphates': '(g/dm3)',
             'Free Sulfur Dioxide': '(mg/dm3)', 'Total Sulfur Dioxide': '(mg/dm3)', 'Alcohol': '(%vol)', 'pH': ''}
    chart = alt.Chart(wine
                      ).transform_density(
        density=xcol,
        groupby=['type', 'quality_factor'],
        as_=['value', 'density'],
        steps=200,  # bandwidth=5
    ).mark_area(opacity=0.6).encode(
        alt.X('value:Q', title=str(xcol), axis=alt.Axis(labels=True, grid=True)),
        alt.Y('density:Q', title=None, axis=alt.Axis(
            labels=False, grid=False, ticks=False)),
        alt.Color('type', scale=alt.Scale(
            range=['darkred', '#ff9581']))
    ).properties(
        # height=200, width=400,
        title=alt.TitleParams(
            text='Wine Quality Factor Distributions',
            align='left', fontSize=14,
            subtitle='Reds and Whites superimposed', subtitleFontSize=12)).interactive()
    #configure_view(stroke=None).configure_headerFacet(title=None, labelAlign='right', labelAnchor='end', labelFontWeight=600, labelFontSize=12)

    return chart.to_html()
#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------
# Rain



@app.callback(
    Output('scatter_1', 'srcDoc'),
    Input('xcol-widget', 'value'),
    Input('ycol-widget', 'value'),
    Input("winetype", "value")
)
def plot_scatter(xcol, ycol, winetype):

    wine_dif = wine.loc[(wine['type'].isin(winetype))]

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['type'], bind='legend')

    base = alt.Chart(wine_dif).properties(
        width=450,
        height=400
    ).add_selection(brush)

    points = base.mark_point().encode(
        x=alt.X(xcol, scale=alt.Scale(zero=False)),
        y=alt.Y(ycol, scale=alt.Scale(zero=False)),
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
        color='quality_factor:N',
        tooltip='count(quality_factor):Q'
    ).transform_filter(brush)

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
        x=alt.X('quality',
                bin=alt.Bin(step=1),  # step keeps bin size the same
                scale=alt.Scale(zero=False)),
        y=alt.Y('count()',
                stack=None),
        color=alt.Color('quality_factor:N'),
        tooltip='count(quality):Q'
    ).transform_filter(brush)

    chart = (points & bars | hists).add_selection(click)
    return chart.to_html()

#------------------------------------------------------------------------------------------------



# ------------eric-------------------------------------------------------------------------------


# Make scatterplot

# Matrix plot. I couldn't figure out how to make it work at the bottom without a callback input
@app.callback(
    Output("matrix", "srcDoc"),
    Input("quality", "value"),
    Input("winetype", "value")
)
def plot_matrix(qual, winetype):
    if qual in [0, 1, 2]:
        subset = corr_df.loc[(corr_df["quality_factor"] == qual) & (
            corr_df["type"].isin(winetype))]
    else:
        subset = corr_df.loc[corr_df["type"].isin(winetype)]
    chart = alt.Chart(subset, title="Correlation Plot for Numeric Features").mark_square().encode(
        alt.X('level_0', title=None),
        alt.Y('level_1', title=None),
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
def plot_scatter_eric(xcol, ycol, qual, winetype):
    # Subset by quality
    if qual in [0, 1, 2]:
        subset = wine.loc[(wine["quality_factor"] == qual)
                          & (wine["type"].isin(winetype))]
    else:
        subset = wine.loc[wine["type"].isin(winetype)]
    # Subset by wine type (red, white, or both)

    chart = alt.Chart(subset).mark_circle(size=0.25).encode(
        alt.X(xcol, scale=alt.Scale(zero=False)),
        alt.Y(ycol, scale=alt.Scale(zero=False)),
        alt.Color("type", scale=alt.Scale(domain=['red', 'white'],
                                          range=['darkred', 'blue']))
    )
    regression = chart.transform_regression(xcol, ycol, groupby=["type"],
                                            # By default lines don't go beyond data and are hard to read in this dense dataset
                                            extent=[min(wine[xcol]) - 1, max(wine[xcol]) + 1]).mark_line(size=5)
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
    if qual in [0, 1, 2]:
        subset = wine.loc[(wine["quality_factor"] == qual)
                          & (wine["type"].isin(winetype))]
    else:
        subset = wine.loc[wine["type"].isin(winetype)]

    chart = alt.Chart(subset).mark_bar().encode(
        alt.X(histvalue, type="quantitative", bin=alt.Bin(maxbins=30)),
        alt.Y("count()"),
        alt.Color("type", scale=alt.Scale(domain=['red', 'white'],
                                          range=['darkred', 'blue']))
    ).properties(height=300, width=1000)
    return chart.to_html()


#------------------------------------------------------------------------------------------------



if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False)
