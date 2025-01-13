import json
import requests
from flask import Flask, jsonify, request, redirect, render_template
from cryptography.fernet import Fernet
import paypalrestsdk

my_api = paypalrestsdk.configure({
    'mode':
    'sandbox',
    'client_id':
    'clientid',
    'client_secret':
    'clientid'
})
key = b'yourkey'
fernet = Fernet(key)

# This is your Stripe CLI webhook secret for testing your endpoint locally.
endpoint_secret = ''

app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data.decode()
    print(payload)
    md = json.loads(payload)["data"]["object"]["metadata"]
    amount = json.loads(payload)["data"]["object"]["amount_subtotal"]
    """sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header,
                                               endpoint_secret)
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e"""

    # Handle the event
    #print('Unhandled event type {}'.format(event['type']))
    #db.update_bal(md["tag"],float(amount)/100)
    encText = fernet.encrypt(md["tag"].encode()).decode()

    dd = {"tag": md["tag"], "amount": float(amount) / 100, "secret": encText}
    r = requests.get('http://127.0.0.1:25400/events?tag=', json=dd)
    print(r.text)
    print('request sent')
    return jsonify(success=True)


@app.route('/paypal')
def get_data():
    id = request.args.get("paymentId")
    payer = request.args.get("PayerID")
    tag = request.args.get("tag")
    amount = request.args.get("amount")
    payment = paypalrestsdk.Payment.find(id)
    #print(payment.to_dict)
    if payment.execute({"payer_id": payer}):
        print("Payment execute successfully")
        encText = fernet.encrypt(tag.encode()).decode()
        dp = {"tag": tag, "amount": amount, "secret": encText}
        r = requests.get('http://127.0.0.1:25400/events', json=dp)
        print(r.text)
        print('request sent')
        return redirect("discord://", code=302)

    else:
        print(payment.error)
        return redirect("discord://", code=302)

@app.route("/success")
def success():
    return render_template('./html/success.html')
@app.route("/cancel")
def cancel():
    return render_template('./html/cancel.html')
app.run(host="0.0.0.0", port=3007)
