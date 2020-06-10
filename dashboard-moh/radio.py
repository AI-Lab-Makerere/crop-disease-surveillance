# Import required libraries
import pickle
import copy
import pathlib
import dash
import plotly.graph_objects as go
import math
import datetime as dt
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as da
# Multi-dropdown options
from controls import TIMESCALE,KEYWORDS
import plotly.express as px
import speech_recognition as sr
from pydub import AudioSegment

# get relative data folder
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# Create controls
keyword_options = [
    {"label": str(KEYWORDS[key_words]), "value": str(key_words)}
    for key_words in KEYWORDS
]

time_options = [
    {"label": str(TIMESCALE[time_scale]), "value": str(time_scale)}
    for time_scale in TIMESCALE
]


# Load data
df = pd.read_csv(DATA_PATH.joinpath("radio.csv"), low_memory=False)


dd = pd.read_csv(DATA_PATH.joinpath("rad.csv"), low_memory=False)
dmap = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')

fig = go.Figure(data=go.Choropleth(
    locations=dmap['code'], # Spatial coordinates
    z = dmap['total exports'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Keyword Mentions",
))

fig.update_layout(
    title_text = 'June 11th 2020  COVID-19 conversations',
    geo_scope='africa', # limite map scope to USA
)



PATH = "assets/1.mp3"
#PATH = "assets/pmoney.mp3"
podcast = AudioSegment.from_mp3(PATH)
PODCAST_LENGTH = podcast.duration_seconds
PODCAST_INTERVAL = 5000

app = dash.Dash(__name__)
server = app.server


def seconds_to_MMSS(slider_seconds):
    decimal, minutes = math.modf(slider_seconds / 60.0)
    seconds = str(round(decimal * 60.0))
    if len(seconds) == 1:
        seconds = "0" + seconds
    MMSS = "{0}:{1}".format(round(minutes), seconds)
    return MMSS


def generate_plot(step=1):
    print(PODCAST_INTERVAL * step, PODCAST_INTERVAL * (step + 1))
    # 5 second interval of podcast
    seg = podcast[PODCAST_INTERVAL * step: PODCAST_INTERVAL * (step + 1)]
    samples = seg.get_array_of_samples()
    arr = np.array(samples)
    dff = pd.DataFrame(arr)
    figg = px.line(dff, x=dff.index, y=0, render_mode="webgl")
    figg.update_layout(
        height=250,
        margin_r=0,
        margin_l=0,
        margin_t=0,
        yaxis_title="",
        yaxis_fixedrange=True,
    )

    # Set custom x-axis labels
    figg.update_xaxes(
        ticktext=[seconds_to_MMSS(i + step * 5) for i in range(6)],
        tickvals=[i * 100000 for i in range(6)],
        tickmode="array",
        title="",
    )

    return figg


figg = generate_plot()


# Create app layout
app.layout = html.Div(
    [
        #dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        #html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("moh.png"),
                            id="plotly-image",
                            style={
                                "height": "180px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "COVID-19 Analysis",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Overview of the Voices from the Public", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("View Details", id="learn-more-button"),
                            href="#",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Select by Date:",
                            className="control_label",
                        ),
                        dcc.DatePickerSingle(
                            id='stream-date',
                            min_date_allowed=da(2020, 6, 1),
                            max_date_allowed=da(2020, 6, 7),
                            initial_visible_month=da(2020, 6, 1),
                            date=str(da(2020, 6, 25, 23, 59, 59)),
                            className="dcc_control",
                            ),

                        html.P("Filter by Keywords:", className="control_label"),
                        dcc.RadioItems(
                            id="keywords_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="key_words",
                            options=keyword_options,
                            multi=True,
                            value=list(KEYWORDS.keys()),
                            className="dcc_control",
                        ),
                        html.P("Filter by Time Frame:", className="control_label"),
                        dcc.RadioItems(
                            id="timescale_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Customize ", "value": "custom"},
                            ],
                            value="all",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="time_scale",
                            options=time_options,
                            multi=True,
                            value=list(TIMESCALE.keys()),
                            className="dcc_control",
                        ),

                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="hits"), html.P("No. of hits")],
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="keywords"), html.P("Active keywords")],
                                    className="mini_container",
                                ),

                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="count_graph",
                                    figure={
                                        'data': [
                                            {'x': dd.time, 'y': dd.counts, 'type': 'bar'}
                                        ],
                                        'layout': {
                                            'title': 'Daily Hits',
                                            'xaxis':{'title': 'Keyword'},
                                            'yaxis': {'title': 'Time'},
                                            'height': 3000,

                                        }
                                    }

                            )],
                            id="countGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="main_graph",figure=fig)],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [
                        #dcc.Textarea(id="transcription_output", cols=80),
                        html.Br(),
                        html.Audio(id="player", src=PATH,controls=True, style={
                            "width": "100%"
                        }),html.P(id="kwd"),
                        dcc.Graph(id="waveform", figure=figg),

                    ],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),

    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)








# Create callbacks
# app.clientside_callback(
#     ClientsideFunction(namespace="clientside", function_name="resize"),
#     Output("output-clientside", "children"),
#     [Input("count_graph", "figure")],
# )




# Radio -> multi
@app.callback(
    Output("key_words", "value"), [Input("keywords_selector", "value")]
)
def display_status(selector):
    if selector == "all":
        return list(KEYWORDS.keys())
    elif selector == "custom":
        return ["CD", "CA", "LA", "SS", "AK"]
    else:
        return []


# Radio -> multi
@app.callback(Output("time_scale", "value"), [Input("timescale_selector", "value")])
def display_type(selector):
    if selector == "all":
        return list(TIMESCALE.keys())
    elif selector == "custom":
        return ["MO", "BK", "LM", "MD", "AN", "LN", "EV", "LE","MN"]
    return []





# # Selectors -> main graph
# @app.callback(
#     Output("count_graph", "figure"),
#     [
#         Input("key_words", "value"),
#         Input("time_scale", "value"),
#         Input("stream-date", "value"),
#     ],)
# def make_main_figure(key_words, time_scale, stream_date):
#
#     return 0
#
#
#
#
# # Selectors -> well text
@app.callback(
    [Output("hits", "children"),Output("keywords", "children")],
    [
        Input("key_words", "value"),
        Input("time_scale", "value"),
        Input("stream-date", "date"),
    ],
)
def update_summary(key_words, time_scale,stream):

    return [len(df),len(df.groupby(['keyword']))]


# @app.callback(
#     [Output("player", "children"),Output("kwd", "children")],
#     [
#         Input("timescale_selector", "value"),
#         Input("keywords_selector", "value"),
#         Input("stream-date", "date"),
#     ],
# )
# def playlist(time_scale,keyword,stream):
#     if time_scale == "all" and keyword == "all":
#         df["date"] = pd.to_datetime(df["date"])
#         sm=df['start'].value_counts()
#         same=pd.DataFrame(sm)
#
#         return list(TIMESCALE.keys())







# Main
if __name__ == "__main__":
    app.run_server(debug=True)
