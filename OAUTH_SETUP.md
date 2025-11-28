# OAuth 2.0 Setup & Configuration Guide

## Overview

This guide covers OAuth 2.0 authentication setup for all third-party APIs used by EntertainmentBuddy.

## Prerequisites

- Zoho SalesIQ account with admin access
- Access to Zoho API Console
- Individual API accounts created for each third-party service

## Step-by-Step Setup

### 1. TMDB (The Movie Database)

**Purpose**: Movie recommendations, ratings, genres

**Setup Steps**:
1. Go to https://www.themoviedb.org/settings/api
2. Create free account if needed
3. Request API key
4. Generate API key for your application
5. Copy API key to secure location

**Connection Details**:
- Base URL: `https://api.themoviedb.org/3/`
- Auth Type: API Key (Query parameter)
- Key Parameter: `api_key`
- Rate Limit: 40 requests/10 seconds

**Sample Request**:
```bash
curl "https://api.themoviedb.org/3/discover/movie?api_key=YOUR_KEY&with_genres=28&vote_average.gte=7"
```

### 2. Ticketmaster API

**Purpose**: Event booking, concerts, talkshows, movie shows

**Setup Steps**:
1. Go to https://developer.ticketmaster.com/
2. Sign up for developer account
3. Create new app
4. Generate Consumer Key & Secret
5. Choose OAuth 2.0 authentication

**Connection in Zoho**:
```
Connection Name: ticketmaster_oauth_connection
Auth Type: OAuth 2.0
Client ID: YOUR_CONSUMER_KEY
Client Secret: YOUR_CONSUMER_SECRET
Authorize URL: https://auth.ticketmaster.com/oauth/authorize
Token URL: https://auth.ticketmaster.com/oauth/token
Scope: events
```

**Base URL**: `https://app.ticketmaster.com/discovery/v2/`

### 3. Zomato API

**Purpose**: Restaurant and food recommendations

**Setup Steps**:
1. Go to https://developers.zomato.com/
2. Create account
3. Create new API key
4. Choose your app details

**Connection Details**:
- Base URL: `https://api.zomato.com/api/v2.1/`
- Auth Type: API Key (Header)
- Header: `user-key: YOUR_API_KEY`
- Rate Limit: 100 requests/minute (Lite) / Higher for premium

### 4. OpenAI API

**Purpose**: AI-powered mood detection and intelligent recommendations

**Setup Steps**:
1. Go to https://platform.openai.com/api-keys
2. Create OpenAI account or sign in
3. Create new API key
4. Set usage limits for cost control

**Connection Details**:
```
Base URL: https://api.openai.com/v1/
Auth: Bearer Token
Token: sk-YOUR_API_KEY
Model: gpt-3.5-turbo
Max Tokens: 500-2000 (adjustable)
```

## Zoho Connection Configuration

### Creating Connections in Zoho

1. **Go to Zoho Console**
   - Settings → APIs & Extensions → Connections
   - Click "Create New Connection"

2. **For OAuth 2.0 APIs (Ticketmaster)**
   ```
   Name: ticketmaster_oauth
   Auth Type: OAuth 2.0
   - Client ID: YOUR_ID
   - Client Secret: YOUR_SECRET
   - Auth URL: https://auth.ticketmaster.com/oauth/authorize
   - Token URL: https://auth.ticketmaster.com/oauth/token
   - Redirect URI: https://accounts.zoho.com/oauth/callback (auto)
   - Scope: events (space-separated)
   ```

3. **For API Key APIs (TMDB, Zomato)**
   ```
   Name: api_key_connection
   Auth Type: API Key
   - Key Name: api_key (or user-key for Zomato)
   - Key Value: YOUR_KEY
   - Location: Query Parameter (or Header)
   ```

4. **Test Connection**
   - Click "Test Connection"
   - Verify successful authentication
   - Note the Connection ID for use in Plugs

## Connection IDs to Update in Code

After creating connections, update these in your bot scripts:

```deluge
// In plugs/get_movie_suggestions.dlz
connection: "tmdb_oauth_connection"

// In plugs/get_events_near_me.dlz
connection: "ticketmaster_oauth_connection"

// In plugs/get_food_suggestions.dlz
connection: "zomato_api_connection"

// In main bot handler
connection: "openai_oauth_connection"
```

## Security Best Practices

✅ **Do's**:
- Store API keys in Zoho Connection, not in code
- Use separate API keys per environment (Dev, Test, Prod)
- Set rate limits and monitoring alerts
- Use API key rotation policies
- Enable request logging for audit trails

❌ **Don'ts**:
- Never hardcode API keys in scripts
- Don't commit credentials to GitHub
- Don't share API keys via email or chat
- Don't use production keys for testing
- Don't disable OAuth 2.0 verification

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" | Verify API key/secret correct in Connection |
| "Rate limit exceeded" | Add exponential backoff retry logic |
| "CORS error" | Not applicable - Zoho handles backend calls |
| "Expired token" | Zoho auto-refreshes OAuth 2.0 tokens |
| "Redirect URI mismatch" | Ensure callback URL matches Zoho's setting |

## Testing Connections

```deluge
// Test script to verify connections
response = invokeurl(
    [
        url: "https://api.themoviedb.org/3/genre/movie/list",
        type: "GET",
        connection: "tmdb_oauth_connection"
    ]
);

if(response.get("statusCode") == 200) {
    info "Connection successful";
} else {
    error "Connection failed: " + response.get("statusCode");
}
```

## API Quotas & Limits

| API | Free Tier | Limit |
|-----|-----------|-------|
| TMDB | Yes | 40 req/10s |
| Ticketmaster | Yes | Limited |
| Zomato | Yes | 100 req/min |
| OpenAI | Yes | $5/month free |

## Support & Documentation

- TMDB Docs: https://developers.themoviedb.org/3
- Ticketmaster: https://developer.ticketmaster.com/
- Zomato: https://developers.zomato.com/documentation
- OpenAI: https://platform.openai.com/docs/api-reference
- Zoho Connections: https://www.zoho.com/deluge/connections-framework.html
