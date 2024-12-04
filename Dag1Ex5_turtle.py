# https://nl.wikipedia.org/wiki/Regelmatige_veelhoek

import turtle

# Create two turtles
t1 = turtle.Turtle()
t2 = turtle.Turtle()

# Give the turtles diverent colors
t1.color('red')
t2.color('blue')

n = 5
# angle = 360/n   # 180 - (180 - 360/n)
angle = 180 - (180 - 360/n)

for _ in range(n):
    t1.forward(100)
    t1.left(angle)

n = 8
# angle = 360/n   # 180 - (180 - 360/n)
angle = 180 - (180 - 360/n)

for _ in range(n):
    t2.forward(100)
    t2.left(angle)

turtle.done()
