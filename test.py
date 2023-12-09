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


QUESTION_IDLE = 0
QUESTION_AWAITING_VOTER_DESIGNATION = 1
QUESTION_AWAITING_VOTER_ANSWER = 2
QUESTION_FINAL_ANSWER = 3


###### Helper functions


def call(_contract, _function, _args=[]):
    return getattr(_contract.functions, _function)(*_args).call()


def transact(_w3, _contract, _function, _args=[], _params={}):
    try:
        tx_hash = getattr(_contract.functions, _function)(*_args).transact(_params)
        _w3.eth.wait_for_transaction_receipt(tx_hash)
        return True
    except:
        return False


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


###### State machine simulation


def show_last_question(serialJustice):
    nb_questions = call(serialJustice, "getQuestionCount")
    print("=================== Last question")
    if nb_questions >= 1:
        question_id = nb_questions - 1
        print(
            f"Question {question_id}: {call(serialJustice, 'getQuestionData', [question_id])}"
        )
    else:
        print("None")


def check_upkeep(_w3, _contracts):
    _, _, justiceToken = _contracts
    if call(justiceToken, "checkUpkeep", ["0x"])[0]:
        print("### Performing upkeep")
        transact(_w3, justiceToken, "performUpkeep", ["0x"])


def add_members(_w3, _contracts, _accounts, _state):
    mainDAO, _, _ = _contracts
    if call(mainDAO, "getMemberCount") == 0:
        print("### Adding DAO members")
        for account in _accounts:
            transact(_w3, mainDAO, "addMember", [account])
    else:
        print("Not needed")
    print(f"Number of DAO members: {call(mainDAO, 'getMemberCount')}")
    _state.next()


def submit_question(_w3, _contracts, _accounts, _state):
    _, serialJustice, justiceToken = _contracts
    creator = _accounts[0]

    answer_price = call(justiceToken, "getAnswerPrice")

    if call(justiceToken, "balanceOf", [creator]) < answer_price:
        print("Not enough Justice Tokens, waiting for token creation...")
        time.sleep(10)
        return

    print("### Submitting a question")
    if transact(
        _w3, serialJustice, "submitQuestion", ["Is pineapple allowed on pizza?"]
    ):
        print("=> Successful")
        show_last_question(serialJustice)
        _state.next()
    else:
        time.sleep(10)


def wait_new_voter_defined(_w3, _contracts, _accounts, _state):
    _, serialJustice, _ = _contracts

    question_id = call(serialJustice, "getQuestionCount") - 1
    question = call(serialJustice, "getQuestionData", [question_id])
    question_state = question[0]

    if question_state != QUESTION_AWAITING_VOTER_ANSWER:
        print("Next voter not yet defined, waiting...")
        time.sleep(10)
        return

    next_voter = question[3]
    print(f"Next Voter selected: {next_voter}")
    show_last_question(serialJustice)
    _state.next()


def new_voter_answers_question(_w3, _contracts, _accounts, _state):
    _, serialJustice, _ = _contracts

    question_id = call(serialJustice, "getQuestionCount") - 1
    question = call(serialJustice, "getQuestionData", [question_id])
    next_voter = question[3]
    question_text = question[1]

    answer = bool(int(random.random() * 2) % 2)
    print(f'### Member {next_voter} answers to "{question_text}": {answer}')
    transact(
        _w3,
        serialJustice,
        "answerQuestion",
        [question_id, answer],
        {"from": next_voter},
    )
    show_last_question(serialJustice)
    _state.next()


def request_new_vote(_w3, _contracts, _accounts, _state):
    _, serialJustice, justiceToken = _contracts
    creator = _accounts[0]

    answer_price = call(justiceToken, "getAnswerPrice")

    if call(justiceToken, "balanceOf", [creator]) < answer_price:
        print("Not enough Justice Tokens, waiting for token creation...")
        time.sleep(10)
        return

    question_id = call(serialJustice, "getQuestionCount") - 1
    print("### Requesting a new vote")
    if transact(_w3, serialJustice, "requestNewVoter", [question_id]):
        print("=> Successful")
        show_last_question(serialJustice)
        _state.next()
    else:
        time.sleep(10)


def check_is_final_answer(_w3, _contracts, state):
    _, serialJustice, _ = _contracts

    nb_questions = call(serialJustice, "getQuestionCount")
    if nb_questions >= 1:
        question_id = nb_questions - 1
        question = call(serialJustice, "getQuestionData", [question_id])
        question_state = question[0]
        nb_votes_yes = question[4]
        nb_votes_no = question[5]
        if question_state == QUESTION_FINAL_ANSWER:
            if nb_votes_yes > nb_votes_no:
                print("Thankfully, pinapple is allowed on pizza")
            else:
                print("Unfortunately, pinapple is not allowed on pizza")
            state.set_finished()


class State:
    index = 0
    finished = False

    def __init__(self, states):
        self.states = states

    def next(self):
        self.index += 1

    def set_finished(self):
        self.finished = True

    def get(self):
        if self.finished or self.index >= len(self.states):
            return None
        return self.states[self.index]


def state_machine_simulation(_w3, _contracts, _accounts):
    setup_states = [
        "add_members",
        "submit_question",
    ]

    voting_cycle_states = [
        "wait_new_voter_defined",
        "new_voter_answers_question",
        "request_new_vote",
    ]

    state_list = setup_states + voting_cycle_states * 10
    state = State(state_list)

    transact(_w3, _contracts[1], "submitQuestion", ["Is it true?"])  #### hot fix
    while state.get() != None:
        print(f"=================== State: {state.get()}")

        # calling the function corresponding to the current state
        globals()[state.get()](_w3, _contracts, _accounts, state)

        check_upkeep(_w3, _contracts)
        check_is_final_answer(_w3, _contracts, state)

    print("Finished.")


###### Main


def main():
    print(f"Running on chain id: {CHAIN_ID}")

    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    accounts = add_accounts(w3)
    contracts = get_contracts(w3, MAIN_DAO_ADDR)
    state_machine_simulation(w3, contracts, accounts)


if __name__ == "__main__":
    main()
