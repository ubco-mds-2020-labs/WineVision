dbc.Container([
    html.H1('Various Features in Different Quality Factors'),
    dbc.Row([
        dbc.Col([
            dbc.Card(
                dbc.CardBody(html.H3('Wine Type', className = 'wine-type'),
                html.P('You can select either type or both', className = 'wine-type')),
                color='info'),

            dcc.Checklist(
                id = "winetype",
                options = [
                    {"label": "White Wine", "value": "white"},
                    {"label": "Red Wine", "value": "red"}
                ],
                value = ["red", "white"],
                labelStyle={"display": "block"}
            )
        ]),
        dbc.Col([
            html.H3('Select your variables:'),

            html.H4('X-axis'),
            
            # dcc.Dropdown(
            #     id = "type-widget",
            #     options=[
            #         {'label': 'White', 'value': 'white'},
            #         {'label': 'Red', 'value': 'red'}],
            #     value='white', placeholder = "Select Wine Type"),
            dcc.Dropdown(
                id='xcol-widget',
                value='pH',
                options=[{'label': col, 'value': col} for col in wine.columns],
                clearable = False
                ),

            html.H4("Y-axis"),

            dcc.Dropdown(
                id='ycol-widget',
                value='pH',
                options=[{'label': col, 'value': col} for col in wine.columns],
                clearable = False
                ),
        ]),

        html.Iframe(
            id = "scatter",
            # srcDoc = plot_scatter(),
            style={'border-width': '0', 'width': '120%', 'height': '700px'})

    ])
])
