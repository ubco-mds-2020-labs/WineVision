# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import altair as alt

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output
<<<<<<< HEAD
from pages import (intergraph, overview, modelling)
=======
<<<<<<< HEAD:.ipynb_checkpoints/app-checkpoint.py
from src.pages import (
    intergraph,
    overview
)
import src.utils
>>>>>>> main

#------------------
# imort data

<<<<<<< HEAD
wine = pd.read_csv("wine_quality.csv")
=======
wine = pd.read_csv("src/data/wine_quality.csv")
=======
from pages import (intergraph, overview, modelling)
import utils
#------------------
# import data
wine = pd.read_csv("wine_quality.csv")
>>>>>>> main:src/app.py
>>>>>>> main
alt.data_transformers.enable('csv')

#---------------------

app = dash.Dash(
<<<<<<< HEAD
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
=======
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=["https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap-grid.min.css"]
>>>>>>> main
)
server = app.server

# Describe the layout/ UI of the app
app.layout = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

#Update page
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
    units = {'Fixed Acidity':'(g/dm3)', 'Volatile Acidity':'(g/dm3)', 'Citric Acid':'(g/dm3)',
             'Residual Sugar':'(g/dm3)', 'Chlorides':'(g/dm3)', 'Density':'(g/dm3)', 'Sulphates':'(g/dm3)',
             'Free Sulfur Dioxide':'(mg/dm3)', 'Total Sulfur Dioxide':'(mg/dm3)', 'Alcohol':'(%vol)', 'pH':''}
    chart = alt.Chart(wine
            ).transform_density(
                density=xcol,
                groupby=['Wine', 'Quality_Factor'],
                as_=['value', 'density'],
                steps=200, # bandwidth=5
            ).mark_area(opacity=0.6).encode(
                alt.X('value:Q', title=str(xcol+' '+units[xcol]), axis=alt.Axis(labels=True, grid=True)),
                alt.Y('density:Q', title=None, axis=alt.Axis(labels=False, grid=False, ticks=False)),
                alt.Color('Wine', scale=alt.Scale(range=['darkred', '#ff9581'])),
                alt.Facet('Quality_Factor:N', columns = 1)
            ).properties(
                #height=200, width=400,
                title = alt.TitleParams(
                text='Wine Quality Factor Distributions', 
                align='left', fontSize=14,
                subtitle='Reds and Whites superimposed', subtitleFontSize=12)
            ).configure_view(stroke=None).configure_headerFacet(title=None, labelAlign='right', labelAnchor='end', labelFontWeight=600, labelFontSize=12).interactive()
    
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
<<<<<<< HEAD
)
=======
<<<<<<< HEAD:.ipynb_checkpoints/app-checkpoint.py
)
=======
     )


>>>>>>> main:src/app.py
>>>>>>> main
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