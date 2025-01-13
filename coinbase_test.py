from coinbase_commerce.client import Client

API_KEY=""

client = Client(api_key=API_KEY)

charge_info = {
    "name": "SHFT test",
    "description": "Juss testin",
    "local_price": {
        "amount": "1.00",
        "currency": "USD"
    },
    "pricing_type": "fixed_price",
    "metadata":{"user":"test"}

}
charge = client.charge.create(**charge_info)
print(charge['hosted_url']) 
#print("https://commerce.coinbase.com/checkout/"+checkout['id'])