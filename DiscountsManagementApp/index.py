from flask import render_template

from DiscountsManagementApp import app


@app.route("/")
def index():
    return render_template("home.html")