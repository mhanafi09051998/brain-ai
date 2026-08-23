const express = require('express');
const compression = require('compression');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3021;

app.use(compression());
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/status', (req, res) => {
  res.json({
    status: 'online',
    app: 'Claudia Code Official Gateway',
    version: '5.0.0 Apex',
    engine: 'Claudia Max 4.0 Quantum Apex',
    oauthPortal: 'https://claudiacode.zolu.my.id/login',
    installWindows: 'irm https://get.zolu.my.id/win | iex',
    installUnix: 'curl -fsSL https://get.zolu.my.id | bash',
    repository: 'https://github.com/mhanafi09051998/claudia-code'
  });
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/oauth', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('[CLAUDIA CODE WEB] Portal & OAuth listening on http://0.0.0.0:' + PORT);
});
