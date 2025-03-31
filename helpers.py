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

if __name__ == '__main__':
    main()