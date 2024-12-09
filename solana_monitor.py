import asyncio
import json
import websockets

WS_URL = "YOUR_WEBSOCKET_URL_HERE"  # Replace with your actual WebSocket URL

async def subscribe_to_logs():
    async with websockets.connect(WS_URL) as websocket:
        # Send subscription request
        subscription_request = {
            "jsonrpc": "2.0",
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": ["YOUR_WALLET_ADDRESS_HERE"]  # Replace with the wallet address you want to monitor
                }
            ],
            "id": 1
        }
        
        await websocket.send(json.dumps(subscription_request))

        while True:
            response = await websocket.recv()
            print("Received data:", response)
            # Here you can process the received logs as needed
            # For example, you can parse and check for specific logs or events

# Run the async function
if __name__ == "__main__":
    asyncio.run(subscribe_to_logs())
