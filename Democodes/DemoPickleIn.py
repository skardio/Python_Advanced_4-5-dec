import pickle

class Dier:

    def __init__(self, naam, grootte, geslacht, leeftijd):
        self.__naam = naam
        self.__grootte = grootte
        self.__geslacht = geslacht
        self.__leeftijd = leeftijd

    def maaktGeluid(self):
        print(self.__naam, "maakt geluid")

    def jaagt(self):
        print(self.__naam, "jaagt op muizen.")

    def info(self):
        return "{} {} {} {}".format(self.__naam, self.__grootte, self.__geslacht, self.__leeftijd)

infile = open("data100.dat", "rb")

d1 = pickle.load(infile)
d2 = pickle.load(infile)


infile.close()

print(d1.info())
print(d2.info())
