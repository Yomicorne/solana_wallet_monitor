import asyncio
import base64
import requests
from solana.rpc.api import Client
from solana.rpc.websocket_api import connect
from solana.publickey import PublicKey
from solana.transaction import Transaction, TransactionInstruction
from solana.keypair import Keypair
from solana.rpc.types import TxOpts
from solana.message import Message
from datetime import datetime
import pytz

# RPC and WebSocket endpoints (Mainnet)
RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
WS_ENDPOINT = "wss://api.mainnet-beta.solana.com"

# Your private key (replace with your actual secret key)
SECRET_KEY = [37, 235, 101, 169, 91, 99, 74, 217, 34, 30, 231, 127, 250, 136, 205, 20, 16, 28, 193, 191, 99, 7, 168, 138, 132, 131, 171, 19, 190, 245, 130, 114, 236, 133, 110, 40, 190, 71, 47, 181, 202, 84, 30, 64, 237, 78, 204, 207, 1, 221, 167, 161, 39, 15, 193, 140, 27, 69, 234, 90, 227, 28, 77, 212]
kp = Keypair.from_secret_key(bytes(SECRET_KEY))

# Telegram Bot credentials
telegramBotToken = '7769169396:AAH7IO0XAFFuTEPoKMVSYtKTwfpaQfpB9bg'  
telegramChatId = '6297756292'  

# Wallets you want to monitor (Replace with the wallet you want to monitor)
WATCHED_WALLETS = [
    PublicKey("71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC") 
]

# Solana client
client = Client(RPC_ENDPOINT)

# Function to send Telegram notification
def send_telegram_notification(message):
    telegram_url = f"https://api.telegram.org/bot{telegramBotToken}/sendMessage"
    params = {
        'chat_id': telegramChatId,
        'text': message,
        'parse_mode': 'Markdown'
    }
    response = requests.get(telegram_url, params=params)
    return response.json()

# Function to get formatted date and time for Warsaw, Poland
def get_poland_time():
    warsaw_tz = pytz.timezone("Europe/Warsaw")
    current_time = datetime.now(warsaw_tz)
    return current_time.strftime("%d-%m-%Y %H:%M:%S")

# Function to handle logs and reconnect on failure
async def handle_logs():
    while True:
        try:
            async with connect(WS_ENDPOINT) as ws:
                # Subscribe to logs
                subscription_id = await ws.logs_subscribe()
                print(f"Subscribed to logs with ID: {subscription_id}")

                async for msg in ws:
                    # Display the current time in Poland
                    current_time = get_poland_time()
                    print(f"Checking for transactions... | Time: {current_time}")

                    # Change here to access msg directly
                    if hasattr(msg, 'result'):
                        notification = msg.result
                        if isinstance(notification, dict) and notification.get("type") == "logsNotification":
                            sig = notification["result"]["value"]["signature"]
                            tx_info = client.get_transaction(sig)
                            if tx_info.get("result") is None:
                                continue

                            result = tx_info["result"]
                            if not result or "transaction" not in result:
                                continue

                            transaction_json = result["transaction"]
                            message_b64 = transaction_json["message"]
                            signatures = transaction_json["signatures"]
                            account_keys = transaction_json["message"]["accountKeys"]

                            # Check if any of the involved accounts is in the watched list
                            involved_accounts = [PublicKey(acc) for acc in account_keys]
                            if not any(acc in WATCHED_WALLETS for acc in involved_accounts):
                                continue

                            print(f"Detected a transaction from a watched wallet: {sig}")

                            # Decode the message
                            raw_message = base64.b64decode(message_b64)
                            message = Message.deserialize(raw_message)

                            # Extract token details and action type
                            token_name = "Unknown Token"
                            amount_spent = 0
                            amount_received = 0
                            action_type = "Unknown"

                            for ci in message.instructions:
                                if ci.program_id_index == 2:  # Assuming token program
                                    token_name = message.account_keys[ci.accounts[0]].to_base58().decode('utf-8')
                                    amount_spent = int.from_bytes(ci.data[:8], 'little') / (10 ** 9)  # Assuming 9 decimals
                                    amount_received = int.from_bytes(ci.data[8:16], 'little') / (10 ** 9)

                                    # Check if it's a buy or sell
                                    if "buy" in str(ci.data):
                                        action_type = "Buy"
                                    elif "sell" in str(ci.data):
                                        action_type = "Sell"

                            # Send Telegram notification with transaction details
                            message = f"New Transaction Detected:\n" \
                                      f"🔹 **Action:** {action_type}\n" \
                                      f"🔹 **Token:** {token_name}\n" \
                                      f"🔹 **Spent:** {amount_spent} SOL\n" \
                                      f"🔹 **Received:** {amount_received} {token_name}\n" \
                                      f"🔗 [View Transaction on Solscan](https://solscan.io/tx/{sig})"
                            send_telegram_notification(message)

                            # Create and send the mirrored transaction (as before)
                            new_tx = Transaction()
                            for ix in message.instructions:
                                new_tx.add(ix)

                            # Sign the transaction with your keypair
                            new_tx.sign(kp)

                            # Send the new transaction to the network
                            try:
                                send_resp = client.send_transaction(new_tx, kp, opts=TxOpts(skip_confirmation=False))
                                print("Repeated transaction sent:", send_resp)

                            except Exception as e:
                                print("Error while repeating the transaction:", e)

        except Exception as e:
            print(f"Connection error: {e}. Reconnecting...")
            await asyncio.sleep(5)  # Wait before attempting to reconnect

# Main entry point for running the script
async def main():
    await handle_logs()

if __name__ == "__main__":
    asyncio.run(main())
