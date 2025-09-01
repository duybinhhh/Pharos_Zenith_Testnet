from utils.helpers import get_web3_with_check
from config.constants import WPHRS_CONTRACT_ADDRESS,ERC20_CONTRACT_ABI

wrap_amount=0

def perform_wrapped(account:str, address:str, use_proxy:bool,proxy:str,wrap_amount:float):
    web3 = get_web3_with_check(address, use_proxy,proxy)
    contract_address = web3.to_checksum_address(WPHRS_CONTRACT_ADDRESS)
    token_contract = web3.eth.contract(address=contract_address,abi=ERC20_CONTRACT_ABI)
    amount_to_wei = web3.to_wei(wrap_amount,"ether")
    wrap_data = token_contract.functions.deposit()
    estimated_gas = wrap_data.estimate_gas({"from":address,"value":amount_to_wei})

    max_priority_fee = web3.to_wei(1, "gwei")
    max_fee = max_priority_fee

    wrap_tx = wrap_data.build_transaction({
        "from": address,
        "value": amount_to_wei,
        "gas": int(estimated_gas * 1.2),
        "maxFeePerGas": int(max_fee),
        "maxPriorityFeePerGas": int(max_priority_fee),
        "nonce": web3.eth.get_transaction_count(address, "pending"),
        "chainId": web3.eth.chain_id,
    })

    signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
    raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    tx_hash = web3.to_hex(raw_tx)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    block_number = receipt.blockNumber

    return tx_hash, block_number

def perform_unwrapped(account: str, address: str, use_proxy: bool,proxy:str,wrap_amount:float):
        try:
            web3 = get_web3_with_check(address, use_proxy,proxy)

            contract_address = web3.to_checksum_address(WPHRS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(wrap_amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            return None,None