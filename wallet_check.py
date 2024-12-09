from solana.publickey import PublicKey  # Correct import

def is_valid_solana_wallet(wallet_address):
    try:
        # Try to create a PublicKey object from the wallet address
        PublicKey(wallet_address)
        return True  # If no exception is raised, the wallet address is valid
    except Exception as e:
        return False  # If there's an exception, the wallet address is invalid

# Example wallet addresses to test
wallet_addresses = [
    "9XZLoRZKkV5gFnxDvk83WZ8QzX6TvC2tsc3eKc3ztdiD",
    "5h4cSkx3BzPhPnpdTgRhK8YkuyvqX4z7ujDPy9knBf8E",
    "6fNHTF5bVxKMiZ9h14tn6Hhr8QkRYA1fm7vV38kcs6N7",
    "2S7DFp66hsD6ivPBXke6p5je7rdXrxmj9m5M4Z2ALMeJ",
    "AyRzrd8gDdb7JJMtn9Vv6nzGsoGpTw9TChgv8GV6BGG3",
    "6TVdMtUSZpgC1fQ2UjG9v9ktQUcuaH2WhPnz22wCEXcu",
    "He4TZyGQXQUiYzNVpNyM9nWw17QGNh9i4aJ7pCswFJ6f",
    "D6U61rnXemNm6heJcLBkUYPF3PmwD3rQGnHkX6n6C2oV",
    "BEvGFohRUdcgsq8p7kUJ5iqgAwwgH9xx5ahV2KoK9uN8",
    "YAXH1Rk2kMEg9ctq5mCCrhj5STwBUn4X5cJ4i4mrdmka",
    "6F7P8PA7cqP8AyJbB9r4n2K42F5YzvBNn5hxyuYPo9tT"
]

# Check if each wallet address is valid
for wallet in wallet_addresses:
    if is_valid_solana_wallet(wallet):
        print(f"Valid wallet address: {wallet}")
    else:
        print(f"Invalid wallet address: {wallet}")
