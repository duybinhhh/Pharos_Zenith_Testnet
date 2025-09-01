from config.constants import ERC20_CONTRACT_ABI,RPC_URL
from web3 import Web3
import time 
import secrets
from eth_account import Account
from eth_utils import to_hex


def normalize_private_key(key:str)->str:
    return key if key.startswith("Ox") else f"0x{key}"

def get_web3_with_check(address: str, use_proxy: bool, proxy: str = "", retries=3, timeout=60):
    request_kwargs = {"timeout": timeout}

    if use_proxy and proxy:
        proxies = parse_proxy(proxy)
        request_kwargs["proxies"] = proxies

    for attempt in range(retries):
        try:
            web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs=request_kwargs))
            web3.eth.get_block_number()  # test RPC
            return web3
        except Exception as e:
            if attempt < retries - 1:
                print(f"🔄 RPC fail, retry ({attempt+1}/{retries})...")
                time.sleep(5)
                continue
            raise Exception(f"❌ Failed to Connect to RPC: {str(e)}")

def approving_token(web3, account, address, spender_address, contract_address, amount):
    try:
        address = web3.to_checksum_address(address)
        spender = web3.to_checksum_address(spender_address)
        token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=ERC20_CONTRACT_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_to_wei = int(amount * (10 ** decimals))
        allowance = token_contract.functions.allowance(address, spender).call()

        if allowance < amount_to_wei:
            approve_data = token_contract.functions.approve(spender, 2 ** 256 - 1)
            estimated_gas = approve_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(1, "gwei")
            max_fee = max_priority_fee

            approve_tx = approve_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            web3.eth.wait_for_transaction_receipt(raw_tx, timeout=300)
    except Exception as e:
        raise Exception(f"Approving Token Contract Failed: {str(e)}")


    
def check_balance(web3, address, token_address=""):
    try:
        address = web3.to_checksum_address(address)
        if token_address == "":
            balance_wei = web3.eth.get_balance(address)
            return web3.from_wei(balance_wei, "ether")
        else:
            token_contract = web3.eth.contract(
                address=web3.to_checksum_address(token_address),
                abi=ERC20_CONTRACT_ABI
            )
            decimals = token_contract.functions.decimals().call()
            balance = token_contract.functions.balanceOf(address).call()
            return balance / (10 ** decimals)
    except Exception as e:
        print(f"❌ Error check balance: {e}")
        return 0.0
    
def get_ip(session):
    try:
        r=session.get("https://api.ipify.org?format=json",timeout=5)
        return r.json().get("ip","Unknown")
    except:
        return "Unknown"
    
def parse_proxy(proxy_string: str) -> dict:
    """
    Convert string to dict {"http": url, "https": url}
    Example:
        '1.2.3.4:8080:user:pass'
        ->
        {
            "http": "http://user:pass@1.2.3.4:8080",
            "https": "http://user:pass@1.2.3.4:8080"
        }
    """
    parts = proxy_string.strip().split(":")
    if len(parts) == 4:
        host, port, user, pwd = parts
        proxy_url = f"http://{user}:{pwd}@{host}:{port}"
    elif len(parts) == 2:
        host, port = parts
        proxy_url = f"http://{host}:{port}"
    else:
        raise ValueError("Proxy format is invalid. Correct format: ip:port or ip:port:user:pass")

    return {"http": proxy_url, "https": proxy_url}


def generate_random_receiver():
        try:
            private_key_bytes = secrets.token_bytes(32)
            private_key_hex = to_hex(private_key_bytes)
            account = Account.from_key(private_key_hex)
            receiver = account.address
            
            return receiver
        except Exception as e:
            return None