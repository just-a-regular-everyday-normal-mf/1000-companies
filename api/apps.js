import { put, list } from '@vercel/blob';

export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  try {
    if (req.method === 'GET') {
      const { blobs } = await list({ prefix: 'apps.json' });
      const file = blobs.find(b => b.pathname === 'apps.json');
      if (!file) return res.status(200).json([]);
      const r = await fetch(file.url + '?t=' + Date.now(), { cache: 'no-store' });
      return res.status(200).send(await r.text());
    }
    if (req.method === 'PUT') {
      const body = typeof req.body === 'string' ? req.body : JSON.stringify(req.body);
      await put('apps.json', body, {
        access: 'public',
        addRandomSuffix: false,
        allowOverwrite: true,
        cacheControlMaxAge: 0,
        contentType: 'application/json',
      });
      return res.status(200).send('ok');
    }
    res.status(405).send('Method not allowed');
  } catch (e) {
    res.status(500).send('ERROR: ' + e.message);
  }
}
