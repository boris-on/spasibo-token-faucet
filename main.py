from flask import Flask, request, jsonify
from web3 import Web3
from eth_account import Account
import json
from flask_cors import CORS, cross_origin

# Load configuration from JSON file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Initialize variables from config
mnemonic = config["mnemonic"]
account_address = config["account_address"]
blockchain_url = config["blockchain_url"]
token_contract_address = config["token_contract_address"]
private_key = config["private_key"]

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(blockchain_url))
account = w3.eth.account
account.enable_unaudited_hdwallet_features()
account.from_mnemonic(mnemonic)

# Load ABI from JSON file
with open("abi.json", "r") as abi_file:
    abi = json.load(abi_file)

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


# Route to serve index.html
@app.route("/")
@cross_origin()
def index():
    with open("index.html", "r") as file:
        content = file.read()
    return content


# Route to get token balance
@app.route("/get_balance", methods=["GET"])
@cross_origin()
def get_balance():
    balance = get_token_balance()
    return jsonify({"balance": balance})


# Route to transfer tokens
@app.route("/get_token", methods=["POST"])
@cross_origin()
def get_token():
    data = request.json
    to_address = data.get("to_address")
    hash = send_tokens(account_address, to_address)
    return jsonify({"transaction_hash": hash})


# Function to get token balance
def get_token_balance():
    contract = w3.eth.contract(address=token_contract_address, abi=abi)
    balance = contract.functions.balanceOf(account_address).call()
    return balance / (10**18)


# Function to send tokens
def send_tokens(from_address, to_address):
    nonce = w3.eth.get_transaction_count(from_address)
    dict_transaction = {"from": from_address, "nonce": nonce}
    contract = w3.eth.contract(address=token_contract_address, abi=abi)
    transaction = contract.functions.transfer(
        to_address, 1000 * 10**18
    ).build_transaction(dict_transaction)
    signed_txn = account.sign_transaction(transaction, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return txn_hash.hex()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
