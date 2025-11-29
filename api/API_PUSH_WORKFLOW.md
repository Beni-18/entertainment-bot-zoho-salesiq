# Zoho SalesIQ Bot API Push Workflow

## Complete Guide to Automated Bot Script Updates via REST API

### Quick Start

```bash
# 1. Install requirements
pip install requests

# 2. Copy and configure config template
cp api/config_example.json api/config.json

# 3. Add your Zoho credentials to config.json
# Get credentials from: https://accounts.zoho.com/developerconsole

# 4. Push your bot script
python3 api/push_bot_script.py \
  --org-id YOUR_ORG_ID \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --refresh-token YOUR_REFRESH_TOKEN \
  --script scripts/bot_v4.0.dlz \
  --bot-id 1094836000000008001
```

## API Endpoints

### GET /bots/{bot_id}/script
Retrieve current bot script

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "script": "... deluge code ..."
}
```

### PUT /bots/{bot_id}/script
Update bot script

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Payload:**
```json
{
  "script": "... deluge code ..."
}
```

**Success Response:**
```
Status: 200, 201, or 204
```

## OAuth 2.0 Setup

### Required Scopes
- `ZohoSalesIQ.ZohoBots.READ` - Read bot scripts
- `ZohoSalesIQ.ZohoBots.UPDATE` - Update bot scripts

### Getting Tokens

1. Register OAuth app at: https://accounts.zoho.com/developerconsole
2. Add scopes: `ZohoSalesIQ.ZohoBots.READ` + `ZohoSalesIQ.ZohoBots.UPDATE`
3. Get authorization code and exchange for refresh token
4. Use refresh token to get access tokens

### Token Exchange

**Endpoint:** `POST https://www.zohoapis.com/oauth/v2/token`

**Payload:**
```json
{
  "grant_type": "refresh_token",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "refresh_token": "your_refresh_token"
}
```

**Response:**
```json
{
  "access_token": "...",
  "expires_in": 3600,
  "token_type": "Bearer"
}
```

## JSON Payload Escaping

When sending multiline Deluge code in JSON:

- Newlines: `\n`
- Quotes: `\"`
- Backslashes: `\\`
- Tabs: `\t`
- Carriage returns: `\r`

**Example:**

Original code:
```
response = Map();
replies.add("test");
```

JSON escaped:
```json
{
  "script": "response = Map();\nreplies.add(\"test\");"
}
```

## Workflow Features

✅ **Automatic Backup**
- Current script backed up before each push
- Stored in `backups/` directory with timestamp

✅ **Auto-Rollback**
- On API failure, automatically restores from backup
- Keeps bot stable in production

✅ **Token Management**
- Automatic token refresh using refresh token
- Handles token expiration gracefully

✅ **Error Reporting**
- Detailed logging of all operations
- Clear error messages for debugging

## File Structure

```
api/
├── push_bot_script.py         # Main push script
├── API_PUSH_WORKFLOW.md       # This file
└── config_example.json        # Configuration template

backups/
└── bot_{bot_id}_backup_{timestamp}.dlz   # Auto-created backups

scripts/
├── bot_v3.0.dlz              # Current version
└── bot_v4.0.dlz              # Version to push
```

## Testing

### Dry Run (No Rollback)
```bash
python3 api/push_bot_script.py \
  --org-id YOUR_ORG_ID \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --token YOUR_ACCESS_TOKEN \
  --script scripts/bot_v4.0.dlz \
  --bot-id 1094836000000008001 \
  --no-rollback
```

### With Auto-Rollback (Default)
```bash
python3 api/push_bot_script.py \
  ... all args ...
```

## Verify After Push

1. Check bot preview chat in Zoho SalesIQ
2. Test key flows: menu options, follow-ups, termination
3. Verify API backup was created
4. Confirm GET /bots/{bot_id}/script returns new code

## Troubleshooting

### "Invalid access token"
- Refresh token may be expired
- Get new refresh token from OAuth console

### "API Error 4xx"
- Check JSON payload escaping
- Verify bot_id is correct
- Ensure scopes include READ and UPDATE

### "Rollback failed"
- Backup file may be corrupted
- Manually restore from Git version history
- Re-publish from Zoho UI as fallback

## Best Practices

1. **Always test locally first** - Syntax errors should be caught before push
2. **Keep backups in Git** - Commit working versions to repository
3. **Use meaningful version names** - bot_v4.0, bot_v4.1, etc.
4. **Test in preview** - Always test in bot preview after push
5. **Monitor logs** - Check script output for issues
6. **Gradual rollout** - Test on small portion first if possible

## Security

- **Never commit config.json** - Add to .gitignore
- **Store tokens securely** - Use environment variables
- **Rotate credentials regularly** - Update OAuth tokens
- **Validate scripts** - Run syntax check before push
