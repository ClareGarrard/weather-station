from flask import Blueprint, render_template, request

from server.db import add_data, retrieve_data
from server.graphs import default_graph, easy_linegraph

bp = Blueprint("weather", __name__)


weather_dict = {
"humidity": "Humidity %",
"temperature": "Temperature C",
"pressure": "Pressure Pa",
"air_quality": "IAQ",
"eCO2": "eCO2 ppm",
"timestamp_unix_epoch": "Time",
}


@bp.route("/")
def index():
    latest_data = retrieve_data(limit=1)
    latest_data = [dict(row) for row in latest_data][0]
    return render_template("weather/index.html", latest_data=latest_data)


@bp.route("/legacy")
def legacy():
    latest_data = retrieve_data(limit=1)
    latest_data = [dict(row) for row in latest_data][0]
    return render_template("weather/legacy.html", latest_data=latest_data)


@bp.route("/visualise")
def visualise():
    latest_data = retrieve_data(limit=1)
    latest_data = [dict(row) for row in latest_data][0]
    return render_template("weather/visualise.html", easy_linegraph=easy_linegraph, latest_data=latest_data)


@bp.route("/explore", methods=("GET",))
def explore():
    measurement_x = request.args.get('measurement_x', default='timestamp_unix_epoch')
    weather_component_y = request.args.get('weather_component_y', default='humidity')
    time_period= request.args.get('time_period', default=72) # = 6hours (+- 12 readings/hr)
    latest_data = retrieve_data(limit=1)
    latest_data = [dict(row) for row in latest_data][0]
    return render_template("weather/explore.html", 
                            weather_graph_template=easy_linegraph(weather_component_y, weather_dict[weather_component_y], 
                                measurement_x, weather_dict[measurement_x], limit=int(time_period)),
                                latest_data=latest_data)


@bp.route("/analyse")
def analyse():
    return render_template("weather/analyse.html")


@bp.route("/about")
def about():
    return render_template("weather/about.html")


@bp.route("/data", methods=("POST",))
def post_data():
    data = request.get_json()
    print(data)
    add_data(
        data["timestamp"],
        data["temperature"],
        data["pressure"],
        data["humidity"],
        data["air_quality"],
        data["e_co2"],
        data.get("co2", None) # default=None
    )
    return "JSON received!"


@bp.route("/api/data", methods=("GET",))
def get_data():
    # Get the JSON data from the SQL database
    results = retrieve_data(1)
    results = dict(results[0])
    results["pressure"] /= 100  # convert pressure to millibars
    return results


@bp.route("/test_graph", methods=("GET",))
def display_graph():
    return default_graph()


@bp.route("/graph/<weather_component>")
def display_weather_data(weather_component):
    return easy_linegraph(weather_component, weather_dict[weather_component], limit=288)
