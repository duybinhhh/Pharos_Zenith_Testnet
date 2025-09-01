import random

from web3 import Web3
from config.constants import USDC_CONTRACT_ADDRESS,USDT_CONTRACT_ADDRESS,WPHRS_CONTRACT_ADDRESS,POTITION_MANAGER_ADDRESS,ERC20_CONTRACT_ABI,ADD_LP_CONTRACT_ABI
from utils.helpers import get_web3_with_check,approving_token, check_balance
import time
from utils.helpers import check_balance

def generate_add_lp_option(web3, address, amount:int):
    options = ["USDCnWPHRS", "USDCnUSDT", "WPHRSnUSDT"]
    for _ in range(amount):
        a = random.choice(options)
        if a == "USDCnWPHRS":
            add_lp_option = "USDCnWPHRS"
            token0 = USDC_CONTRACT_ADDRESS
            token1 = WPHRS_CONTRACT_ADDRESS
            amount0 = round((check_balance(web3, address, USDC_CONTRACT_ADDRESS ))/amount, 2)
            amount1 = round((check_balance(web3, address, WPHRS_CONTRACT_ADDRESS ))/amount, 4)
            ticker0 = "USDC"
            ticker1 = "WPHRS"
        elif a == "USDCnUSDT":
            add_lp_option = "USDCnUSDT"
            token0 = USDC_CONTRACT_ADDRESS
            token1 = USDT_CONTRACT_ADDRESS
            amount0 = round((check_balance(web3, address, USDC_CONTRACT_ADDRESS ))/amount, 2)
            amount1 = round((check_balance(web3, address, USDT_CONTRACT_ADDRESS ))/amount, 2)
            ticker0 = "USDC"
            ticker1 = "USDT"
        elif a == "WPHRSnUSDT":
            add_lp_option = "WPHRSnUSDT"
            token0 = WPHRS_CONTRACT_ADDRESS
            token1 = USDT_CONTRACT_ADDRESS
            amount0 = round((check_balance(web3, address, WPHRS_CONTRACT_ADDRESS ))/amount, 4)
            amount1 = round((check_balance(web3, address, USDT_CONTRACT_ADDRESS ))/amount, 2)
            ticker0 = "WPHRS"
            ticker1 = "USDT"

    return add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1


def perform_add_liquidity(account:str, address:str, add_lp_option:str, token0:str, token1:str, amount0:float, amount1:float, use_proxy:bool, proxy:str):
    address = Web3.to_checksum_address(address) 
    web3 = get_web3_with_check(address,use_proxy,proxy)

    approving_token(web3, account, address, POTITION_MANAGER_ADDRESS, token0, amount0)
    approving_token(web3, account, address, POTITION_MANAGER_ADDRESS, token1, amount1)

    
    token0_contract = web3.eth.contract(address=web3.to_checksum_address(token0), abi=ERC20_CONTRACT_ABI)
    token0_decimals = token0_contract.functions.decimals().call()
    amount0_desired = int(amount0 * (10 ** token0_decimals))

    token1_contract = web3.eth.contract(address=web3.to_checksum_address(token1), abi=ERC20_CONTRACT_ABI)
    token1_decimals = token1_contract.functions.decimals().call()
    amount1_desired = int(amount1 * (10 ** token1_decimals))

    mint_params = {
        "token0": web3.to_checksum_address(token0),
        "token1": web3.to_checksum_address(token1),
        "fee": 500,
        "tickLower": -887270,
        "tickUpper": 887270,
        "amount0Desired": amount0_desired,
        "amount1Desired": amount1_desired,
        "amount0Min": 0,
        "amount1Min": 0,
        "recipient": web3.to_checksum_address(address),
        "deadline": int(time.time()) + 600
    }

    token_contract = web3.eth.contract(address=web3.to_checksum_address(POTITION_MANAGER_ADDRESS), abi=ADD_LP_CONTRACT_ABI)

    lp_data = token_contract.functions.mint(mint_params)

    estimated_gas = lp_data.estimate_gas({"from": address})
    max_priority_fee = web3.to_wei(1, "gwei")
    max_fee = max_priority_fee

    lp_tx = lp_data.build_transaction({
        "from": address,
        "gas": int(estimated_gas * 1.2),
        "maxFeePerGas": int(max_fee),
        "maxPriorityFeePerGas": int(max_priority_fee),
        "nonce": web3.eth.get_transaction_count(address, "pending"),
        "chainId": web3.eth.chain_id,
    })

    signed_tx = web3.eth.account.sign_transaction(lp_tx, account)
    raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash = web3.to_hex(raw_tx)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    block_number = receipt.blockNumber

    return tx_hash, block_number