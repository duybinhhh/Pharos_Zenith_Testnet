from config.settings import wallets, sleep
from config.constants import WPHRS_CONTRACT_ADDRESS, USDT_CONTRACT_ADDRESS, USDC_CONTRACT_ADDRESS
from core.Zenith.swap import perform_swap, generate_swap_option
from core.Zenith.wrap_unwrap import perform_wrapped, perform_unwrapped
from core.Zenith.liquidity import perform_add_liquidity, generate_add_lp_option
from core.Zenith.checkin import checkin
from core.Zenith.faucet import faucet
from core.transfer import transfer
from utils.helpers import check_balance, get_web3_with_check, parse_proxy,get_ip
import time
import random
from web3 import Web3
import requests


def print_question():
    while True:
        print("\nSelect Option:")
        print("1. Wrapped - Unwrapped")
        print("2. Swap WPHRS - USDC - USDT")
        print("3. Add Liquidity Pool")
        print("4. Check In")
        print("5. Faucet Claim")
        print("6. Single Transfer")
        try:
            option = int(input("Choose [1-6]: ").strip())
            if option in range(1, 7):
                return option
            else:
                print("Invalid option. Please choose 1-6.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def prepare_wallet(wallet):
    address = wallet["address1"]
    account = wallet["private1"]
    proxy = wallet.get("proxy", "")
    use_proxy = bool(proxy)

    web3 = get_web3_with_check(address, use_proxy, proxy)

    session = requests.Session()
    if proxy:
        session.proxies = parse_proxy(proxy)

    return address, account, web3, session, use_proxy, proxy


def main():
    while True:
        
        selected_option = print_question()

        if selected_option == 1:  # Wrap/Unwrap
            wrap_option = int(input("1. Wrap | 2. Unwrap: ").strip())

        elif selected_option == 2:  # Swap
            swap_count = int(input("How many swaps? ").strip())

            min_delay = int(input("Min delay (sec): ").strip())
            max_delay = int(input("Max delay (sec): ").strip())

        elif selected_option == 3:  # Add Liquidity
            add_lp_count = int(input("How many times? ").strip())
            min_delay = int(input("Min delay (sec): ").strip())
            max_delay = int(input("Max delay (sec): ").strip())

        elif selected_option == 6:  # Transfer
            transfer_amount = float(input("Enter amount to transfer: ").strip())
            number = int(input("Enter number of recipients: ").strip())
           


        for i, wallet in enumerate(wallets):
            
            address, account, web3, session, use_proxy, proxy = prepare_wallet(wallet)

            address = web3.to_checksum_address(address)

            print(f"\n🚀 Ví {i+1}: {address}")
            if proxy:
                get_ip_address = get_ip(session)
                print(f"🌐  IP: {get_ip_address}")
            else:
                print("⚠️  No proxy!")
            if selected_option == 1:
                native_before = check_balance(web3, address)
                wphrs_before = check_balance(web3, address, WPHRS_CONTRACT_ADDRESS)
                print(f"🔍 Before PHRS: {native_before:.4f}, WPHRS: {wphrs_before:.4f}")

                wrap_amount = float(input("Enter amount [e.g. 0.01]: ").strip())

                if wrap_amount > (wphrs_before if wrap_option == 2 else native_before):
                    print(f"❌ Not enough balance in {address}")
                    continue

                if wrap_option == 1:
                    tx_hash, _ = perform_wrapped(account, address, use_proxy, proxy, wrap_amount)
                    print(f"✅ Wrapped: https://testnet.pharosscan.xyz/tx/{tx_hash}")
                else:
                    tx_hash, _ = perform_unwrapped(account, address, use_proxy, proxy, wrap_amount)
                    print(f"✅ Unwrapped: https://testnet.pharosscan.xyz/tx/{tx_hash}")
                
                native_after = check_balance(web3, address)
                wphrs_after = check_balance(web3, address, WPHRS_CONTRACT_ADDRESS)
                print(f"🔍 After PHRS: {native_after:.4f}, WPHRS: {wphrs_after:.4f}")

            elif selected_option == 2:
                for j in range(swap_count):

                    usdc_before = check_balance(web3, address, USDC_CONTRACT_ADDRESS)
                    usdt_before = check_balance(web3, address, USDT_CONTRACT_ADDRESS)
                    wphrs_before = check_balance(web3, address, WPHRS_CONTRACT_ADDRESS)

                    print(f"🔍 Before USDC: {usdc_before:.4f}, USDT: {usdt_before:.4f}, WPHRS: {wphrs_before:.4f}")

                    wphrs_amount = round(random.uniform(wphrs_before/4, wphrs_before/2),2) if wphrs_before > 0 else 0
                    usdc_amount = round(random.uniform(usdc_before/4, usdc_before/2),0) if usdc_before > 0 else 0
                    usdt_amount = round(random.uniform(usdt_before/4, usdt_before/2),0) if usdt_before > 0 else 0
                    from_token, to_token, from_ticker, to_ticker, amount = generate_swap_option(
                        wphrs_amount, usdc_amount, usdt_amount
                    )
                    print(f"🔄 Wallets {i+1} Swap {from_ticker}->{to_ticker} | Amount: {amount:.4f}")

                    try:
                        perform_swap(web3, account, address, from_token, to_token, amount)
                    except Exception as e: 
                        print(f"❌ Error swap {from_ticker}->{to_ticker} (Attempt {j+1}): {e}")
                        continue

                    usdt_after = check_balance(web3, address, USDT_CONTRACT_ADDRESS)
                    wphrs_after = check_balance(web3, address, WPHRS_CONTRACT_ADDRESS)
                    usdc_after = check_balance(web3, address, USDC_CONTRACT_ADDRESS)
                    print(f"🔍 After USDC: {usdc_after:.4f}, USDT: {usdt_after:.4f}, WPHRS: {wphrs_after:.4f}")

                    delay = random.randint(min_delay, max_delay)
                    print(f"⏳ Wait {delay}s...\n")
                    time.sleep(delay)

            elif selected_option == 3:
                for j in range(add_lp_count):
                    add_lp_option, token0, token1, amount0, amount1, ticker0, ticker1 = generate_add_lp_option(web3, address, add_lp_count)
                    print(f"\n🧪 Ví {i+1} Add LP {ticker0}-{ticker1} (Attempt {j+1})")

                    token0_before = check_balance(web3, address, token0)
                    token1_before = check_balance(web3, address, token1)

                    print(f"🔍 Before {ticker0}: {token0_before:.4f}, {ticker1}: {token1_before:.4f}")


                    try:
                        tx_hash, _ = perform_add_liquidity(
                            account, address, add_lp_option, token0, token1, amount0, amount1, use_proxy, proxy
                        )
                        print(f"✅ Added LP: https://testnet.pharosscan.xyz/tx/{tx_hash}")
                    except Exception as e:
                        print(f"❌ Error Add LP {ticker0}-{ticker1} : {e}")
                        continue  


                    token0_after = check_balance(web3, address, token0)
                    token1_after = check_balance(web3, address, token1)

                    print(f"🔍 After {ticker0}: {token0_after:.4f}, {ticker1}: {token1_after:.4f}")

                    delay = random.randint(min_delay, max_delay)
                    print(f"⏳ Wait {delay}s...\n")
                    time.sleep(delay)

            elif selected_option == 4:
                checkin(address, account, web3, session, use_proxy, proxy)

            elif selected_option == 5:
                faucet(address, account, web3, session, use_proxy, proxy)

            elif selected_option == 6:
                transfer_amount = round(random.uniform(transfer_amount/4, transfer_amount/2),4)
                transfer(address, account, web3, session, use_proxy, proxy,transfer_amount,number)



if __name__ == "__main__":
    main()
