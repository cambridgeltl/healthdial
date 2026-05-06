# Deployment Guide

This guide deploys the healthcare dialogue annotation tool with Docker Compose.
It uses the production compose file in `deployment/docker-compose.yml`.

## 1. Architecture

The Compose stack contains four services:

- `client`: builds the React application and serves static files with Nginx.
- `server`: runs the Flask API with Gunicorn on port `5000` inside Docker.
- `web`: internal Nginx reverse proxy. It routes `/api/` and `/audio/` to the server and all other paths to the client.
- `nginx-proxy-manager`: public reverse proxy and HTTPS certificate manager. It forwards the public domain to `web:80`.

MongoDB can be either an external managed database or a self-hosted MongoDB container.
The self-hosted database is optional and is enabled with the `local-mongo` Compose profile.
An optional Mongo Express admin UI is available with the `mongo-admin` profile.
The OpenAI key is mounted from `deployment/secrets/openai.key`.

## 2. Prerequisites

Install these on the deployment host:

- Docker Engine
- Docker Compose v2
- Git
- A domain name pointing to the host public IP
- Access to an external MongoDB database, or enough local disk for a self-hosted MongoDB container
- An OpenAI API key file if ASR is enabled

Check the host ports before deployment:

```bash
sudo lsof -i :80 -i :81 -i :443
docker compose version
```

Ports `80`, `81`, and `443` must be available for Nginx Proxy Manager.

## 3. Security Preparation

Before using this branch in production, rotate any secrets that were previously committed.
At minimum, rotate:

- Flask/JWT `SECRET_KEY`
- MongoDB username and password
- OpenAI API key

Real `.env` files must stay out of Git. This repository tracks only `.env.example` files.

## 4. Prepare The Repository

Clone the repository and check out the deployment branch:

```bash
git clone <repository-url>
cd annotation_tool_healthcare_dialogue
git checkout deployment
```

Review the production task file you plan to use:

```bash
jq -r 'to_entries | length' server/config/en_task_dic.json
```

Use the matching task file for the target language:

- English: `server/config/production_en_task_dic.json`
- Arabic: `server/config/production_ar_task_dic.json`
- Spanish: `server/config/production_es_task_dic.json`
- Chinese: `server/config/production_zh_task_dic.json`

## 5. Configure Environment Variables

Create the deployment environment file:

```bash
cd deployment
cp .env.example .env
chmod 600 .env
```

Edit `deployment/.env`:

```bash
nano .env
```

Required values:

```env
SECRET_KEY=replace-with-a-long-random-secret
MONGO_URI=replace-with-your-mongodb-connection-string
KEY_PATH=/run/secrets/openai.key

MONGO_INITDB_ROOT_USERNAME=annotation_admin
MONGO_INITDB_ROOT_PASSWORD=replace-with-a-strong-password
MONGO_APP_DATABASE=annotation_tool_healthcare_dialogue
MONGO_EXPRESS_PORT=8081
MONGO_EXPRESS_USERNAME=admin
MONGO_EXPRESS_PASSWORD=replace-with-a-strong-password

TASK_PATH=/server/config/production_en_task_dic.json
TASK_LANGUAGE=English
TASK_DATASET=healthcare dialogue
TASK_THRESHOLD=75
ADMIN_EMAIL=admin@example.com

REACT_APP_SERVER_URL=https://eng.example.org
REACT_APP_TARGET_LANGUAGE=English
REACT_APP_CONTACT_NAME=Research Team
REACT_APP_CONTACT_EMAIL=research-team@example.com

SERVER_WORKERS=2
LOG_LEVEL=info
FLASK_DEBUG=false
APP_HTTP_PORT=8080
```

Notes:

- `SECRET_KEY` should be generated with `openssl rand -base64 42`.
- `MONGO_URI` selects the database mode. Use an external URI for managed MongoDB, or the internal `mongo` hostname for self-hosted MongoDB.
- `TASK_PATH` is a path inside the server container, not the host.
- `REACT_APP_SERVER_URL` must be the public origin users open in the browser.
- React variables are embedded at image build time. Rebuild the client after changing any `REACT_APP_*` value.

## 6. Choose The MongoDB Mode

Choose one of the following modes before starting the stack.

### Option A: External MongoDB

Use this mode if you already have MongoDB Atlas, DigitalOcean Managed MongoDB, or another hosted MongoDB service.

1. Create or choose a MongoDB database for this deployment.
2. Create a database user with read/write access to that database.
3. Add the deployment host IP to the database provider's allowlist if the provider requires it.
4. Set `MONGO_URI` in `deployment/.env` to the provider connection string.

Example shape:

```env
MONGO_URI=your-provider-connection-string
```

Then start the stack without a MongoDB profile:

```bash
docker compose --env-file .env up -d
```

### Option B: Self-Hosted MongoDB

Use this mode if you want Docker Compose to run MongoDB on the same host.
The MongoDB port is not published to the public network; only services inside the Compose network can reach it.

Set `MONGO_URI` in `deployment/.env` to the internal Compose hostname:

```env
MONGO_URI=mongodb://annotation_admin:replace-with-a-strong-password@mongo:27017/annotation_tool_healthcare_dialogue?authSource=admin
MONGO_INITDB_ROOT_USERNAME=annotation_admin
MONGO_INITDB_ROOT_PASSWORD=replace-with-a-strong-password
MONGO_APP_DATABASE=annotation_tool_healthcare_dialogue
```

Start the stack with the local MongoDB profile:

```bash
docker compose --env-file .env --profile local-mongo up -d
```

Check MongoDB:

