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

@app.route("/apv", methods=['GET', 'POST'])
def apv():
    years = get_available_years()
    years.sort()

    if request.method == 'POST':
        sex = request.form.get('sex')
        anb = request.form.get('anb')
        term = request.form.get('term')
        year = request.form.get('year')
        premium = request.form.get('premium')
        benefit = request.form.get('benefit')
        discount = request.form.get('discount')

        if sex not in ['Male', 'Female'] or not anb or not term or \
           not year or not premium or not benefit or not discount:
            return render_template("apv.html", years=years, error_msg='Missing input')
        
        try:
            anb, term, year = int(anb), int(term), int(year)
            premium, benefit, discount = float(premium), float(benefit), float(discount)
        except ValueError:
            return render_template("apv.html", years=years, error_msg='Except for sex, input should be numbers')
        
        table = get_life_table(year, sex)

        return render_template("apv.html", years=years)
    
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