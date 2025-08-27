// Debug API endpoint for Vercel deployment testing
export default function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight request
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }

    const debugInfo = {
        status: 'success',
        message: 'Vercel API endpoint is working correctly! ✅',
        timestamp: new Date().toISOString(),
        method: req.method,
        url: req.url,
        headers: {
            'user-agent': req.headers['user-agent'],
            'host': req.headers['host'],
            'x-forwarded-for': req.headers['x-forwarded-for'],
            'x-vercel-id': req.headers['x-vercel-id'],
            'x-real-ip': req.headers['x-real-ip']
        },
        query: req.query,
        environment: {
            NODE_ENV: process.env.NODE_ENV,
            VERCEL: process.env.VERCEL,
            VERCEL_ENV: process.env.VERCEL_ENV,
            VERCEL_REGION: process.env.VERCEL_REGION,
            VERCEL_URL: process.env.VERCEL_URL
        },
        runtime: {
            platform: process.platform,
            nodeVersion: process.version,
            memoryUsage: process.memoryUsage(),
            uptime: process.uptime()
        }
    };

    // Test different response formats based on query parameter
    const format = req.query.format || 'json';
    
    switch (format) {
        case 'text':
            res.status(200).send(`Debug Info - Status: ${debugInfo.status}, Timestamp: ${debugInfo.timestamp}`);
            break;
        
        case 'html':
            res.status(200).send(`
                <!DOCTYPE html>
                <html>
                <head><title>Debug Info</title></head>
                <body>
                    <h1>Vercel API Debug</h1>
                    <pre>${JSON.stringify(debugInfo, null, 2)}</pre>
                </body>
                </html>
            `);
            break;
        
        case 'error':
            res.status(500).json({
                status: 'error',
                message: 'Intentional test error',
                timestamp: new Date().toISOString()
            });
            break;
        
        default:
            res.status(200).json(debugInfo);
    }
}