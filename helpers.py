import csv
import sqlite3

def main():
    """
    Main function is used to create a table for lifetable data and insert them into the database.
    Pre-requisit:
        - lifetables sqlite3 database to be created
        - lifetable data to be stored in a csv file named lifetables
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
        
    cursor.close()
    connection.close()

def get_available_years():
    """
    Return a list of the years with lifetable available
    """
    with sqlite3.connect('lifetables.db') as con:
        res = con.execute('SELECT DISTINCT year FROM lifetables ORDER BY year')
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
    
def calc_insurance_value(table, anb, term, benefit, discount, premium):
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
    
    val['anb'] = anb
    val['term'] = term
    val['benefit'] = benefit
    val['discount'] = discount
    val['premium'] = premium

    return table, val

if __name__ == '__main__':
    # main()
    pass
