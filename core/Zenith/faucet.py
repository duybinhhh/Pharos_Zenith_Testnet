from config.settings import sleep
from utils.helpers import normalize_private_key
from eth_account.messages import encode_defunct




def faucet(address, account, web3, session, use_proxy, proxy):
    
        message = "pharos"
        signable_message = encode_defunct(text=message)
        signature = web3.eth.account.sign_message(
        signable_message,
        private_key=normalize_private_key(account)
        ).signature.hex()

        sleep(2000)
        login = session.post(f"https://api.pharosnetwork.xyz/user/login?address={address}&signature={signature}", headers={
            "referer": "https://testnet.pharosnetwork.xyz/",
            "authorization": "Bearer null",
            "content-length": "0"
        })
        jwt = login.json().get("data", {}).get("jwt")
        sleep(3000)
        if not jwt:
            print("Invalid JWT")
            return

        faucet_claim = session.post(f"https://api.pharosnetwork.xyz/faucet/daily?address={address}", headers={
            "authorization": f"Bearer {jwt}",
            "referer": "https://testnet.pharosnetwork.xyz/"
        })
        result = faucet_claim.json()
        if result.get("code") == 0:
            print("✅ Faucet successfull:", result.get("msg"))
        else:
            print("❌ Faucet failed or already claimed:", result.get("msg"))


