# matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO

import pandas as pd
from matplotlib.figure import Figure

from server.db import retrieve_data

from threading import Lock

lock = Lock() 
# See https://stackoverflow.com/a/71527466 - preprocess graph with multiple threads but plot with single thread


def default_graph():
    """Plot simple test graph for use in development."""
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot([1, 2])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


def graph_data(limit): 
    """Retrieve data from database and returns as a df with time in unix epoch & ISO."""
    results = retrieve_data(limit)
    results = [dict(row) for row in results]
    df = pd.DataFrame(results)
    df["timestamp_unix_epoch"] = pd.to_datetime(df["timestamp"], format="mixed").map(
        pd.Timestamp.timestamp
    )
    return df


def easy_linegraph(weather_component_y, ylabel, measurement_x="timestamp_unix_epoch", xlabel="Time", limit=72): # 12 readings = ± 1hr if measured every 5 min 
    """Plot simple graph of weather component vs time."""
    df = graph_data(limit)
    plt.style.use('./server/eclipse.mplstyle')
    fig = Figure()
    ax = fig.subplots()
    ax.scatter(df[measurement_x], df[weather_component_y])
    if measurement_x=="timestamp_unix_epoch":
        ax.set_xticks(
                ticks=df[measurement_x][0::round(limit/5)], labels=df.timestamp[0::round(limit/5)], minor=False, rotation=90
            )
    if measurement_x=="pressure":
        # pressure readings very long, so rotate labels
        ax.set_xticks(
                ticks=df[measurement_x][0::], labels=df[measurement_x][0::], rotation=90
            )
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    buf = BytesIO()
    fig.tight_layout()
    lock.acquire()
    fig.savefig(buf, format="png")
    lock.release()
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"
