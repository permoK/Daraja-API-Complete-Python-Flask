from flask import Flask, request
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import base64

import uuid

app = Flask(__name__)

base_url = ''
key = ''
secret = ''


@app.route('/')
def home():
    return 'Hello World!'

@app.route('/access_token')
def get_access_token():
    consumer_key = key
    consumer_secret = secret
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']

@app.route('/register')
def register_urls():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    access_token = _access_token()
    my_endpoint = base_url + "c2b/"
    headers = { "Authorization": "Bearer %s" % access_token }
    r_data = {
        "ShortCode": "600383",
        "ResponseType": "Completed",
        "ConfirmationURL": my_endpoint + 'con',
        "ValidationURL": my_endpoint + 'val'
    }

    response = requests.post(endpoint, json = r_data, headers = headers)
    return response.json()


@app.route('/simulate')
def test_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate'
    access_token = _access_token()
    headers = { "Authorization": "Bearer %s" % access_token }

    data_s = {
        "Amount": 100,
        "ShortCode": "174379",
        "BillRefNumber": "test",
        "CommandID": "CustomerBuyGoodsOnline", # for paybill - CustomerPayBillOnline
        "Msisdn": "254714025354"
    }

    res = requests.post(endpoint, json= data_s, headers = headers)
    return res.json()

@app.route('/b2c')
def make_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest'
    access_token = _access_token()
    headers = { "Authorization": "Bearer %s" % access_token }
    my_endpoint = base_url + "/b2c/"

    data = {
        "OriginatorConversationID": uuid.uuid4().hex,
        "InitiatorName": "testapi",
        "SecurityCredential": "d++95U0ItaW985ABjd+n0b49es9AdXnC4v7vfztnx6/sbdbuxoq9Zqmv85RfL0CriEr62lUC11lgLxKjtSQGFD1DWJ50Vkecto6LNgjJTFH9KmSKKVEi0Ix2RiKKMdCAZydDLsQ1vSnGjgyg8CWhe2GpoVCm9OBu8jlmaVNBCZ/pQ/UmbSct8WsnT8CU4u4gV/v+Egx8s9cxI5CdJOJHy7QjCR4VZK/DX0tn7wOK86+ZZ7K+EVIPi0PfkbYw/QxByiphk27pPF1xFoHHBX46HEugSaXMm83K2SW7dMy7yxXjHefDi6KFgsMCUJxUhu0H43indXRGvLP5jRiWaWJJuA==",
        "CommandID": "BusinessPayment",
        "Amount": "200",
        "PartyA": "601342",
        "PartyB": "254714025354",
        "Remarks": "Pay Salary",
        "QueueTimeOutURL": my_endpoint + "timeout",
        "ResultURL": my_endpoint + "result",
        "Occasion": "Salary"
    }

    res = requests.post(endpoint, json = data, headers = headers)
    return res.json()

@app.route('/lnmo')
def init_stk():
    phone = request.args.get('phone')
    amount = request.args.get('amount')

    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = _access_token()
    headers = { "Authorization": f"Bearer {access_token}" }
    my_endpoint = base_url 
    Timestamp = datetime.now()
    times = Timestamp.strftime("%Y%m%d%H%M%S")
    password = "174379" + "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" + times
    datapass = base64.b64encode(password.encode('utf-8')).decode('utf-8')  # Decode to string
    # print(datapass)

    data = {
        "BusinessShortCode": "174379",
        "Password": datapass,
        "Timestamp": times,
        "TransactionType": "CustomerBuyGoodsOnline", # for paybill - CustomerPayBillOnline
        "PartyA": phone,
        "PartyB": "174379",
        "PhoneNumber": phone, # fill with your phone number
        "CallBackURL": my_endpoint + "/lnmo-callback",
        "AccountReference": "TestPay",
        "TransactionDesc": "HelloTest",
        "Amount": amount
    }
    res = requests.post(endpoint, json=data, headers=headers)
    return res.json()

# consume mpesa express CallBack
@app.route('/lnmo-callback', methods=['POST'])
def incoming():
    data = request.get_json()
    print(data)
    return "ok"

@app.route('/lnmo', methods=['POST'])
def lnmo_result():
    data = request.get_data()
    f = open('lnmo.json', 'a')
    f.write(data)
    f.close()


@app.route('/b2c/result', methods=['POST'])
def result_b2c():
    data = request.get_data()
    f = open('b2c.json', 'a')
    f.write(data)
    f.close()

@app.route('/b2c/timeout', methods=['POST'])
def b2c_timeout():
    data = request.get_json()
    f = open('b2ctimeout.json', 'a')
    f.write(data)
    f.close()

@app.route('/c2b/val', methods=['POST'])
def validate():
    data = request.get_data()
    f = open('data_v.json', 'a')
    f.write(data)
    f.close()

@app.route('/c2b/con', methods=['POST'])
def confirm():
    data = request.get_json()
    f = open('data_c.json', 'a')
    f.write(data)
    f.close()


def _access_token():
    consumer_key = key
    consumer_secret = secret
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
