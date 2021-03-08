import numpy as np
import pandas as pd
import altair as alt

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from utils import Header, make_dash_table

# temporary filler for app testing
def create_layout(app):
    # Page layouts
    return html.Div(    
        [html.Div([Header(app)]),
            # page 1
            html.Div(
                [# Row 3
                    html.Div(
                        [html.H3('Modelling'),
                            html.Br([]),
                            html.P(
                                "\
                                This is a temporary tab filler for modelling so modelling.create_layout is defined when running app.py",
                                    style={'color':"#FFFFFF"},
                                     className="row",  
                                ),
                        ],
                        className="product"
                    )
                    
                ],
            ),    
                
        ],
        className="page",
    )