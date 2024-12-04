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

toine = Dier("Toine", 1.80, 'M', 63)
edwin = Dier("Edwin", 1.70, 'M', 60)
martijn = Dier("Martijn", 2, "M", 42)

lstDieren = []
lstDieren.append(toine)
lstDieren.append(edwin)
lstDieren.append(martijn)

print(martijn.info())
print(toine.info())
print(edwin.info())

edwin.jaagt()
toine.maaktGeluid()
edwin.jaagt()

print(lstDieren[0].info())

toine.__naam = "Tonie"

print(lstDieren[0].info())
print(toine.__naam)