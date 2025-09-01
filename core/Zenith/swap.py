from config.settings import wallets, sleep
from config.constants import SWAP_CONTRACT_ABI,ERC20_CONTRACT_ABI,USDC_CONTRACT_ADDRESS,USDT_CONTRACT_ADDRESS,WPHRS_CONTRACT_ADDRESS,SWAP_ROUTER_ADDRESS
from utils.helpers import get_web3_with_check, approving_token

from eth_utils import to_hex
from eth_abi.abi import encode
import json
import time
import random


wphrs_amount = 0
usdc_amount = 0
usdt_amount = 0


def generate_swap_option(wphrs_amount: float, usdc_amount: float, usdt_amount: float):
    swap_option= random.choice([
        "WPHRStoUSDC", "WPHRStoUSDT", "USDCtoWPHRS",
        "USDTtoWPHRS", "USDCtoUSDT", "USDTtoUSDC"
    ])

    from_token=(
        USDC_CONTRACT_ADDRESS if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
        USDT_CONTRACT_ADDRESS if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
        WPHRS_CONTRACT_ADDRESS
    )
    to_token = (
        USDC_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
        USDT_CONTRACT_ADDRESS if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
        WPHRS_CONTRACT_ADDRESS
    )
    
    from_ticker = (
        "USDC" if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
        "USDT" if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
        "WPHRS"
    )

    to_ticker = (
        "USDC" if swap_option in ["WPHRStoUSDC", "USDTtoUSDC"] else
        "USDT" if swap_option in ["WPHRStoUSDT", "USDCtoUSDT"] else
        "WPHRS"
    )

    swap_amount = (
        usdc_amount if swap_option in ["USDCtoWPHRS", "USDCtoUSDT"] else
        usdt_amount if swap_option in ["USDTtoWPHRS", "USDTtoUSDC"] else
        wphrs_amount
    )
    return from_token,to_token,from_ticker,to_ticker,swap_amount



def generate_multicall_data(web3, address: str, from_token: str, to_token: str, swap_amount: float):
    try:
        token_contract = web3.eth.contract(address=web3.to_checksum_address(from_token), abi=ERC20_CONTRACT_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_to_wei = int(swap_amount * (10 ** decimals))

        encoded_data = encode(
            ["address", "address", "uint256", "address", "uint256", "uint256", "uint256"],
            [
                web3.to_checksum_address(from_token),
                web3.to_checksum_address(to_token),
                500,
                web3.to_checksum_address(address),
                amount_to_wei,
                0,
                0
            ]
        )
        multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]
        return multicall_data
    except Exception as e:
        raise Exception(f"Generate Multicall Data Failed: {str(e)}")

def perform_swap(web3, account, address, from_token, to_token, swap_amount):
    try:
        approving_token(web3, account, address, SWAP_ROUTER_ADDRESS, from_token, swap_amount)
        token_contract = web3.eth.contract(address=web3.to_checksum_address(SWAP_ROUTER_ADDRESS), abi=SWAP_CONTRACT_ABI)

        deadline = int(time.time()) + 300
        multicall_data = generate_multicall_data(web3, address, from_token, to_token, swap_amount)
        swap_data = token_contract.functions.multicall(deadline, multicall_data)

        estimated_gas = swap_data.estimate_gas({"from": address})
        max_priority_fee = web3.to_wei(1, "gwei")
        max_fee = max_priority_fee
    
        swap_tx = swap_data.build_transaction({
            "from": address,
            "gas": int(estimated_gas * 1.2),
            "maxFeePerGas": int(max_fee),
            "maxPriorityFeePerGas": int(max_priority_fee),
            "nonce": web3.eth.get_transaction_count(address, "pending"),
            "chainId": web3.eth.chain_id,
        })

        signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
        raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash = web3.to_hex(raw_tx)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
        print(f"✅ Swap successfull: https://testnet.pharosscan.xyz/tx/{tx_hash}")
    except Exception as e:
        print("❌ Error perform_swap:", e)
