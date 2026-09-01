const express = require('express');
const path = require('path');
const app = express();
const PORT = 3500;

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, '127.0.0.1', () => {
    console.log(`🚀 CLAI Landing Page running securely on http://127.0.0.1:${PORT}`);
});
