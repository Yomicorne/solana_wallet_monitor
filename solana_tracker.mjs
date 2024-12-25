import fetch from 'node-fetch';
import TelegramBot from 'node-telegram-bot-api';
import { Connection, PublicKey } from '@solana/web3.js';

// Your credentials
const alchemyApiUrl = 'https://solana-mainnet.g.alchemy.com/v2/J0E1ahfrm15BBS0cEYSROfiyRW8S3Ar3';
const telegramBotToken = '7769169396:AAH7IO0XAFFuTEPoKMVSYtKTwfpaQfpB9bg';
const telegramChatId = '6297756292';
const walletToMonitor = '71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC';

const coinGeckoApiUrl = 'https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd';

const bot = new TelegramBot(telegramBotToken, { polling: true });

// Solana connection and public key
const connection = new Connection('https://api.mainnet-beta.solana.com', 'confirmed');
const publicKey = new PublicKey(walletToMonitor);

// Log the wallet address being monitored
console.log(`Monitoring wallet: ${walletToMonitor}`);

async function fetchTransactionData(signature) {
    const response = await fetch(`${alchemyApiUrl}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            jsonrpc: "2.0",
            id: 1,
            method: "getTransaction",
            params: [signature, { encoding: "json" }],
        }),
    });
    const data = await response.json();
    return data.result;
}

async function fetchTokenPrice() {
    const response = await fetch(coinGeckoApiUrl);
    const data = await response.json();
    return data.solana.usd;
}

// Send Telegram notification
async function sendTransactionNotification(signature, type, amount, usdValue) {
    const message = `New Transaction Detected:\n🔹 Action: ${type}\n🔹 Token: SOL\n🔹 Amount: ${amount} SOL (~$${usdValue.toFixed(2)})\n🔗 [View Transaction on Solscan](https://solscan.io/tx/${signature})`;
    await bot.sendMessage(telegramChatId, message);
}

// Listen for transaction logs on the monitored wallet
async function listenForTransactions() {
    connection.onLogs(publicKey, async (logs, context) => {
        if (logs.err) {
            console.log('Error in transaction log:', logs.err);
            return;
        }

        console.log('New transaction log detected...');

        // Fetch the signature from the logs (just an example, modify as necessary)
        const signature = logs.signature;

        // Fetch the transaction details
        const transaction = await fetchTransactionData(signature);
        if (transaction) {
            const tokenPrice = await fetchTokenPrice();
            
            // Check if instructions exist and parse type correctly
            let type = 'Unknown';
            if (transaction.transaction.message.instructions && transaction.transaction.message.instructions[0].parsed) {
                type = transaction.transaction.message.instructions[0].parsed.type || 'Unknown';
            }

            // Ensure the amount is correctly calculated
            const amount = transaction.meta?.postBalances[0] / Math.pow(10, 9) || 0; // Adjust decimals for SOL
            const usdValue = amount * tokenPrice;

            // Send the notification
            sendTransactionNotification(signature, type, amount, usdValue);
        }
    });
}

// Start listening for logs
listenForTransactions();
