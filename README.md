# Getting started

## Preparation

As a prerequisite, [serial-justice-contracts](https://github.com/flokapi/serial-justice-contracts) must be installed. 



Create 5 MetaMask wallets and fund them with the Fantom Testnet Faucet:  https://faucet.fantom.network/



## Installation

#### Clone the repository

You should find yourself in the same directory as `serial-justice-contracts`

````
serial-justice/ <- HERE
	serial-justice-contract
````



Clone the `serial-justice-simulation` repository

````
git clone git@github.com:flokapi/serial-justice-simulation.git
````



### Deploy and export the contracts

From `serial-justice-contracts`, deploy to the Fantom Testnet

````
make deploy ARGS="--network fantom-test"
````

This should produce a `config.json` and ABI files under `serial-justice-simulation/env`



Create a `serial-justice-simulation/env/private_keys.json`  which contains the previously created private keys.

````
[
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]
````



### Run the simulation

Start the simulation with `python test.py`



# Expected results

Example: [expected_result.txt](./doc/expected_result.txt)

If the DAO has no members, the members will be added

The first member submits a questions, which burns a Justice Token. If he has no JT token, he will have to wait util the next token creation.

A member of the DAO will be randomly picked as the next voter on the question. He submits an answer.

The first member repeats requesting new voters by spending tokens until the question reaches a certain number of votes and becomes "finally answered".

