# EUR/ARS Exchange Rate Monitor

Monitors Western Union's EUR to ARS exchange rate and sends Discord alerts when it exceeds your threshold.

## Setup

1. **Configure environment variables:**

```bash
cp .env.example .env
# Edit .env with your Discord webhook URL and threshold
```

2. **Run with Docker:**

```bash
docker build -t exchange-rate-monitor .
docker run --rm --env-file .env exchange-rate-monitor
```

## Testing

```bash
# Test all components
docker run --rm --env-file .env exchange-rate-monitor python test.py

# Test all notification types
docker run --rm --env-file .env exchange-rate-monitor python test.py --notifications
```

## GitHub Actions

Runs automatically every 6 hours. Configure in **Settings → Secrets and variables → Actions**:

**Secrets:**
- `DISCORD_WEBHOOK_URL`

**Variables:**
- `WESTERN_UNION_URL`
- `RATE_THRESHOLD`

## Environment Variables

```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
WESTERN_UNION_URL=https://www.westernunion.com/es/en/currency-converter/eur-to-ars-rate.html
RATE_THRESHOLD=1700.0
```

Optional: `MAX_RETRIES`, `DELAY_BETWEEN_REQUESTS`, `DEBUG_HTML`