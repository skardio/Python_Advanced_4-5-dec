from datetime import datetime

input_format = '%d-%m-%Y'
output_format = '%d %B %Y'

user_input = input('Geef een datum: ')

try:
    d = datetime.strptime(user_input, input_format)

    print(d.strftime(output_format))

except ValueError:
    print('Dat is geen geldige datum.')