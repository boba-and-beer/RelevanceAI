import dash
from dash import dcc
from dash import html
from relevanceai.visualise.dash_components.components.sections import Card

def build_display_panel(app: dash.Dash) -> html.Div:
    '''
    Builds the display panel.
    '''
    return html.Div(
        className='three columns',
        id='display-panel',
        children=[
                Card(
                    style={'padding': '5px'},
                    children=[html.Div(
                            id='div-plot-click-message',
                            style={
                                'text-align': 'center',
                                'margin-bottom': '7px',
                                'font-weight': 'bold',
                            },
                        ),
                        html.Div(id='div-plot-click-image',
                                 style={
                                    'text-align': 'center',
                                    # 'display': 'inline-block',
                                 }),
                    ],
                ), 

                Card(
                    style={'width': '98vh', 'textwd-align': 'center'},
                    children=[
                        html.Div(id='div-plot-click-neighbours')
                    ],
                )  
            ],
    )