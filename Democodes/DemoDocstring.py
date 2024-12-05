import doctest

def hallo():
    """"
    Deze functie toont een hallo met een vraag over het weer.
    """
    print("Hallo")
    print("Hoe is het weer?")

def berekenSom(getal1, getal2):
    """
    Deze functie berekent de som van 2 getallen.
    :param getal1: Het 1e ingevoerde getal
    :param getal2: Het 2e ingevoerde getal
    :return:
    """
    return getal1 + getal2

hallo()

print(berekenSom(5,7))

doctest.testmod(verbose=True)