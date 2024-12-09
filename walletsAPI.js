const express = require("express");
const bodyParser = require("body-parser");

const app = express();
const port = 3000;

let wallets = [];

// Middleware to parse JSON
app.use(bodyParser.json());

// Serve the HTML form for adding wallets
app.get("/", (req, res) => {
    res.send(`
        <html>
            <head><title>Wallets API</title></head>
            <body>
                <h1>Welcome to the Wallets API!</h1>
                <form action="/wallets" method="POST">
                    <label for="wallet">Wallet Address:</label>
                    <input type="text" id="wallet" name="wallet" required>
                    <button type="submit">Add Wallet</button>
                </form>
                <ul>
                    ${wallets.map(wallet => `<li>${wallet}</li>`).join("")}
                </ul>
            </body>
        </html>
    `);
});

// Endpoint to add wallets via form submission
app.post("/wallets", express.urlencoded({ extended: true }), (req, res) => {
    const wallet = req.body.wallet;
    if (wallet && !wallets.includes(wallet)) {
        wallets.push(wallet);
        res.redirect("/"); // Redirect back to the form
    } else {
        res.status(400).send("Invalid or duplicate wallet address.");
    }
});

// Endpoint to get the wallets
app.get("/wallets", (req, res) => {
    res.json(wallets);
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
