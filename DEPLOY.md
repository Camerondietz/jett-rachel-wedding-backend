# Deploying to the Raspberry Pi (Docker)

## 1. One-time Pi setup
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # log out/in after this
```

## 2. Get the code onto the Pi
```bash
git clone <your-repo-url> jett-backend   # or scp the jett-backend folder over
cd jett-backend
```

## 3. Create the Cloudflare Tunnel
1. Cloudflare dashboard → Zero Trust → Networks → Tunnels → **Create a tunnel**.
2. Name it (e.g. `rsvp`), choose **Docker** as the connector — it shows a `docker run ... --token eyJ...` command. Copy just the token value.
3. Still in the tunnel setup, add a **Public Hostname**: `rsvp.rachelandjett.com` → Service `http://web:8000`.

## 4. Configure environment
```bash
cp .env.example .env
nano .env
```
Fill in:
- `SECRET_KEY` — generate one: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DEBUG=False`
- `TUNNEL_TOKEN` — the token from step 3

## 5. First-time database file
```bash
touch db.sqlite3   # only if it doesn't already exist — Docker needs a file to bind-mount over
```

## 6. Build and run
```bash
docker compose up -d --build
```

## 7. Migrate + create the bride/groom login
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## 8. Check it
- `https://rsvp.rachelandjett.com/admin/` — bride/groom login to view RSVPs
- `https://rsvp.rachelandjett.com/api/guests/search/?q=smith` — should return JSON

## Everyday commands
```bash
docker compose logs -f web          # tail app logs
docker compose logs -f cloudflared  # tail tunnel logs
docker compose restart web          # restart after an .env change
docker compose down                 # stop everything
```

## Deploying an update
```bash
git pull
docker compose up -d --build
docker compose exec web python manage.py migrate   # only if models changed
```

## Backing up RSVP data
`db.sqlite3` in this folder **is** the database — just copy it somewhere safe:
```bash
cp db.sqlite3 ~/backups/db-$(date +%F).sqlite3
```
