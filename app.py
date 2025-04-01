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
            anb, year = int(anb), int(year)
            premium, benefit, discount = float(premium), float(benefit), float(discount)
        except ValueError:
            return render_template("apv.html", years=years, error_msg='Except for sex, input should be numbers')
        
        if term == 'Whole Life':
            term = 101 - anb
        else:
            try:
                term = int(term)
            except ValueError:
                return render_template("apv.html", years=years, error_msg='Invalid term duration')

        table = get_life_table(year, sex)

        P_death_total = 0
        for age in range(len(table)):
            if table[age]['age_x'] < anb:
                # If your Age Next Birthday is bigger than the start of age_x
                # It means you have already survived this age
                table[age]['Px_death']        = 0.0
                table[age]['Px_survive']      = 1.0
                table[age]['Px1_Cum_survive'] = 1.0
                table[age]['E_benefit']       = 0.0
                table[age]['EPV_benefit']     = 0.0
                table[age]['Premium']         = 0.0
                table[age]['PV_premium']      = 0.0
            else:
                # If this is a future age
                # Px_death is the conditional probability of you dying between age x and x+1
                # Given that you already survived til age.
                # So it is = Cumulative probability to survive til age x * P dying between x & x+1
                table[age]['Px_death']        = table[age-1]['Px1_Cum_survive'] * table[age]['qx']
                # Your probability of surviving from x to x+1 given survival til x is just the compliment
                table[age]['Px_survive']      = 1 - table[age]['Px_death']
                # Your cumulative prob of surviving till x+1 is then Cum_prob_sur til x * surviving x to x+1
                table[age]['Px1_Cum_survive'] = table[age-1]['Px1_Cum_survive'] * table[age]['Px_survive']

                # When the term life is still active
                if table[age]['age_x'] < anb + term:
                    # EV of benefit is the benefit * P of dying between x & x+1
                    table[age]['E_benefit']   = table[age]['Px_death'] * benefit
                    # Assume benefit is always paid out End of the Year -> start & die at 24 anb, benefit discount 1 yr
                    table[age]['EPV_benefit'] = table[age]['E_benefit'] / (1 + discount) ** (table[age]['age_x'] - anb + 1)
                    table[age]['Premium']     = premium
                    # premium assumed to be paid Start of Year
                    table[age]['PV_premium']  = premium / (1 + discount) ** (table[age]['age_x'] - anb)
                else:
                    # Life insurance is not active anymore
                    table[age]['E_benefit']   = 0.0
                    table[age]['EPV_benefit'] = 0.0
                    table[age]['Premium']     = 0.0
                    table[age]['PV_premium']  = 0.0

            P_death_total += table[age]['Px_death']
        
        print(P_death_total)

        return render_template("apv.html", years=years, table=table, PdT=P_death_total)
    
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