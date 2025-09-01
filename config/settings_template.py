import time

def sleep(millis):
    time.sleep(millis/1000)

# You can add your wallet information and proxy here
wallets = [
    # Wallet 1
    {
        "address1":"your wallet address",
        "private1":"your private key",
        "proxy":"1.2.3.4:8080:user:pass or None"
    },
    # Wallet 2
    {
        "address1":"your wallet address",
        "private1":"your private key",
        "proxy":"1.2.3.4:8080:user:pass"
    },
    # Wallet 3,...
]