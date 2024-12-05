import datetime

datum = datetime.date(2021, 12,9)

datumVandaag = datum.strftime("%d-%m-%Y")

print(datumVandaag)