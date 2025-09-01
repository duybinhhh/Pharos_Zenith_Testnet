import time
import random
from web3 import Web3
from utils.helpers import  generate_random_receiver
import random


def transfer(address, account, web3, session, use_proxy, proxy,amount: float, number:int):

        recipients = [generate_random_receiver() for _ in range(number)] 
        base = amount / len(recipients)
        for j, to in enumerate(recipients):
            amount_PHRS = round(random.uniform(0.9 * base, 1.1 * base), 4)
            to = Web3.to_checksum_address(to)
            value = web3.to_wei(amount_PHRS, "ether")

            tx = {
                "from": address,
                "to": to,
                "value": value,
                "gas": 21000,
                "gasPrice": web3.to_wei(1, "gwei"),
                "nonce": web3.eth.get_transaction_count(address),
                "chainId": web3.eth.chain_id,
            }

            try:
                print(f"Transfer {amount_PHRS} PHRS from {address} to {to}")
                signed = web3.eth.account.sign_transaction(tx, private_key=account)
                tx_hash = web3.eth.send_raw_transaction(signed.raw_transaction)
                print(f"✅ Transfer successful: https://testnet.pharosscan.xyz/tx/{tx_hash.hex()}")
                

            except Exception as e:
                print(f"❌ Error when transferring to {to}: {e}")

            waiting_time = round(random.uniform(5, 10),0)
            print(f"⏱️  Wait {waiting_time}s before making the next transaction...")
            time.sleep(waiting_time)
