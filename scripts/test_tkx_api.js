const crypto = require('crypto');
const https = require('https');
require('dotenv').config();

const API_KEY = process.env.TOKOCRYPTO_API_KEY;
const API_SECRET = process.env.TOKOCRYPTO_API_SECRET;

const timestamp = Date.now();
const queryString = `timestamp=${timestamp}`;
const signature = crypto.createHmac('sha256', API_SECRET).update(queryString).digest('hex');

const options = {
  hostname: 'www.tokocrypto.com',
  port: 443,
  path: `/api/v3/account?${queryString}&signature=${signature}`,
  method: 'GET',
  headers: {
    'X-MBX-APIKEY': API_KEY,
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});
req.end();
