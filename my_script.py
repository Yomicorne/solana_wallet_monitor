import asyncio
import json
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey

# Solana WebSocket URL
SOLANA_WEBSOCKET_URL = "wss://api.mainnet-beta.solana.com"
WALLETS_TO_MONITOR = ["9XZLoRZKkV5gFnxDvk83WZ8QzX6TvC2tsc3eKc3ztdiD"]

async def monitor_wallets():
    """Monitor the specified wallets for transactions."""
    async with connect(SOLANA_WEBSOCKET_URL) as websocket:
        print("Connected to Solana WebSocket.")

        # Subscribe to account notifications for each wallet
        for wallet in WALLETS_TO_MONITOR:
            wallet_pubkey = Pubkey.from_string(wallet)
            await websocket.account_subscribe(wallet_pubkey)
            print(f"Subscribed to wallet: {wallet}")

        # Process account updates
        while True:
            # Wait for the next WebSocket message
            message = await websocket.recv()
            print(f"Received message: {message}")  # Log the raw message

            # Handle the SubscriptionResult object properly
            if hasattr(message, "result"):
                print(f"Subscription result ID: {message.result}")
            else:
                print(f"Unrecognized message format: {message}")

async def main():
    """Main entry point for the script."""
    try:
        await monitor_wallets()
    except KeyboardInterrupt:
        print("Monitoring stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
