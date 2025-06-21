import csv

with open("orders.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(int(row[1]))