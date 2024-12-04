class Animal():

    def __init__(self, name):
        self._name = name

    def tell(self):
        return self._name + " gives sound."



class Cat(Animal):

    def __init__(self, name):
        super().__init__(name)

    def tell(self):
        return self._name + " meows."
    
    

class Dog(Animal):

    def __init__(self, name):
        super().__init__(name)

    def tell(self):
        return self._name + " barks."



animalRicky = Dog("Ricky")
animalAmber = Cat("Amber")
generalAnimal = Animal("Martijn")

print(animalRicky.tell())
print(animalAmber.tell())
print(generalAnimal.tell())


