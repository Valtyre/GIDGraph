# Windows Home Hosting Guide

This guide re-establishes the deployment shape already reflected in the repo:

- frontend at `https://www.gidgraph.com`
- backend API at `https://api.gidgraph.com`
- FastAPI bound to `127.0.0.1:8000`
- Nginx on Windows listening on `80` and `443`
- Nginx proxying `/api/` to `http://127.0.0.1:8000/api/`

The repo includes the supporting config in [`nginx/conf/nginx.conf`](../nginx/conf/nginx.conf), frontend API selection in [`frontend/src/lib/apiConfig.ts`](../frontend/src/lib/apiConfig.ts), and a Windows backend launcher in [`scripts/run-backend.ps1`](../scripts/run-backend.ps1).

## 1. Choose the Windows host

Use a Windows machine that:

- stays powered on when you want the API live
- is on your home LAN
- can get a stable LAN IP from your router

Reserve a DHCP lease in your router so the machine keeps the same local IP, for example `192.168.1.50`.

## 2. Check the current machine state

From the repo root, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check-home-hosting.ps1
```

This reports:

- local IPv4 addresses
- default gateway
- current public IP if it can be fetched
- DNS A records for `api.gidgraph.com`
- whether local ports `80`, `443`, and `8000` respond

Use that output to confirm whether DNS is already pointing at your current network.

## 3. Point DNS at the new network

In your DNS provider for `gidgraph.com`:

- point `api.gidgraph.com` to your current public IP
- keep `www.gidgraph.com` pointed at your frontend hosting target

If your public IP changes over time, you will need either:

- manual DNS updates
- dynamic DNS automation
- a tunnel or VPS instead of direct home hosting

## 4. Confirm your ISP allows inbound hosting

If port forwarding never works, the likely causes are:

- CGNAT
- ISP inbound port filtering
- double NAT from multiple routers

Signs of trouble:

- your router WAN IP does not match the public IP reported by `check-home-hosting.ps1`
- external port checks for `80` and `443` stay closed even after forwarding

If that happens, stop fighting the router and switch to a tunnel or VPS.

## 5. Recreate router forwarding

In your router admin panel, forward:

- TCP `80` -> Windows host LAN IP
- TCP `443` -> Windows host LAN IP

The repo config expects Nginx to own both ports directly.

If Windows Firewall blocks inbound traffic, create local allow rules with:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\open-firewall-ports.ps1
```

## 6. Start the backend locally

Install the Python dependencies, then launch the API from the repo root:

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File .\scripts\run-backend.ps1
```

Expected binding:

- `127.0.0.1:8000`

Local test:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
```

Expected response:

```json
{"Hello":"World"}
```

## 7. Configure and start Nginx

The repo already contains the intended config at [`nginx/conf/nginx.conf`](../nginx/conf/nginx.conf).

It is configured to:

- listen on `80` for `api.gidgraph.com`
- expose `/.well-known/acme-challenge/` for win-acme
- redirect other HTTP traffic to HTTPS
- listen on `443 ssl`
- proxy `/api/` to `http://127.0.0.1:8000/api/`

Before starting Nginx, confirm the certificate paths in `nginx/conf/nginx.conf` match where win-acme writes them on your machine.

If you installed Nginx under the repo copy, test the config with:

```powershell
.\nginx\nginx.exe -t -p "$PWD\nginx" -c conf/nginx.conf
```

Start it with:

```powershell
.\nginx\nginx.exe -p "$PWD\nginx" -c conf/nginx.conf
```

If you installed Nginx elsewhere, use that installation path instead.

## 8. Issue or renew TLS certificates with win-acme

The Nginx config expects certificate files like:

- `C:/ProgramData/win-acme/acme-v02.api.letsencrypt.org/Certificates/api.gidgraph.com-chain.pem`
- `C:/ProgramData/win-acme/acme-v02.api.letsencrypt.org/Certificates/api.gidgraph.com-key.pem`

That implies a Windows setup using win-acme with Let’s Encrypt.

When issuing the certificate:

- use `api.gidgraph.com`
- make sure port `80` is publicly reachable for the ACME HTTP challenge
- confirm the challenge root in Nginx matches win-acme’s path

## 9. Verify end to end

Local checks on the host:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/
```

External checks from mobile data or another network:

- `https://api.gidgraph.com/`
- `https://api.gidgraph.com/api/parse`

Also verify the frontend can call:

- `https://api.gidgraph.com/api/parse`
- `https://api.gidgraph.com/api/optimize_nl`
- `https://api.gidgraph.com/api/export_ginml`

## 10. Keep frontend production config aligned

The frontend production target should stay:

```env
NEXT_PUBLIC_PROD_API_BASE_URL=https://api.gidgraph.com
```

Relevant files:

- [`frontend/.env.example`](../frontend/.env.example)
- [`frontend/.env.local`](../frontend/.env.local)
- [`frontend/src/lib/apiConfig.ts`](../frontend/src/lib/apiConfig.ts)

## Troubleshooting

`Backend works on localhost:8000 but public HTTPS fails`

- check router forwarding
- check Windows firewall
- check Nginx is listening on `80` and `443`
- check DNS resolves to the current public IP

`win-acme cannot validate the domain`

- make sure DNS for `api.gidgraph.com` points to your public IP
- make sure port `80` reaches the Windows host
- make sure Nginx serves `/.well-known/acme-challenge/`

`DNS points correctly but external requests still fail`

- check for CGNAT or double NAT
- compare your router WAN IP to the public IP reported by the script

`Frontend still calls the wrong backend`

- inspect `frontend/.env.local`
- restart the frontend dev server after changing `NEXT_PUBLIC_*`
