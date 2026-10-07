import time
from time import sleep


print("Welcome to our website!")
sleep(1)

first_name = input("What is your name? ")
sleep(0.5)

last_name = input("What is your last name? ")
sleep(0.5)


full_name = f"{first_name} {last_name}"

print("Congratulations! You have successfully logged in as " + full_name + "!!!")
sleep(2)

print("\tHere are available pages in our website: \nAbout\nProducts\nPricing\nServices\nContacts")

