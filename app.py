from flask import Flask, render_template, request, jsonify
from helpers import get_available_years, get_life_table, calc_insurance_value
from helpers import add_plan, get_plans, get_table_for_apv

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
        val, table, error_msg = get_table_for_apv(request.form)
        if error_msg:
            return render_template("apv.html", years=years, error_msg=error_msg)
        else:
            return render_template("apv.html", years=years, table=table, val=val)
    
    elif request.method == 'GET':
        val, table, error_msg = get_table_for_apv(request.args)
        if error_msg:
            return render_template("apv.html", years=years, error_msg=error_msg)
        else:
            return render_template("apv.html", years=years, table=table, val=val)
    
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
        msg = f'This is the life table for {sex} with the reference year {year}.'

        return render_template("tables.html", years=years, table=table, msg=msg)
    
    return render_template("tables.html", years=years)

@app.route("/compare")
def compare():
    plans = get_plans()
    return render_template("compare.html", plans=plans)

@app.route("/save_plan", methods=['POST'])
def save_plan():
    data = request.get_json()
    try:
        result = add_plan(data)
    except:
        return jsonify({'result':"Failed to add plan"})
    
    if result == 0:
        return jsonify({'result':"Plan successfully added for comparison"})
    else:
        return jsonify({'result':"Plan name already exists"})