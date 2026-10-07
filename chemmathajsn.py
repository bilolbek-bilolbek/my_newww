import math
import time
from time import sleep


print("Welcome to calculator!")
sleep(2)

text1 = ("For now, we have the only function: x^y , where x and y are any digits" +
      "\n(intevgers, floats, negative, etc.)")

def type_print(text1, delay = 0.1):
    for word in text1.split(" "):
        print(word, end = " ", flush = True)
        sleep(delay)
    print()
print(type_print(text1))




print("Please enter x from x^y")
x = int, float(input())
sleep(2)


print("Please enter y from x^y")
y = int, float(input())


print(math.pow(x, y))


