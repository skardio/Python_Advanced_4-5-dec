class Vector():
    def __init__(self, x,y):
        self.x = x
        self.y = y
    
    def __str__(self): # For users
        return f"({self.x}, {self.y})"
    
    def __repr__(self): # Debugging, recreëren
        return f"Vector({self.x}, {self.y})"
    
    def __add__(self,other): #v1 + v2, self = v1 en other = v2
        return Vector(self.x + other.x, self.y + other.y) # returned een nieuw object

v1 = Vector(1,1)
v2 = Vector(3,1)

v3 = v1 + v2
print(v3.__repr__)

v3 = Vector(4, 2)