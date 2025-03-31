import csv
import sqlite3

def main():
    """
    Main function is used to create a table for lifetable data and insert them into the database.
    Pre-requisit:
        - lifetables sqlite3 database to be created
        - lifetable data to be stored in a csv file named lifetables
    """
    with open('lifetables.csv', mode='r') as file:
        reader = csv.DictReader(file)


if __name__ == '__main__':
    main()