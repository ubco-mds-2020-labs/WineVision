# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import altair as alt

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
from src.pages import (
    intergraph,
    overview
)

#------------------
# imort data

wine = pd.read_csv("src/data/wine_quality.csv")

#---------------------

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
     groupby=['quality', 'final_quality'],
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
    color='final_quality').interactive()
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
    color=alt.condition(brush, 'final_quality:N', alt.value('lightgray'))
).add_selection(brush).properties(height=300, width=600)
    
    bars = alt.Chart(wine,title="Count of Each Quality Level of Wines").mark_bar().encode(y='final_quality:N',
                                                                                          color='final_quality:N',
                                                                                          x='count(final_quality):Q',tooltip='count(final_quality):Q').transform_filter(brush).properties(height=150, width=600)
    return (points & bars).to_html()


if __name__ == "__main__":
    app.run_server(debug=True)