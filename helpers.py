import csv
import sqlite3

def main():
    """
    Main function is first used to create a table for lifetable data and insert them into the database.
    Pre-requisit:
        - lifetables sqlite3 database to be created
        - lifetable data to be stored in a csv file named lifetables

    Then it will create another table 'plans' for storage of insurance plans to be compared
    """
    # Start connection to lifetables.db and create cursor object
    connection = sqlite3.connect('lifetables.db')
    cursor = connection.cursor()

    # As we are loading in new data, drop whatever existing data there are
    cursor.execute("DROP TABLE IF EXISTS lifetables")

    # Create a new lifetables table and commit the udpate
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lifetables (
            year INTEGER,
            sex TEXT,
            age_x INTEGER,
            qx FLOAT,
            lx INTEGER,
            dx INTEGER,
            upcase_lx INTEGER,
            upcase_tx INTEGER,
            ex FLOAT
            );
    """)
    connection.commit()

    with open('lifetables.csv', mode='r') as file:
        reader = csv.reader(file)
        header = next(reader)

        # create a list of tuples with all data converted to desired dtype for insertion
        data = [(int(r[0]),               r[1],              100 if 'and' in r[2] else int(r[2]), 
                 (d := int(r[5])) / (l := int(r[4])),   l,   d,
                 int(r[6]),               int(r[7]),         float(r[8]))
                for r in reader]

        try:
            cursor.execute("BEGIN TRANSACTION")
            cursor.executemany("INSERT INTO lifetables VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", data)
            connection.commit()
        except:
            print('Data insertion error, please check that your datatypes are proepr')
            return 1
        
    cursor.execute("DROP TABLE IF EXISTS plans")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            plan TEXT,
            sex TEXT,
            year INTEGER,
            anb INTEGER,
            term INTEGER,
            benefit FLOAT,
            discount FLOAT,
            premium FLOAT,
            apv FLOAT,
            ppv FLOAT,
            ratio FLOAT
            )
    """)
        
    connection.commit()

    cursor.close()
    connection.close()

def get_available_years():
    """
    Return a list of the years with lifetable available
    """
    with sqlite3.connect('lifetables.db') as con:
        res = con.execute('SELECT DISTINCT year FROM lifetables ORDER BY year')

        # sqlite result is always a list of tuples, where each tuple is the data
        # for each result row. 
        return [row[0] for row in res.fetchall()]

def get_life_table(year, sex):
    """
    Return life table of a specific year 
    """
    with sqlite3.connect('lifetables.db') as con:
        res = con.execute("""
                SELECT year,
                       sex,
                       age_x,
                       qx,
                       lx,
                       dx,
                       ex
                FROM lifetables
                WHERE year = ?
                AND sex = ?
                ORDER BY age_x
        """, (year, sex))
        cols = [col[0] for col in res.description]
        table = [{k:v for k, v in zip(cols, row)} for row in res.fetchall()]
        return table
    
def calc_insurance_value(year, sex, anb, term, benefit, discount, premium):
    table = get_life_table(year, sex)
    val = {'apv': 0, 'ppv': 0}
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
            # Px_death is the conditional probability of you dying between age x and x+1 given you live til anb
            # Given that you already survived til age anb.
            # So it is = Cumulative probability to survive til age x * P dying between x & x+1
            table[age]['Px_death']        = table[age-1]['Px1_Cum_survive'] * table[age]['qx']
            # Your probability of surviving from x to x+1 given survival til x is just the compliment
            table[age]['Px_survive']      = 1 - table[age]['qx']
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

        val['apv'] += table[age]['EPV_benefit']
        val['ppv'] += table[age]['PV_premium']
    
    val['year'] = year
    val['sex']  = sex
    val['anb'] = anb
    val['term'] = term
    val['benefit'] = benefit
    val['discount'] = discount
    val['premium'] = premium

    return table, val

def add_plan(plandata):
    con = sqlite3.connect('lifetables.db')
    cur = con.cursor()

    existing_plans = cur.execute("SELECT DISTINCT plan FROM plans")
    existing_plans = [row[0] for row in existing_plans.fetchall()]

    if plandata['plan'] in existing_plans:
        return 1

    plandata['year']     = int(plandata['year'])
    plandata['anb']      = int(plandata['anb'])
    plandata['term']     = int(plandata['term'])
    plandata['benefit']  = float(plandata['benefit'])
    plandata['discount'] = float(plandata['discount'])
    plandata['premium']  = float(plandata['premium'])
    plandata['apv']      = float(plandata['apv'])
    plandata['ppv']      = float(plandata['ppv'])
    plandata['ratio']    = plandata['apv'] / plandata['ppv']

    cur.execute("""
        INSERT INTO plans VALUES (
            :plan, :sex, :year, :anb, :term, :benefit, 
            :discount, :premium, :apv, :ppv, :ratio)""", plandata)
    
    con.commit()

    cur.close()
    con.close()

    return 0

def get_plans():
    con = sqlite3.connect('lifetables.db')
    cur = con.cursor()

    cur.execute("SELECT * FROM plans ORDER BY ratio DESC")

    cols = [col[0] for col in cur.description]
    plans = [{k:v for k, v in zip(cols, row)} for row in cur.fetchall()]

    return plans

if __name__ == '__main__':
    main()
