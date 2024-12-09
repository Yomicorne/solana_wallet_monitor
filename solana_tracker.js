// Import necessary libraries
const { Connection, PublicKey } = require("@solana/web3.js"); // Solana blockchain interaction
const axios = require("axios"); // HTTP requests for Telegram

// Replace with your details
const TELEGRAM_BOT_TOKEN = "7769169396:AAH7IO0XAFFuTEPoKMVSYtKTwfpaQfpB9bg";
const TELEGRAM_CHAT_ID = "6297756292";
const WALLET_TO_MONITOR = "71CPXu3TvH3iUKaY1bNkAAow24k6tjH473SsKprQBABC";

// Solana RPC connection
const SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"; // Public RPC URL
const connection = new Connection(SOLANA_RPC_URL, "confirmed");

// Send a message to Telegram
async function sendTelegramMessage(message) {
    try {
        const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
        await axios.post(telegramUrl, {
            chat_id: TELEGRAM_CHAT_ID,
            text: message,
            parse_mode: "HTML",
        });
    } catch (error) {
        console.error("Failed to send Telegram message:", error.response?.data || error.message);
    }
}

// Format transaction data for Telegram
function formatTelegramMessage(transaction, signature) {
    if (!transaction || !transaction.meta) {
        return `Transaction detected, but details are incomplete. Please check manually:
🔗 <a href="https://solscan.io/tx/${signature}">View Transaction on Solscan</a>`;
    }

    const { meta } = transaction;
    const action = meta.preBalances[0] < meta.postBalances[0] ? "Buy" : "Sell";
    const amount = Math.abs((meta.postBalances[0] - meta.preBalances[0]) / 1e9); // Convert lamports to SOL
    const tokenSymbol = "SOL"; // Assuming SOL
    const usdValue = (amount * 20).toFixed(2); // Mock USD conversion rate

    return `
New Transaction Detected:
🔹 <b>Action:</b> ${action}
🔹 <b>Amount:</b> ${amount} ${tokenSymbol} (~$${usdValue})
🔗 <a href="https://solscan.io/tx/${signature}">View Transaction on Solscan</a>
    `;
}

// Monitor a specific wallet
async function monitorWallet(wallet) {
    console.log(`Monitoring wallet: ${wallet}`);
    const walletPublicKey = new PublicKey(wallet);
    let latestSignature = null;

    setInterval(async () => {
        try {
            // Fetch the latest transaction signatures
            const signatures = await connection.getSignaturesForAddress(walletPublicKey, { limit: 1 });

            // If there's a new transaction
            if (signatures.length > 0 && signatures[0].signature !== latestSignature) {
                latestSignature = signatures[0].signature;

                // Delay to allow transaction to propagate
                await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds

                // Fetch transaction details
                const transaction = await connection.getTransaction(latestSignature, {
                    commitment: "confirmed",
                    maxSupportedTransactionVersion: 0
                });

                // Format and send the message
                const telegramMessage = formatTelegramMessage(transaction, latestSignature);
                await sendTelegramMessage(telegramMessage);
            }
        } catch (error) {
            console.error(`Error monitoring wallet ${wallet}:`, error.message);
        }
    }, 15000); // Poll every 15 seconds
}

// Start monitoring
monitorWallet(WALLET_TO_MONITOR);
