# Pharos Testnet Automation Bot

This is an automation bot for the **Pharos Testnet**, designed to simplify repetitive tasks across multiple wallets.

It supports the following features:

## Features

- ✅ Wrapped ↔ Unwrapped PHRS
- 🔁 Swap between **WPHRS, USDC, and USDT**
- 💧 Add Liquidity Pools (LP)
- 📆 Daily Check-In
- 🚰 Faucet Claim
- 📤 Single Token Transfer

Each wallet is executed with randomized delays and supports optional proxy configuration.

---

## Configuration

### 1. Clone the repository

```bash
git clone https://github.com/duybinhhh/Pharos_Zenith_Testnet.git
cd Pharos_Zenith_Testnet
```

### 2. Setup `settings.py`

```bash
cp config/settings_template.py config/settings.py
```

#### Edit `config/settings.py`

```bash
wallets = [
    {
        "address1": "0xYourWalletAddress",
        "private1": "your_private_key",
        "proxy": "ip:port:user:pass"  # or None
    },
    ...
]
```

⚠️ **Important:** Do not upload `settings.py` to GitHub – it is already ignored by `.gitignore`.

## 🚀 How to Use

### Start the CLI tool

```bash
python -m cli.main
```

You will be prompted with options:
Select Option:

- Wrapped - Unwrapped
- Swap WPHRS - USDC - USDT
- Add Liquidity Pool
- Check In
- Faucet Claim
- Single Transfer
- Choose [1-6]:

## 📂 Project Structure

```bash
pharos-bot/
├── cli/
│ └── main.py # CLI entry point
├── core/Zenith/
│ ├── checkin.py
│ ├── faucet.py
│ ├── liquidity.py
│ ├── swap.py
│ └── wrap_unwrap.py
│ transfer.py
├── config/
│ ├── settings_template.py # Example config
│ └── settings.py # User config (ignored in Git)
├── utils/
│ └── helpers.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 🧾 Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

## 🛡️ Security Recommendations

- Use a testnet-only wallet
- Store private keys securely - never upload to public respositories
- Use proxies (residential or datacenter) to avoid IP bans
- Add delay between actions to mimic human behavior

## 🛑 .gitignore

Your `.gitignore` should include:

```bash
config/settings.py
__pycache__/
```

This ensures private keys and compiled files are not pushed to Github

## 👨‍💻 Example Wallet Setup

```bash
wallets = [
    {
        "address1": "0x1234abcd...",
        "private1": "0xabc123...",
        "proxy": "123.123.123.123:8000:user:pass"  # or None
    }
]
```

## 🧪 Example Command Output (for addliquidity and swap)

```bash

🚀 Wallet 1: 0x1234abcd...
⚠️ No proxy!
✅ Successfully swapped WPHRS → USDC
💧 LP Added to WPHRS-USDT
🎉 Claimed faucet
```

## 📘 License

This tool is for educational and testing purposes only.

The authors are not responsible for any misuse or financial loss.

This project is licensed under the [MIT License](LICENSE).

## 🙋‍♂️ Author

Made with ❤️ by **DuyBinh**

Feel free to contribute, fork, or suggest improvements.
