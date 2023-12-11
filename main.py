import time
import random

import setup


QUESTION_IDLE = 0
QUESTION_AWAITING_VOTER_DESIGNATION = 1
QUESTION_AWAITING_VOTER_ANSWER = 2
QUESTION_FINAL_ANSWER = 3


###### Helper functions


def call(_contract, _function, _args=[]):
    return getattr(_contract.functions, _function)(*_args).call()


def transact(_w3, _contract, _function, _args=[], _params={}):
    tx_hash = getattr(_contract.functions, _function)(*_args).transact(_params)
    return _w3.eth.wait_for_transaction_receipt(tx_hash)


def get_contract(_w3, _address, _abi):
    return _w3.eth.contract(address=_address, abi=_abi)


###### Simulation


def show_last_question(serialJustice):
    nb_questions = call(serialJustice, "getQuestionCount")
    print("========== Last question")
    if nb_questions >= 1:
        question_id = nb_questions - 1
        print(
            f"Question {question_id}: {call(serialJustice, 'getQuestionData', [question_id])}"
        )
    else:
        print("None")


def show_balance(justiceToken, accounts, decimals):
    print("========== Justice Token Balance")
    for account in accounts:
        balance = call(justiceToken, 'balanceOf', [account]) / (10**decimals)
        print(f"{account}: {balance} JT")


def check_upkeep(w3, justiceToken):
    if call(justiceToken, "checkUpkeep", ["0x"])[0]:
        print("### Minting one Justice Token for each member")
        transact(w3, justiceToken, "performUpkeep", ["0x"])


def add_members(w3, mainDAO, accounts):
    print("=================== Add DAO Members")
    if call(mainDAO, "getMemberCount") == 0:
        for account in accounts:
            print(f"### Adding member {account}")
            transact(w3, mainDAO, "addMember", [account])
    else:
        print("Not needed")
    print(f"Number of DAO members: {call(mainDAO, 'getMemberCount')}")


def check_enough_balance(w3, justiceToken, creator, answer_price):
    print("=================== Check Justice Tokens balance")
    while call(justiceToken, "balanceOf", [creator]) < answer_price:
        print("Not enough Justice Tokens, waiting for token creation...")
        check_upkeep(w3, justiceToken)
        time.sleep(10)
    print("=> Balance is enough")


def submit_question(w3, serialJustice, creator):
    print("=================== Submit question")
    question_text = "Should we remove the shoes before getting inside?"
    print(f"### Member {creator} submits question: {question_text}")
    transact(w3, serialJustice, "submitQuestion", [question_text])
    show_last_question(serialJustice)


def wait_new_voter_defined(serialJustice, question_id):
    print("=================== Wait new voter defined")
    while True:
        question = call(serialJustice, "getQuestionData", [question_id])
        question_state = question[0]

        if question_state == QUESTION_AWAITING_VOTER_ANSWER:
            break
        else:
            print("Next voter not yet defined, waiting...")
            time.sleep(10)

    next_voter = question[3]
    print(f"Next Voter selected: {next_voter}")
    show_last_question(serialJustice)


def new_voter_answers_question(w3, serialJustice, question_id):
    print("=================== New voter answers question")
    question = call(serialJustice, "getQuestionData", [question_id])
    next_voter = question[3]
    question_text = question[1]

    answer = bool(int(random.random() * 2) % 2)
    print(f'### Member {next_voter} answers to "{question_text}": {answer}')
    transact(
        w3,
        serialJustice,
        "answerQuestion",
        [question_id, answer],
        {"from": next_voter},
    )
    show_last_question(serialJustice)


def request_new_vote(w3, serialJustice, creator, question_id):
    print("=================== Request a new vote")
    print(f"### Member {creator} requests a new vote")
    transact(w3, serialJustice, "requestNewVote", [question_id])
    show_last_question(serialJustice)


def is_answer_final(serialJustice, question_id):
    question = call(serialJustice, "getQuestionData", [question_id])
    question_state = question[0]
    return question_state == QUESTION_FINAL_ANSWER


def show_final_answer(_w3, serialJustice, question_id):
    print("=================== Show final answer")
    question = call(serialJustice, "getQuestionData", [question_id])
    question_state = question[0]
    nb_votes_yes = question[4]
    nb_votes_no = question[5]
    if question_state == QUESTION_FINAL_ANSWER:
        if nb_votes_yes > nb_votes_no:
            print("Yes, everybody must remove their shoes")
        else:
            print("No, you can keep you shoes on")


def simulation(w3, contracts, accounts):
    print("#######################################################################")
    print("#                 Simulating the voting mechanism                      ")
    print("#######################################################################")

    mainDAO, serialJustice, justiceToken = contracts
    creator = accounts[0]

    answer_price = call(justiceToken, "getAnswerPrice")
    decimals = call(justiceToken, "decimals")

    add_members(w3, mainDAO, accounts)

    show_balance(justiceToken, accounts, decimals)

    check_enough_balance(w3, justiceToken, creator, answer_price)
    submit_question(w3, serialJustice, creator)

    question_id = call(serialJustice, "getQuestionCount") - 1

    wait_new_voter_defined(serialJustice, question_id)
    new_voter_answers_question(w3, serialJustice, question_id)

    while not is_answer_final(serialJustice, question_id):
        check_enough_balance(w3, justiceToken, creator, answer_price)
        request_new_vote(w3, serialJustice, creator, question_id)
        wait_new_voter_defined(serialJustice, question_id)
        new_voter_answers_question(w3, serialJustice, question_id)

    show_final_answer(w3, serialJustice, question_id)



def test_vote_timeout(w3, contracts, accounts):
    print("#######################################################################")
    print("#                 Testing the vote Timeout                             ")
    print("#######################################################################")


    mainDAO, serialJustice, justiceToken = contracts
    creator = accounts[0]

    answer_price = call(justiceToken, "getAnswerPrice")
    vote_timeout = call(serialJustice, "getVoteTimeout")

    add_members(w3, mainDAO, accounts)
    check_enough_balance(w3, justiceToken, creator, answer_price)
    submit_question(w3, serialJustice, creator)

    question_id = call(serialJustice, "getQuestionCount") - 1
    wait_new_voter_defined(serialJustice, question_id)
    _, _, _, voter1, _, _, voteUntil1 = call(serialJustice, 'getQuestionData', [question_id])

    wait_duration = vote_timeout*2
    print(f"Waiting until the vote times out... (approx {vote_timeout}s)")
    while True:
        time.sleep(wait_duration/10)
        if call(serialJustice, 'isVoteTimeout', [question_id]):
            print('timeout!')
            break
        else:
            print('not yet')

    print("Performing SerialJustice upkeep")
    transact(w3, serialJustice, "performUpkeep", ["0x"])
    wait_new_voter_defined(serialJustice, question_id)

    _, _, _, voter2, _, _, voteUntil2 = call(serialJustice, 'getQuestionData', [question_id])


    print("=================== Results")
    print(f"voter 1: {voter1} ; voter 2 {voter2} -- they might actually be the same")
    print(f"vote until 1: {voteUntil1} ; vote until 2 {voteUntil2} -- must be different")
    assert voteUntil1 != voteUntil2
    print("=> PASSED!")



###### Main


def main():
    w3, contracts, accounts = setup.get_setup()
    test_vote_timeout(w3, contracts, accounts)
    simulation(w3, contracts, accounts)


if __name__ == "__main__":
    main()
