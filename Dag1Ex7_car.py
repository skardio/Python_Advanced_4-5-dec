class Car:
    """This is my own Car class"""

    def __init__(self, make, type, color, mileage=0):
        """Dit is de __init__ method with 3 arguments"""
        self.make = make
        self.type = type
        self.color = color
        self._mileage = mileage

    def __str__(self):
        """return a string with information about the car"""
        return f"My car is a {self.color} {self.make} {self.type}. " \
               f"Mileage: {self._mileage}."
    
    def __repr__(self):
        return f"Car('{self._make}', '{self._type}', '{self._color}')"

    def __eq__(self, other):
        return self._make == other._make and self._type == other._type

    def __gt__(self, other):
        return self._mileage > other._mileage
    def __lt__(self, other):
        return self._mileage < other._mileage
    def __ge__(self, other):
        return self._mileage >= other._mileage
    def __le__(self, other):
        return self._mileage <= other._mileage

    def __gt__(self, other):
        return self._mileage > other._mileage
    
    def drive(self, distance):
        """drive a distance and increment the mileage"""
        if distance < 0:
            raise Exception("Can't drive a negative distance")
        self._mileage += distance
        print( f'Driving {distance} km.')


car = Car('Volkswagen', 'Kever', 'Red')
car2 = Car('Volkswagen', 'Kever', 'Blauwe')
print(car)

car.drive(123)
car.drive(12)
car2.drive(1043)

print(car > car2)

try:
    car.drive(-5)
except Exception as e:
    print(e)