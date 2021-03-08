import dash_html_components as html
import dash_core_components as dcc


def Header(app):
    return html.Div([get_header(app), html.Br([]), get_menu()])


def get_header(app):
    header = html.Div(
        [html.Div(
                [html.Img(
                        src=app.get_asset_url("logo.png"),
                        className="logo",
                    )
                ],
                className="row",
            ),
            html.Div(
                [html.Div(
                        [html.H2("WineVision Dashboard")],
                        className="seven columns main-title",
                    ),
                    html.Div(
                        [dcc.Link(
                                "Introduction",
                                href="/WineVison/src/full-view",
                                className="full-view-link",
                            )
                        ],
                        className="five columns",
                    ),
                ],
                className="twelve columns",
                #style={"padding-left": "1"},
            ),
        ],
        className="row",
    )
    return header


def get_menu():
    menu = html.Div(
        [dcc.Link(
                "Overview",
                href="/WineVison/src/overview",
                className="tab first",
            ),
            dcc.Link(
                "Wine Type Comparison",
                href="/WineVison/src/Wine_type",
                className="tab",
            ),
            dcc.Link(
                "Quality Factors",
                href="/WineVison/src/qf",
                className="tab",
            ),
        ],
        className="row all-tabs",
    )
    return menu

def make_dash_table(df):
    """ Return a dash definition of an HTML table for a Pandas dataframe """
    table = []
    for index, row in df.iterrows():
        html_row = []
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table
