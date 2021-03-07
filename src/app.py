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

import pandas as pd
import numpy as np

#------------------
# imort data

wine = pd.read_csv("src/data/wine_quality.csv")
wine['Taste'] = np.where(wine['quality']<6, 'Below average', (np.where(wine['quality']>6.5, 'Above average', 'Average')))

#---------------------
alt.data_transformers.enable("data_server")
app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
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


 # first plot   
@app.callback(
     Output('first_plot', 'srcDoc'),
     Input('xcol-widget', 'value')
     )
def plot_altair(xcol):
    chart= alt.Chart(wine).transform_density(
     'pH',
     groupby=['quality', 'Taste'],
     as_=['pH', 'density']).mark_area(opacity=0.4).encode(
     x='pH',
     y='density:Q',
     color='quality:N').properties(
     width=360,
     height=360
).configure_title(fontSize=18
).configure_axis(
    labelFontSize=12,
    titleFontSize=15
)
    return chart.to_html()


# second plot
@app.callback(
     Output('histgram','srcDoc'),
     Input('xcol-widget_2', 'value')
     )
def plot_altair_2(xcol):
    chart= alt.Chart(wine).mark_bar().encode(
    x=alt.X(xcol, type='quantitative', bin=alt.Bin(maxbins=30)),
    y=alt.Y('count()'),
    color='Taste').interactive()
    return chart.to_html()

# thrid plot
@app.callback(
     Output('third_plot','srcDoc'),
     Input('xcol-widget_3', 'value'),
     Input('ycol-widget', 'value')
     )

def plot_altair_3(xcol,ycol):
    select_quality = alt.selection_single(
    name='Select', fields=['quality'], init={'quality': 3.0},
    bind=alt.binding_range(min=3.0, max=9.0, step=1.0))

    chart= alt.Chart(wine,title=ycol+" VS "+xcol).mark_circle(opacity=0.5).encode(
        alt.X(xcol),
        alt.Y(ycol),
        alt.Size('chlorides in g/dm3'),
        alt.OpacityValue(0.5)).add_selection(select_quality).transform_filter(select_quality)
    
    return chart.to_html()

# fourth plot
@app.callback(
     Output('fourth_plot','srcDoc'),
     Input('xcol-widget_4', 'value'),
     Input('ycol-widget_4', 'value')
     )
def plot_altair_4(xcol,ycol):
    brush = alt.selection_interval()
    points = alt.Chart(wine,title="Interactive Plot of "+ ycol+" vs "+ xcol +" for 3 Quality Levels" ).mark_point().encode(
    alt.X(xcol, scale=alt.Scale(zero=False)),
    alt.Y(ycol, scale=alt.Scale(zero=False)),
    color=alt.condition(brush, 'Taste:N', alt.value('lightgray'))
).add_selection(brush).properties(height=300, width=600)
    
    bars = alt.Chart(wine,title="Count of Each Quality Level of Wines").mark_bar().encode(y='Taste:N',
                                                                                          color='Taste:N',
                                                                                          x='count(Taste):Q',tooltip='count(Taste):Q').transform_filter(brush).properties(height=150, width=600)
    return (points & bars).to_html()



##############------------eric---------

# Make scatterplot

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


################------------------------

if __name__ == "__main__":
    app.run_server(debug=True)