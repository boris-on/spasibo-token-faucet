from flask import Flask, request, jsonify
from web3 import Web3
from eth_account import Account
import json
from flask_cors import CORS, cross_origin

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

mnemonic = config["mnemonic"]
account_address = config["account_address"]
blockchain_url = config["blockchain_url"]
token_contract_address = config["token_contract_address"]

w3 = Web3(Web3.HTTPProvider(blockchain_url))
print(w3.is_connected(show_traceback=True))
account = w3.eth.account
account.enable_unaudited_hdwallet_features()
account.from_mnemonic(mnemonic)

with open('abi.json', 'r') as file:
    abi = json.load(file)


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
@cross_origin()
def index():
    with open('index.html', 'r') as file:
        content = file.read()
    get_balance()

    return content

@app.route('/get_balance', methods=['GET'])
@cross_origin()
def get_balance():
    balance = get_token_balance()
    return jsonify({'balance': balance})

@app.route('/get_token', methods=['POST'])
@cross_origin()
def get_token():
    data = request.json
    to_address = data.get('to_address')
    print(to_address)
    hash = send(account_address, to_address)
    return jsonify({'transaction_hash': hash})

def get_token_balance():
    contract = w3.eth.contract(address=token_contract_address, abi=abi)

    balance = contract.functions.balanceOf(account_address).call()
    return balance / (10 ** 18)

def send(from_address, to_address):
    dict_transaction = {
        'from': from_address,
    }
    print(from_address, to_address)
    contract = w3.eth.contract(address=token_contract_address, abi=abi)

    transaction = contract.functions.transfer(
        to_address, 1000 * 10 ** 18
    ).buildTransaction(dict_transaction)

    signed_txn = account.sign_transaction(transaction)

    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return txn_hash

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
