
@app.callback(
     Output('first_plot', 'srcDoc'),
     Input('xcol-widget', 'value')
)
def plot_altair(xcol):
        
    chart = alt.Chart(wine
            ).transform_density(
                density=factor,
                groupby=['Wine', 'Quality Factor'],
                as_=['value', 'density'],
                steps=200, # bandwidth=5
            ).mark_area(opacity=0.5).encode(
                alt.X('value:Q', title=factor, axis=alt.Axis(labels=True, grid=True)),
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
