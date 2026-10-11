#an amusement park charges different rates for different age groups:
#admission for anyone under age 4 is free
#admission for anyone between the ages of 4 and 18 is 25$
#admission for anyone age 18 or older is 40$

#the following code tests for the age group of a person and then prints an admission price message:


age = float(input("What is your age \n"))

if age <4:
    price = 0
elif age < 18:
    price = 25
else:
    price = 40

print(f"Your admission cost is ${price}.")