from flask import Flask, render_template, request, jsonify
from helpers import get_available_years, get_life_table

app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=['GET', 'POST'])
def index():
    
    return render_template("index.html")

@app.route("/apv")
def apv():
    years = get_available_years()
    years.sort()
    return render_template("apv.html", years=years)

@app.route("/tables", methods=['POST', 'GET'])
def tables():
    years = get_available_years()
    years.sort()

    if request.method == 'POST':
        year = request.form.get('year')
        sex  = request.form.get('sex')
        if year not in years or not sex:
            render_template("tables.html", years=years)

        table = get_life_table(year, sex)
        msg = f'This is the life table for {sex} for the reference year {year}.'

        return render_template("tables.html", years=years, table=table, msg=msg)
    
    return render_template("tables.html", years=years)

@app.route("/compare")
def compare():
    return render_template("compare.html")