banned_users = ['andrew', 'carolina', 'david']
user = 'marie'

#we are gonna check whether a user is banned from a forum or not

if user not in banned_users:
    print(f"{user.title()}, you can post a response if you wish")