```bash
docker compose --env-file .env --profile local-mongo ps mongo
docker compose --env-file .env --profile local-mongo exec mongo sh -c 'mongosh --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --eval "db.adminCommand(\"ping\")"'
```

### Optional: Mongo Express

Mongo Express is useful for inspection during setup. It is bound to `127.0.0.1:${MONGO_EXPRESS_PORT:-8081}` and should not be exposed directly to the public internet.

Start it with both profiles:

```bash
docker compose --env-file .env --profile local-mongo --profile mongo-admin up -d
```

Open it from the server with:

```text
http://127.0.0.1:8081
```

If you are connecting from your laptop, use an SSH tunnel:

```bash
ssh -L 8081:127.0.0.1:8081 user@YOUR_SERVER_IP
```

Then open `http://127.0.0.1:8081` locally.

## 7. Configure The OpenAI Key

Create the secrets directory and key file:

```bash
mkdir -p secrets
nano secrets/openai.key
chmod 600 secrets/openai.key
```

The file should contain only the API key, with no surrounding quotes.
The Compose file mounts it to `/run/secrets/openai.key`, matching `KEY_PATH`.

## 8. Build The Images

From the `deployment/` directory:

```bash
docker compose --env-file .env build
```

This builds:

- the React client with the `REACT_APP_*` values from `.env`
- the Flask server image with Python dependencies from `server/requirements.txt`

## 9. Start The Stack

Start all services with an external MongoDB:

```bash
docker compose --env-file .env up -d
```

Start all services with self-hosted MongoDB:

```bash
docker compose --env-file .env --profile local-mongo up -d
```

Check container status:

```bash
docker compose ps
docker compose logs -f server
```

The server initializes the `task_info` collection on startup. Existing task assignment state is preserved; only missing task records are inserted.

## 10. Configure Nginx Proxy Manager

Open the admin UI:

```text
http://YOUR_SERVER_IP:81
```

Create a proxy host:

- Domain Names: your public domain, for example `eng.example.org`
- Scheme: `http`
- Forward Hostname / IP: `web`
- Forward Port: `80`
- Websockets Support: enabled

Then open the SSL tab:

- Request a new Let's Encrypt certificate
- Enable Force SSL
- Enable HTTP/2

Save the proxy host.

## 11. Verify The Deployment

Run server health checks:

```bash
docker compose exec server python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/ping').read().decode())"
curl -i http://127.0.0.1:8080/api/ping
```

If using self-hosted MongoDB, also verify MongoDB:

```bash
docker compose --env-file .env --profile local-mongo exec mongo sh -c 'mongosh --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --eval "db.adminCommand(\"ping\")"'
```

Expected API response:

```json
{"msg":"pong","success":true}
```

Open the public domain in a browser and verify:

- Welcome page loads.
- Registration works.
- Login works.
- Audio check works.
- Assignment page returns a real task.
- Submitting a task marks it complete.
- Refreshing the assignment page returns the user's existing locked task rather than leaking another task.

## 12. Updating A Deployment

Pull new code:

```bash
cd /path/to/annotation_tool_healthcare_dialogue
git fetch origin
git checkout deployment
git pull --ff-only
cd deployment
```

Rebuild and restart:

```bash
docker compose --env-file .env build
docker compose --env-file .env up -d
docker compose ps
```

For self-hosted MongoDB deployments, include the profile:

```bash
docker compose --env-file .env --profile local-mongo build
docker compose --env-file .env --profile local-mongo up -d
docker compose --env-file .env --profile local-mongo ps
```

If only `.env` changed and no `REACT_APP_*` value changed, restart is enough:

```bash
docker compose --env-file .env up -d --force-recreate server web nginx-proxy-manager
```

If any `REACT_APP_*` value changed, rebuild the client.

## 13. Backup And Operations

Back up these items regularly:

- MongoDB database
- `deployment/.env`
- `deployment/secrets/openai.key`
- `deployment/data`
- `deployment/letsencrypt`
- Docker volume `healthcare-dialogue-annotation_server_final_submit`
- Docker volume `healthcare-dialogue-annotation_mongo_data` if using self-hosted MongoDB

Useful commands:

```bash
docker compose logs -f server
docker compose logs -f web
docker compose restart server
docker compose down
docker compose up -d
```

For self-hosted MongoDB backups, use `mongodump` from the MongoDB container or snapshot the `mongo_data` volume while the database is stopped.

## 14. Troubleshooting

If the client calls the wrong API URL:

1. Check `REACT_APP_SERVER_URL` in `deployment/.env`.
2. Rebuild the client image.
3. Restart the stack.

If the server cannot start:

1. Check `MONGO_URI`.
2. Check `TASK_PATH`.
3. Check that `secrets/openai.key` exists.
4. Run `docker compose logs server`.

If tasks are not assigned:

1. Confirm the task JSON is valid with `jq`.
2. Confirm `task_info` exists in MongoDB.
3. Confirm existing completed submissions are in `final_submission`.
4. Check whether the user has reached `TASK_THRESHOLD`.

If self-hosted MongoDB is not reachable:

1. Confirm you started the stack with `--profile local-mongo`.
2. Confirm `MONGO_URI` uses host `mongo` and port `27017`.
3. Confirm `MONGO_INITDB_ROOT_USERNAME` and `MONGO_INITDB_ROOT_PASSWORD` match the credentials inside `MONGO_URI`.
4. Run `docker compose --env-file .env --profile local-mongo logs mongo`.

If HTTPS does not work:

1. Confirm DNS points to the host.
2. Confirm ports `80` and `443` are open.
3. Check Nginx Proxy Manager certificate logs.
