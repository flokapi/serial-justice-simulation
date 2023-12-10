# Getting started

## Preparation

As a prerequisite, [serial-justice-contracts](https://github.com/flokapi/serial-justice-contracts) must be installed.

Create 5 MetaMask wallets and fund them with the Fantom Testnet Faucet: https://faucet.fantom.network/



## Installation

You should find yourself in the same directory as `serial-justice-contracts`

```
serial-justice/ <- HERE
	serial-justice-contract
```

Clone the `serial-justice-simulation` repository

```
git clone git@github.com:flokapi/serial-justice-simulation.git
```

Install the dependencies

````
pip install -r requirements.txt
````



## Deploy and export the contracts

From `serial-justice-contracts`, deploy to the Fantom Testnet

```
make deploy ARGS="--network fantom-test"
```

This should produce a `config.json` and ABI files under `serial-justice-simulation/env`

Create a `serial-justice-simulation/env/private_keys.json` which contains the previously created private keys.

```
[
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]
```



## Run the simulation

Start the simulation with `python simulation.py`



# Expected results

Example: [example_result.txt](./doc/example_result.txt)

Steps:

1. If the DAO has no members, the members will be added

2. The first member submits a questions, which burns a Justice Token. If he has no JT token, he will have to wait util the next token creation.

3. A member of the DAO will be randomly picked as the next voter on the question.

4. The new voter submits an answer.

5. The first member repeats requesting new voters by spending tokens until the question reaches a certain number of votes and becomes "finally answered".

The `Question` struct of the `SerialJustice` contracts is represented as a list:

```
[2, 'Is pineapple allowed on pizza?', '0xAf7A4B0827c5033B641819deeBcb3dd771BCF3Aa', '0x7026A9C05aa2C38a8C712Ed2f2b03a669A16bFF3', 0, 1]
```

can be interpreted with:

```solidity
enum QuestionState {
    IDLE,
    AWAITING_VOTER_DESIGNATION,
    AWAITING_VOTER_ANSWER,
    FINAL_ANSWER
}

struct Question {
    QuestionState state;
    string text;
    address submitter;
    address nextVoter;
    uint256 nbVotesYes;
    uint256 nbVotesNo;
}
```
