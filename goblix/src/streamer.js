// ===================================================================
// GOBLIX STREAMING ENGINE (streamer.js)
// Native HTTP 206 Partial Content (Byte-Range Requests)
// Max ~65 lines • Zero External Dependencies
// ===================================================================

const fs = require('fs');
const path = require('path');

function streamVideoFile(req, res, filePath, contentType = 'video/mp4') {
  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File video tidak ditemukan di penyimpanan server');
      return;
    }

    const fileSize = stats.size;
    const range = req.headers.range;

    if (!range) {
      res.writeHead(200, {
        'Content-Length': fileSize,
        'Content-Type': contentType,
        'Accept-Ranges': 'bytes',
        'Cache-Control': 'public, max-age=3600'
      });
      fs.createReadStream(filePath).pipe(res);
      return;
    }

    // Parse Range: bytes=start-end
    const parts = range.replace(/bytes=/, '').split('-');
    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;

    if (start >= fileSize || end >= fileSize) {
      res.writeHead(416, {
        'Content-Range': `bytes */${fileSize}`,
        'Content-Type': 'text/plain'
      });
      res.end('Requested range not satisfiable');
      return;
    }

    const chunksize = (end - start) + 1;
    const fileStream = fs.createReadStream(filePath, { start, end });

    res.writeHead(206, {
      'Content-Range': `bytes ${start}-${end}/${fileSize}`,
      'Accept-Ranges': 'bytes',
      'Content-Length': chunksize,
      'Content-Type': contentType,
      'Cache-Control': 'no-cache'
    });

    fileStream.pipe(res);
  });
}

module.exports = { streamVideoFile };
