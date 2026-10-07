import requests

url = "https://gamma-api.polymarket.com/markets"
params = {"closed": "true", "limit": 10, "order": "id", "ascending": "false"}

response = requests.get(url, params=params)
markets = response.json()

print(type(markets))
print(len(markets))
print(markets[0].keys())

for m in markets:
    print(m["question"])
    print(" outcomes:", m["outcomes"])
    print(" final prices:", m["outcomePrices"])
    print(" volume:", m["volumeNum"])
    print(" closed:", m["closedTime"])
    print()


