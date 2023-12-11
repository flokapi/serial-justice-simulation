from web3 import Web3
from eth_account import Account
from web3.middleware import construct_sign_and_send_raw_middleware
import time
import random
import utils


CHAIN_ID = "4002"
# CHAIN_ID = "11155111"

MAIN_DAO_ABI = utils.get_abi("MainDAO.json")
SERIAL_JUSTICE_ABI = utils.get_abi("SerialJustice.json")
JUSTICE_TOKEN_ABI = utils.get_abi("JusticeToken.json")

PRIVATE_KEYS = utils.get_private_keys()
CONFIG = utils.get_config()
RPC_URL = CONFIG[CHAIN_ID]["rpc_url"]
MAIN_DAO_ADDR = CONFIG[CHAIN_ID]["contract_address"]



###### Helper functions


def call(_contract, _function, _args=[]):
    return getattr(_contract.functions, _function)(*_args).call()


def transact(_w3, _contract, _function, _args=[], _params={}):
    tx_hash = getattr(_contract.functions, _function)(*_args).transact(_params)
    return _w3.eth.wait_for_transaction_receipt(tx_hash)


def get_contract(_w3, _address, _abi):
    return _w3.eth.contract(address=_address, abi=_abi)


###### Setup


def get_contracts(_w3, _daoAddress):
    mainDAO = get_contract(_w3, _daoAddress, MAIN_DAO_ABI)

    serial_justice_address = call(mainDAO, "getSerialJusticeAddress")
    serialJustice = get_contract(_w3, serial_justice_address, SERIAL_JUSTICE_ABI)

    justice_token_address = call(serialJustice, "getJusticeTokenAddress")
    justiceToken = get_contract(_w3, justice_token_address, JUSTICE_TOKEN_ABI)

    print(f"MainDAO address: {_daoAddress}")
    print(f"SerialJustice address: {serial_justice_address}")
    print(f"JusticeToken address: {justice_token_address}")

    return mainDAO, serialJustice, justiceToken


def add_accounts(_w3):
    accounts = []

    for private_key in PRIVATE_KEYS:
        account = Account.from_key(private_key)
        _w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
        accounts.append(account.address)

    _w3.eth.default_account = accounts[0]

    return accounts


###### Main


def get_setup():
    print(f"Running on chain id: {CHAIN_ID}")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    contracts = get_contracts(w3, MAIN_DAO_ADDR)
    accounts = add_accounts(w3)
    return w3, contracts, accounts