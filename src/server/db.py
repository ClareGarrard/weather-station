import sqlite3

import click
from flask import current_app, g


def init_db():
    """Initialise empty SQL database. Will overwrite an existing database."""
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def get_db():
    """
    Connect to the application's configured database.

    The connection is unique for each request and will be reused if this is called again.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the connection."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def add_data(timestamp, temperature, pressure, humidity, air_quality, eCO2, co2):
    """Add data to database."""
    db = get_db()
    db.execute(
        "INSERT INTO weather (timestamp, temperature, pressure, humidity, air_quality, eCO2, co2)"
        " VALUES (?, ?, ?, ?, ?, ?, ?);",
        (timestamp, temperature, pressure, humidity, air_quality, eCO2, co2),
    )
    db.commit()


def retrieve_data(limit): 
    db = get_db()
    return db.execute(
        f"SELECT cast(timestamp as text) as timestamp, temperature, pressure, humidity, air_quality, eCO2"
        f" FROM weather"
        f" ORDER BY timestamp DESC"
        f" LIMIT {limit};"
    ).fetchall()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """
    Register database functions with the Flask app.

    This is called by the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
