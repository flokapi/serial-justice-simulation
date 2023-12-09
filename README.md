# Getting started

### Preparation

As a prerequisite, [serial-justice-contracts](https://github.com/flokapi/serial-justice-contracts) must be installed. 



Create 5 MetaMask wallets and fund them with the Fantom Testnet Faucet:  https://faucet.fantom.network/



### Installation

You should find yourself in the same directory as `serial-justice-contracts`

````
serial-justice/ <- HERE
	serial-justice-contract
````



Clone the `serial-justice-simulation` repository

````
git clone git@github.com:flokapi/serial-justice-simulation.git
````



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



### Running

Start the simulation with `python test.py`



### Expected results