from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/apv")
def apv():
    return render_template("apv.html")

@app.route("/tables")
def tables():
    return render_template("tables.html")

@app.route("/compare")
def compare():
    return render_template("compare.html")