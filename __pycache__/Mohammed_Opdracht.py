class Warenhuis:
    def __init__(self, naam, manager):
        self.naam = naam
        self.manager = manager

    def wijzigNaam(self, naam):
        print(f"Warenhuisnaam gewijzigd naar {naam}.")
        self.naam = naam

    def wijzigManager(self, manager):
        print(f"Warenhuis heeft een neiwe manager: {manager}.")
        self.manager = manager


class Werknemer:
    def __init__(self, nr, naam, salaris, standplaats, functie, adres):
        self.nr = nr
        self.naam = naam
        self.salaris = salaris
        self.standplaats = standplaats
        self.functie = functie
        self.adres = adres

    def uitdienst(self, nr):
        print(f"Werknemer {nr} is uit dienst.")

    def indienst(self, naam, salaris, standplaats, functie, adres):
        print(f"Nieuwe werknemer {naam} aangenomen met functie {functie} op {standplaats}.")

    def verhuizing(self, nr, adres):
        print(f"Werknemer {nr} heeft een neiwe adres {adres}.")
        self.adres = adres

    def salarismutatie(self, nr, salaris):
        print(f"Salaris van werknemer {nr} is nu {salaris}.")
        self.salaris = salaris



warenhuis = Warenhuis("Blokker","Manager A")

warenhuis.wijzigNaam("Blokker 2.0")
warenhuis.wijzigManager("The manager")


werknemer = Werknemer(1, "Jan Jan", 3500, "Amsterdam", "functie A", "Prinsengracht 1 Adam")
werknemer.indienst("Jan Jan2", 3000, "Rotterdam", "Developer", "Prinsengracht 12 Adam")

