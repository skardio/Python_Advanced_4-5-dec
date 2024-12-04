class Auto:

    kleur = "Rood"

    def __init__(self, name, type):
        self.__name = name
        self.__type = type
        self.__velocity = 0
        self.__aantaldeuren = 5

    def start(self, velocity = 50):
        self.__velocity = velocity

    def geefNaam(self):
        return self.__name

    def geefSnelheid(self):
        return "Auto \"" + self.__name + "\" is gestart."

    def geefAantalDeuren(self):
        return self.__aantaldeuren

calvinauto = Auto("Calvin Auto", "A3")
martijnauto = Auto("Martijn Auto", "Ford")

#calvinauto.start()
#print(calvinauto.geefSnelheid())


print("martijnauto:", martijnauto.geefNaam())
print("calvinauto:", calvinauto.geefNaam())

print("martijnauto:",martijnauto.kleur)
print("calvinauto:",calvinauto.kleur)

martijnauto.kleur = "Geel"

print("martijnauto:",martijnauto.kleur)
print("calvinauto:",calvinauto.kleur)

Auto.kleur = "Blauw"

print("martijnauto:",martijnauto.kleur)
print("calvinauto:",calvinauto.kleur)
print("Auto:", Auto.kleur)