import requests
from config.settings import sleep
from utils.helpers import normalize_private_key
from web3 import Web3
from eth_account.messages import encode_defunct



def checkin(address, account, web3, session, use_proxy, proxy):
        message = "pharos"

        message_object = encode_defunct(text=message)

        signature = web3.eth.account.sign_message(
            message_object,
            private_key=normalize_private_key(account)
        ).signature.hex()

        sleep(2000)
        login_url = f"https://api.pharosnetwork.xyz/user/login?address={address}&signature={signature}"
        res = session.post(login_url, headers={
            "referer": "https://testnet.pharosnetwork.xyz/",
            "authorization": "Bearer null",
            "content-length": "0"
        })

        jwt = res.json().get("data",{}).get("jwt")
        if not jwt:
            print("Invalid JWT")
            return
        sleep(3000)

        checkin_url = f"https://api.pharosnetwork.xyz/sign/in?address={address}"
        res = session.post(checkin_url, headers={
            "authorization": f"Bearer {jwt}",
            "referer": "https://testnet.pharosnetwork.xyz/experience",
            "content-length": "0"
        })
        data = res.json() 
        if data.get("code") == 0:
            print("✅ Checkin successful:", data.get("msg"))
        else:
            print("❌ Checkin failed:", data.get("msg"))

        sleep(3000)

