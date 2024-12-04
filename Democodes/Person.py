class Person:

    residence = "Harderwijk"

    __slots__ = ("__name", "__residence")

    def __init__(self, name, residence):
        self.__name = name
        self.__residence = residence

    def tell(self):
        return "I am {}  and I live in {}.".format(self.__name, self.__residence)

    def move(self, new_residence):
        self.__residence = new_residence

    def __str__(self):
        return "name: " + self.__name + " - " + "residence: " + self.__residence


p = Person("Albert", "Amsterdam")
print(p.tell())
p.move("Eindhoven")
print(p.tell())

print("Class Person Residence:", p.residence)
print("Class Person Residence:", Person.residence)
print(p)

p2 = Person("Laura", "Nijmegen")
print(p2.tell())

lstPersons = []
lstPersons.append(p)
lstPersons.append(p2)

print("p:", hex(id(p)))
print("p2:", hex(id(p2)))
print("lstPersons[0]:",hex(id(lstPersons[0])))
print("lstPersons[1]:", hex(id(lstPersons[1])))

print(lstPersons)

for persoon in lstPersons:
    print("persoon:", hex(id(persoon)))
    print(persoon.tell())

#p.__name="Nabil"

#print(p.name)
print(p.tell())