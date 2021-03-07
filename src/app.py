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



#wine = pd.read_csv("src/data/wine_quality.csv")
#wine['Taste'] = np.where(wine['quality']<6, 'Below average', (np.where(wine['quality']>6.5, 'Above average', 'Average')))

#-------------------------eric data cleaning
## Allow large data set
alt.data_transformers.enable('data_server')


# Correlation Data
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



#-----------------------------


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


 # first plot   Luka
@app.callback(
     Output('first_plot', 'srcDoc'),
     Input('xcol-widget', 'value'))
def plot_altair(xcol):
    units = {'Fixed Acidity':'(g/dm3)', 'Volatile Acidity':'(g/dm3)', 'Citric Acid':'(g/dm3)',
             'Residual Sugar':'(g/dm3)', 'Chlorides':'(g/dm3)', 'Density':'(g/dm3)', 'Sulphates':'(g/dm3)',
             'Free Sulfur Dioxide':'(mg/dm3)', 'Total Sulfur Dioxide':'(mg/dm3)', 'Alcohol':'(%vol)', 'pH':''}
    chart = alt.Chart(wine
            ).transform_density(
                density=xcol,
                groupby=['type', 'quality_factor'],
                as_=['value', 'density'],
                steps=200, # bandwidth=5
            ).mark_area(opacity=0.6).encode(
                alt.X('value:Q', title=str(xcol+' '+units[xcol]), axis=alt.Axis(labels=True, grid=True)),
                alt.Y('density:Q', title=None, axis=alt.Axis(labels=False, grid=False, ticks=False)),
                alt.Color('type', scale=alt.Scale(range=['darkred', '#ff9581'])),
                alt.Facet('quality_factor:N', columns = 1)
            ).properties(
                #height=200, width=400,
                title = alt.TitleParams(
                text='Wine Quality Factor Distributions', 
                align='left', fontSize=14,
                subtitle='Reds and Whites superimposed', subtitleFontSize=12)
            ).configure_view(stroke=None).configure_headerFacet(title=None, labelAlign='right', labelAnchor='end', labelFontWeight=600, labelFontSize=12).interactive()
    
    return chart.to_html()
###################################

# Set up callbacks/backend
# @app.callback(
#      Output('scatter','srcDoc'),
#      Input('xcol-widget', 'value'),
#      Input('ycol-widget', 'value'),
#      Input("winetype", "value")
#      )

# def plot_scatter(xcol,ycol, winetype):

#     wine_dif = wine.loc[(wine['type'].isin(winetype))]

#     brush = alt.selection_interval()
#     click = alt.selection_multi(fields=['type'], bind='legend')

#     base = alt.Chart(wine_dif).properties(
#     width=400,
#     height=400
#     ).add_selection(brush)

#     points = base.mark_point().encode(
#     x = alt.X(xcol, scale=alt.Scale(zero=False)),
#     y = alt.Y(ycol, scale=alt.Scale(zero=False)),
#     color=alt.condition(brush, 'quality_factor:N', alt.value('lightgray')),
#     opacity=alt.condition(click, alt.value(0.9), alt.value(0.2))
#     )
    
#     bars = alt.Chart(wine_dif, title="Percentage of Each Quality Factor").transform_joinaggregate(
#     total='count(*)'
#     ).transform_calculate(
#     pct='1 / datum.total'
#     ).mark_bar().encode(
#     alt.X('sum(pct):Q', axis=alt.Axis(format='%')),
#     alt.Y('quality_factor:N'),
#     color = 'quality_factor:N',
#     tooltip = 'count(quality_factor):Q'
#     ).transform_filter(brush)

#     hists = base.mark_bar(opacity=0.5, thickness=100).encode(
#     x=alt.X('quality',
#             bin=alt.Bin(step=1), # step keeps bin size the same
#             scale=alt.Scale(zero=False)),
#     y=alt.Y('count()',
#             stack=None),
#     color=alt.Color('quality_factor:N'),
#     tooltip = 'count(quality):Q'
#     ).transform_filter(brush)
    
#     chart = (points & bars | hists).add_selection(click)
#     return chart.to_html()



####################
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


    
    
if __name__ == '__main__':
    app.run_server(debug=True,dev_tools_ui=False,dev_tools_props_check=False)
