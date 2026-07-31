# Instagram Access Token — Full Generation & Renewal Guide

This documents exactly how `INSTAGRAM_ACCESS_TOKEN` (+ `INSTAGRAM_USER_ID`) is generated for this
bot, including every pitfall we actually hit while setting it up. Follow this top to bottom when
generating the token for the first time, or when it expires (~60 days) and needs renewal.

## What we're building

The bot needs a **long-lived Facebook Page Access Token** (not a short-lived one, not a User
token, not the separate "Instagram app" product credentials). That Page must be linked to the
`@nibthefridgegoblin` Instagram Professional account. A Page token obtained this way lasts ~60
days and can be re-exchanged for another ~60 days indefinitely, without ever needing to repeat the
full OAuth flow — see [Renewal](#renewal-before-it-expires) at the bottom.

## 1. Find the correct App ID + App Secret

Facebook Apps that have the **"Instagram API with Instagram Login"** product added get a
*separate*, product-specific "Instagram app ID" / "Instagram app secret" shown on that product's
setup page. **Do not use those** — they only work for direct Instagram-Login OAuth
(`api.instagram.com`), not the Page-token flow below, and using them causes:

```
{"error":{"message":"Error validating application. Cannot get application info due to a system error.","type":"OAuthException","code":101}}
```

Instead, use the app's **main** credentials:

1. [developers.facebook.com/apps](https://developers.facebook.com/apps/) → open your app
2. Left sidebar → **Settings → Basic**
3. Copy **App ID** and **App Secret** (click "Show" on the secret, re-enter your Facebook
   password if prompted) from the top of *this* page

Sanity-check the pair is valid before going further:

```bash
curl -s "https://graph.facebook.com/oauth/access_token?client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&grant_type=client_credentials"
```

Expect `{"access_token":"...|...","token_type":"bearer"}`. If you get the same "system error"
above, you still have the wrong App ID/Secret pair (wrong app, or a typo).

## 2. Generate a short-lived token in Graph API Explorer

1. Open [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer/)
2. **Meta App** dropdown → the app from step 1
3. **"User or Page"** dropdown → **Get Token → Get User Access Token**
4. Check these 4 permissions (search box to find each): `instagram_basic`,
   `instagram_content_publish`, `pages_show_list`, `pages_read_engagement`
5. Click **Generate Access Token**

**Watch out:** if you've authorized this app before, Facebook shows *"Continue as [You]? You've
previously linked [App] to Facebook. Would you like to continue with your previous settings?"*.
Clicking **Continue** silently reuses the old grant and **skips the Page picker**, which later
makes `/me/accounts` return `{"data":[]}` even though everything else looks fine. Always click
**Edit settings** instead so you get the full flow, including:

> "Choose the Pages you want [App] to access" → make sure the Page linked to
> `@nibthefridgegoblin` is checked → **Continue**

Copy the resulting token from the **Access Token** field.

## 3. Exchange it for a long-lived User token

```bash
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

Returns `{"access_token":"...","expires_in":5184000}` (~60 days). This is a **User** token —
still one step away from what we need.

## 4. Get the Page's own access token

The "obvious" way is:

```bash
curl -s "https://graph.facebook.com/v21.0/me/accounts?fields=name,access_token,instagram_business_account&access_token=YOUR_LONG_LIVED_USER_TOKEN"
```

**This can return `{"data":[]}`** even when everything is authorized correctly — Meta's "New
Pages Experience" pages don't always get listed by `/me/accounts`. If that happens, get the Page
ID a different way and query it directly:

```bash
curl -s "https://graph.facebook.com/debug_token?input_token=YOUR_USER_TOKEN&access_token=YOUR_APP_ID%7CYOUR_APP_SECRET"
```

Look at `granular_scopes` in the response — the `target_ids` next to `pages_show_list` is your
Page ID. Then query that Page node directly:

```bash
curl -s "https://graph.facebook.com/v21.0/PAGE_ID?fields=name,access_token,instagram_business_account&access_token=YOUR_LONG_LIVED_USER_TOKEN"
```

This returns the Page's `name`, its `access_token`, and `instagram_business_account.id` (this ID
is your `INSTAGRAM_USER_ID` — confirm it matches).

## 5. Exchange the Page token too (important, easy to miss)

If the User token you used in step 4 was the **short-lived** one (not yet exchanged), the Page
token you get back **inherits that short lifetime** — it can expire in as little as an hour even
though it "looks" like a normal Page token. Always run one more exchange on the Page token itself
before using it:

```bash
curl -s "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_PAGE_TOKEN"
```

Verify the final result:

```bash
curl -s "https://graph.facebook.com/debug_token?input_token=FINAL_TOKEN&access_token=YOUR_APP_ID%7CYOUR_APP_SECRET"
```

Confirm `"type":"PAGE"` and `"expires_at"` is ~60 days out (convert with
`date -r <timestamp> -u`).

## 6. Update the token everywhere

- `bot/.env` → `INSTAGRAM_ACCESS_TOKEN=` (the final token from step 5)
- GitHub → repo → **Settings → Secrets and variables → Actions** → `INSTAGRAM_ACCESS_TOKEN` →
  **Update secret** → paste the same value

`INSTAGRAM_USER_ID` (the Instagram Business Account ID from step 4) does **not** normally change
between renewals — you only need to touch `INSTAGRAM_ACCESS_TOKEN`.

## Renewal (before it expires)

The token lasts ~60 days from `data-access-expires-at`/`expires_at`. Put a calendar reminder a
few days before expiry, then just repeat **steps 2–6** above with a fresh short-lived token
(you don't need to touch App settings again — the App ID/Secret stay the same forever).

## Common errors, decoded

| Error | Meaning |
|---|---|
| `Error validating application. Cannot get application info due to a system error.` | Wrong App ID/Secret pair — likely used the Instagram-product-specific ID instead of the main app's (Settings → Basic) ID. |
| `Error validating access token: Session has expired on ...` | You're using a short-lived token (expires in ~1-2 hours) instead of an exchanged long-lived one. |
| `Invalid grant_type: 'EAA...'` | Copy-paste slipped a token into the `grant_type` parameter instead of `client_credentials`/`fb_exchange_token`. |
| `{"data": []}` from `/me/accounts` | Either the "Continue with previous settings" dialog skipped the Page picker (redo with "Edit settings"), or the Page just isn't listed there (New Pages Experience) — query the Page node by ID directly instead (step 4). |
| Page token expires in a few hours despite following all steps | It was derived from a short-lived User token — exchange the Page token itself too (step 5). |
