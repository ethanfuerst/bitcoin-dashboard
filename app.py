import datetime
import os

import pandas as pd
import plotly.graph_objs as go
import requests
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ["api_key"]


def get_new_data():
    url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey={API_KEY}"
    request = requests.get(url)
    df = pd.DataFrame.from_dict(
        request.json()["Time Series (Digital Currency Daily)"], orient="index"
    )
    df["Date"] = pd.to_datetime(df.index)
    df = df.reset_index(drop=True).copy()
    df.columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Date",
    ]
    df[["Open", "High", "Low", "Close", "Volume"]] = (
        df[["Open", "High", "Low", "Close", "Volume"]].astype(float).round(2).copy()
    )
    return df[["Open", "High", "Low", "Close", "Volume", "Date"]].copy()


app = Dash(
    __name__,
    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
)
server = app.server

df = get_new_data()

app.layout = html.Div(
    [
        html.Center(
            [
                html.H1(children="$BTC price in USD", style={"textAlign": "center"}),
                html.H2(children="All times in UTC", style={"textAlign": "center"}),
            ]
        ),
        html.Center([html.Div([dcc.Graph(id="graph")])]),
        html.Center(
            [
                dcc.RadioItems(
                    id="time_period",
                    options=[
                        {"label": "1 Day", "value": "1d"},
                        {"label": "1 Week", "value": "1w"},
                        {"label": "1 Month", "value": "1m"},
                        {"label": "3 Months", "value": "3m"},
                        {"label": "6 Months", "value": "6m"},
                        {"label": "Year To Date", "value": "ytd"},
                    ],
                    value="6m",
                    labelStyle={"display": "inline-block", "textAlign": "center"},
                ),
            ]
        ),
    ]
)


@app.callback(Output("graph", "figure"), [Input("time_period", "value")])
def update_graph(time_period):
    if time_period == "ytd":
        filtered_df = df[df["Date"].dt.year == datetime.datetime.today().year].copy()
    else:
        dates = {
            "1d": {"days": 0},
            "1w": {"weeks": 1},
            "1m": {"months": 1},
            "3m": {"months": 3},
            "6m": {"months": 6},
        }

        filter_date = datetime.datetime.today() - relativedelta(**dates[time_period])
        filtered_df = df[df["Date"] >= filter_date].copy()

    fig = go.Figure(
        go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
        )
    )

    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        plot_bgcolor="#cccccc",
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
