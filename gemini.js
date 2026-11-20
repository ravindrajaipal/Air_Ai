'use strict';

/**
 * Vercel Serverless Function: POST /api/gemini
 * Keeps GEMINI_API_KEY strictly on the server via process.env.GEMINI_API_KEY.
 * Enforces strict request validation, CORS preflight handling, security headers, and an 8s upstream timeout.
 */

const API_CONFIG = Object.freeze({
  MAX_PROMPT_LENGTH: 280,
  MAX_CITY_LENGTH: 60,
  MAX_PROFILE_LENGTH: 40,
  UPSTREAM_TIMEOUT_MS: 8000,
  GEMINI_MODEL: 'gemini-2.5-flash'
});

function clampFinite(value, min, max, fallback) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.min(max, Math.max(min, parsed)) : fallback;
}

module.exports = async function handler(req, res) {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Cache-Control', 'no-store');

  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    return res.status(204).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method Not Allowed. Use POST.' });
  }

  const body = req.body;
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return res.status(400).json({ error: 'Invalid JSON request body. Expected a JSON object.' });
  }

  const rawPrompt = typeof body.prompt === 'string' ? body.prompt.trim() : '';
  if (!rawPrompt || rawPrompt.length > API_CONFIG.MAX_PROMPT_LENGTH) {
    return res.status(400).json({
      error: `Invalid prompt. Must be a non-empty string up to ${API_CONFIG.MAX_PROMPT_LENGTH} characters.`
    });
  }

  const city = typeof body.city === 'string' && body.city.trim()
    ? body.city.trim().slice(0, API_CONFIG.MAX_CITY_LENGTH)
    : 'Delhi NCR';
  const aqi = clampFinite(body.aqi, 0, 500, 367);
  const pm25 = clampFinite(body.pm25, 0, 1000, 218);
  const profile = typeof body.profile === 'string' && body.profile.trim()
    ? body.profile.trim().slice(0, API_CONFIG.MAX_PROFILE_LENGTH)
    : 'family';

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return res.status(503).json({
      error: 'GEMINI_API_KEY environment variable is not configured on the server.',
      fallbackMode: 'Deterministic CPCB/WHO Rule Engine'
    });
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.UPSTREAM_TIMEOUT_MS);

  try {
    const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${API_CONFIG.GEMINI_MODEL}:generateContent?key=${encodeURIComponent(apiKey)}`;
    const upstream = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      signal: controller.signal,
      body: JSON.stringify({
        contents: [{
          parts: [{
            text: `You are VayuAI, an Indian Urban Air Quality & Winter Smog Assistant grounded in CPCB NAQI, CAQM GRAP, WHO guidelines, DIY MERV-13 CADR, and ITF-OECD transport data. City: ${city} (AQI ${aqi}, PM2.5 ${pm25} ug/m3). User Profile: ${profile}. User Question: ${rawPrompt}. Reply concisely in 3 sentences in English followed by a 2-sentence Hinglish summary and exact % impact.`
          }]
        }]
      })
    });
    clearTimeout(timeoutId);

    if (!upstream.ok) {
      return res.status(502).json({ error: `Upstream Gemini API returned HTTP ${upstream.status}` });
    }

    const data = await upstream.json();
    const text = data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    if (!text) {
      return res.status(502).json({ error: 'Empty response from upstream model.' });
    }
    return res.status(200).json({ text, sourceMode: 'Live Gemini 2.5 Flash API (Server Proxy)' });
  } catch (err) {
    clearTimeout(timeoutId);
    return res.status(504).json({ error: 'Upstream request timed out or failed.' });
  }
};
