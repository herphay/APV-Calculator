import csv

def main():
    with open('lifetable.csv', mode='r') as file:
        reader = csv.DictReader(file)
