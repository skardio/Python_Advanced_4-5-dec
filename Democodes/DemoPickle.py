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

dier1 = Dier("Jan Klaasen", 1.8, "M", 100)
dier2 = Dier("Griet Jansen", 1.5, "V", 80)

outfile = open("data100.dat", "wb")

pickle.dump(dier1, outfile)
pickle.dump(dier2, outfile)


outfile.close()