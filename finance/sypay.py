import stripe
import datetime
from paypalrestsdk import Payment
import paypalrestsdk
from coinbase_commerce.client import Client
import time

SYCASH_URL = ""
my_api = paypalrestsdk.Api({
  'mode': 'sandbox',
  'client_id': '',
  'client_secret': ''})

stripe.api_key = ""


def create_checkout(tag,amount):
    current_time = datetime.datetime.now(datetime.timezone.utc)
    unix_timestamp = current_time.timestamp()
    prix=stripe.Price.create(
    unit_amount=int(amount*100),
    currency="eur",
    product="",
    )

    lnk=stripe.checkout.Session.create(
    success_url=f"{SYCASH_URL}/success",
    cancel_url=f"{SYCASH_URL}/cancel",
    line_items=[
        {
        "price": prix["id"],
        "quantity": 1
        },
    ],
    mode="payment",
    metadata={"tag":tag},
    expires_at=int(unix_timestamp + (30 * 60)))

    return lnk['url']


def create_checkout_paypal(tag,amount):
    am=str(amount)
    payment = Payment({
        "intent": "sale",

        # Payer
        # A resource representing a Payer that funds a payment
        # Payment Method as 'paypal'
        "payer": {
            "payment_method": "paypal"},

        # Redirect URLs
        "redirect_urls": {
            "return_url": f"{SYCASH_URL}/paypal?tag="+tag+"&amount="+am,
            "cancel_url": f"{SYCASH_URL}/cancel"},

        # Transaction
        # A transaction defines the contract of a
        # payment - what is the payment for and who
        # is fulfilling it.
        "transactions": [{

            "custom_id":"900141001916678214",
            "item_list": {
                "items": [{
                    "name": "Sycash credit",
                    "sku": "sycash",
                    "price": "100",
                    "currency": "EUR",
                    "quantity": 1}]},

            # Amount
            # Let's you specify a payment amount.
            "amount": {
                "total": "100",
                "currency": "EUR"},
            "description": "Fund your Sycash account."}]},api=my_api)

    # Create Payment and return status
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Redirect the user to given approval url
        for link in payment.links:
            if link.rel == "approval_url":
                # Convert to str to avoid google appengine unicode issue
                # https://github.com/paypal/rest-api-sdk-python/pull/58
                approval_url = str(link.href)
                #print("Redirect for approval: %s" % (approval_url))
                return approval_url
    else:
        print("Error while creating payment:")
        print(payment.error)


def create_checkout_crypto(tag,amount):
    expire_time = int(time.time() + 18)
    client = Client(api_key=API_KEY)
    charge_info = {
        "name": "Sycash credit",
        "description": "Fund your Sycash account.",
        "local_price": {
            "amount": str(amount),
            "currency": "USD"
        },
        "pricing_type": "fixed_price",
        "metadata":{"tag":tag}

    }
    charge = client.charge.create(**charge_info)
    return charge['hosted_url'] 


print(create_checkout("900141001916678214",10.50))