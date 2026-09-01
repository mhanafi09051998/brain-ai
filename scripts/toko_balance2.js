const crypto = require('crypto');
const https = require('https');
require('dotenv').config();

const API_KEY = process.env.TOKOCRYPTO_API_KEY || '6cf116fC93452F0Aa6545edccf519a61Q9sc3W8O4fhpBYRmESraTJrgv2GQ0NiP';
const API_SECRET = process.env.TOKOCRYPTO_API_SECRET || '890F47BCE574881bfeE45C053006F30F8yJoh6748vmCh46peGSvDJHHCpnzwpFy';

function getBalances() {
  return new Promise((resolve) => {
    const timestamp = Date.now();
    const params = new URLSearchParams({
      recvWindow: 5000,
      timestamp: timestamp
    });

    const signature = crypto.createHmac('sha256', API_SECRET).update(params.toString()).digest('hex');
    params.append('signature', signature);

    const options = {
      hostname: 'www.tokocrypto.com',
      port: 443,
      path: `/api/v3/account?${params.toString()}`,
      method: 'GET',
      headers: {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          if (result.balances) {
            const usefulBalances = result.balances.filter(b => parseFloat(b.free) > 0 || parseFloat(b.locked) > 0);
            resolve({ success: true, balances: usefulBalances });
          } else {
            resolve({ success: false, error: result.msg || 'Unknown error', raw: data });
          }
        } catch (e) {
          resolve({ success: false, error: e.message, raw: data });
        }
      });
    });

    req.on('error', (err) => resolve({ success: false, error: err.message }));
    req.end();
  });
}

getBalances().then(res => console.log(JSON.stringify(res, null, 2)));
