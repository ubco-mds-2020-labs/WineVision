@app.callback(
     Output('scatter','srcDoc'),
     Input('xcol-widget', 'value'),
     Input('ycol-widget', 'value'),
     Input("winetype", "value")
     )

def plot_scatter(xcol,ycol, winetype):

    wine_dif = wine.loc[(wine['type'].isin(winetype))]

    brush = alt.selection_interval()
    click = alt.selection_multi(fields=['type'], bind='legend')

    base = alt.Chart(wine_dif).properties(
    width=400,
    height=400
    ).add_selection(brush)

    points = base.mark_point().encode(
    x = alt.X(xcol, scale=alt.Scale(zero=False)),
    y = alt.Y(ycol, scale=alt.Scale(zero=False)),
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
    color = 'quality_factor:N',
    tooltip = 'count(quality_factor):Q'
    ).transform_filter(brush)

    hists = base.mark_bar(opacity=0.5, thickness=100).encode(
    x=alt.X('quality',
            bin=alt.Bin(step=1), # step keeps bin size the same
            scale=alt.Scale(zero=False)),
    y=alt.Y('count()',
            stack=None),
    color=alt.Color('quality_factor:N'),
    tooltip = 'count(quality):Q'
    ).transform_filter(brush)
    
    chart = (points & bars | hists).add_selection(click)
    return chart.to_html()