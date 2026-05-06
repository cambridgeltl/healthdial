# 部署文档

本文档说明如何使用 Docker Compose 部署 healthcare dialogue annotation tool。
生产部署文件位于 `deployment/docker-compose.yml`。

## 1. 部署架构

Compose 栈包含四个服务：

- `client`：构建 React 应用，并使用 Nginx 提供静态文件。
- `server`：使用 Gunicorn 运行 Flask API，容器内监听 `5000` 端口。
- `web`：内部 Nginx 反向代理。它把 `/api/` 和 `/audio/` 转发到后端，把其他路径转发到前端。
- `nginx-proxy-manager`：公网入口和 HTTPS 证书管理服务。它把公网域名转发到 `web:80`。

MongoDB 可以使用外部托管数据库，也可以由 Docker Compose 在本机部署。
自部署 MongoDB 是可选项，需要启用 `local-mongo` Compose profile。
如需临时管理界面，可以额外启用 `mongo-admin` profile 运行 Mongo Express。
OpenAI API key 从 `deployment/secrets/openai.key` 挂载到容器内。

## 2. 前置条件

请先在部署服务器上安装：

- Docker Engine
- Docker Compose v2
- Git
- 一个已经解析到服务器公网 IP 的域名
- 可访问的外部 MongoDB 数据库，或者为自部署 MongoDB 准备足够的本地磁盘空间
- 如果启用 ASR，需要准备 OpenAI API key

部署前检查端口和 Compose 版本：

```bash
sudo lsof -i :80 -i :81 -i :443
docker compose version
```

`80`、`81`、`443` 端口需要留给 Nginx Proxy Manager 使用。

## 3. 安全准备

如果此前有真实密钥被提交到仓库，正式部署前必须轮换这些密钥。
至少需要轮换：

- Flask/JWT 使用的 `SECRET_KEY`
- MongoDB 用户名和密码
- OpenAI API key

真实 `.env` 文件不能提交到 Git。本仓库只保留 `.env.example` 模板。

## 4. 准备代码

克隆仓库并切换到部署分支：

```bash
git clone <repository-url>
cd annotation_tool_healthcare_dialogue
git checkout deployment
```

检查要部署的任务文件：

```bash
jq -r 'to_entries | length' server/config/en_task_dic.json
```

根据目标语言选择对应任务文件：

- 英文：`server/config/production_en_task_dic.json`
- 阿拉伯语：`server/config/production_ar_task_dic.json`
- 西班牙语：`server/config/production_es_task_dic.json`
- 中文：`server/config/production_zh_task_dic.json`

## 5. 配置环境变量

创建部署环境文件：

```bash
cd deployment
cp .env.example .env
chmod 600 .env
```

编辑 `deployment/.env`：

```bash
nano .env
```

必填配置示例：

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

说明：

- `SECRET_KEY` 建议用 `openssl rand -base64 42` 生成。
- `MONGO_URI` 决定数据库模式。使用托管数据库时填写外部连接串；使用自部署 MongoDB 时填写 Compose 内部主机名 `mongo`。
- `TASK_PATH` 是 server 容器内部路径，不是宿主机路径。
- `REACT_APP_SERVER_URL` 必须是用户在浏览器中访问的公网地址。
- React 的 `REACT_APP_*` 变量会在镜像构建时写入前端包；修改后需要重新构建 client 镜像。

## 6. 选择 MongoDB 模式

启动服务前，请先在以下两种模式中选择一种。

### 方案 A：使用外部 MongoDB

如果你已经有 MongoDB Atlas、DigitalOcean Managed MongoDB 或其他托管 MongoDB 服务，请使用此方案。

1. 创建或选择本次部署使用的 MongoDB 数据库。
2. 创建具有该数据库读写权限的数据库用户。
3. 如果服务商要求 IP allowlist，请把部署服务器公网 IP 加入 allowlist。
4. 在 `deployment/.env` 中把 `MONGO_URI` 设置为服务商提供的连接串。

连接串形式示例：

```env
MONGO_URI=your-provider-connection-string
```

然后不启用 MongoDB profile，直接启动服务：

```bash
docker compose --env-file .env up -d
```

### 方案 B：自部署 MongoDB

如果希望 Docker Compose 在同一台服务器上运行 MongoDB，请使用此方案。
该 MongoDB 不会向公网发布端口，只有 Compose 网络内部的服务可以访问它。

在 `deployment/.env` 中把 `MONGO_URI` 设置为 Compose 内部主机名：

```env
MONGO_URI=mongodb://annotation_admin:replace-with-a-strong-password@mongo:27017/annotation_tool_healthcare_dialogue?authSource=admin
MONGO_INITDB_ROOT_USERNAME=annotation_admin
MONGO_INITDB_ROOT_PASSWORD=replace-with-a-strong-password
MONGO_APP_DATABASE=annotation_tool_healthcare_dialogue
```

启用本地 MongoDB profile 启动服务：

```bash
docker compose --env-file .env --profile local-mongo up -d
```

检查 MongoDB 状态：

```bash
docker compose --env-file .env --profile local-mongo ps mongo
docker compose --env-file .env --profile local-mongo exec mongo sh -c 'mongosh --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --eval "db.adminCommand(\"ping\")"'
```

### 可选：Mongo Express 管理界面

Mongo Express 适合部署初期临时查看数据。它绑定到 `127.0.0.1:${MONGO_EXPRESS_PORT:-8081}`，不要直接暴露到公网。

同时启用两个 profile：

```bash
docker compose --env-file .env --profile local-mongo --profile mongo-admin up -d
```

在服务器本机访问：

```text
http://127.0.0.1:8081
```

如果从自己的电脑访问，请使用 SSH 隧道：

```bash
ssh -L 8081:127.0.0.1:8081 user@YOUR_SERVER_IP
```

然后在本地浏览器打开 `http://127.0.0.1:8081`。

## 7. 配置 OpenAI Key

创建 secrets 目录和 key 文件：

```bash
mkdir -p secrets
nano secrets/openai.key
chmod 600 secrets/openai.key
```

文件中只放 API key 本身，不要加引号。
Compose 会把该文件挂载到 `/run/secrets/openai.key`，与 `KEY_PATH` 保持一致。

## 8. 构建镜像

在 `deployment/` 目录执行：

```bash
docker compose --env-file .env build
```

该命令会构建：

- 前端 React 镜像，并写入 `.env` 中的 `REACT_APP_*` 变量
- 后端 Flask 镜像，并安装 `server/requirements.txt` 中的 Python 依赖

## 9. 启动服务

使用外部 MongoDB 时启动整个服务栈：

```bash
docker compose --env-file .env up -d
```

使用自部署 MongoDB 时启动整个服务栈：

```bash
docker compose --env-file .env --profile local-mongo up -d
```

查看容器状态：

```bash
docker compose ps
docker compose logs -f server
```

后端启动时会初始化 MongoDB 的 `task_info` 集合。已有任务分配状态会保留，只会插入缺失的任务记录。

## 10. 配置 Nginx Proxy Manager

打开管理界面：

```text
http://服务器公网 IP:81
```

创建 Proxy Host：

- Domain Names：公网域名，例如 `eng.example.org`
- Scheme：`http`
- Forward Hostname / IP：`web`
- Forward Port：`80`
- Websockets Support：启用

然后进入 SSL 选项卡：

- 申请新的 Let's Encrypt 证书
- 启用 Force SSL
- 启用 HTTP/2

保存配置。

## 11. 验证部署

检查后端健康状态：

```bash
docker compose exec server python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:5000/api/ping').read().decode())"
curl -i http://127.0.0.1:8080/api/ping
```

如果使用自部署 MongoDB，也检查 MongoDB：

```bash
docker compose --env-file .env --profile local-mongo exec mongo sh -c 'mongosh --username "$MONGO_INITDB_ROOT_USERNAME" --password "$MONGO_INITDB_ROOT_PASSWORD" --authenticationDatabase admin --eval "db.adminCommand(\"ping\")"'
```

预期 API 返回：

```json
{"msg":"pong","success":true}
```

在浏览器打开公网域名并验证：

- Welcome 页面能正常加载。
- 注册流程可用。
- 登录流程可用。
- 音频检查可用。
- Assignment 页面能返回真实任务。
- 提交任务后任务会被标记为完成。
- 刷新 Assignment 页面时会返回当前用户已有的锁定任务，而不是额外泄露新任务。

## 12. 更新部署

拉取最新代码：

```bash
cd /path/to/annotation_tool_healthcare_dialogue
git fetch origin
git checkout deployment
git pull --ff-only
cd deployment
```

重新构建并启动：

```bash
docker compose --env-file .env build
docker compose --env-file .env up -d
docker compose ps
```

如果使用自部署 MongoDB，更新时带上 profile：

```bash
docker compose --env-file .env --profile local-mongo build
docker compose --env-file .env --profile local-mongo up -d
docker compose --env-file .env --profile local-mongo ps
```

如果只修改了 `.env`，且没有修改任何 `REACT_APP_*` 变量，通常只需要重建后端相关服务：

```bash
docker compose --env-file .env up -d --force-recreate server web nginx-proxy-manager
```

如果修改了任意 `REACT_APP_*` 变量，必须重新构建 client 镜像。

## 13. 备份与日常运维

请定期备份：

- MongoDB 数据库
- `deployment/.env`
- `deployment/secrets/openai.key`
- `deployment/data`
- `deployment/letsencrypt`
- Docker volume `healthcare-dialogue-annotation_server_final_submit`
- 如果使用自部署 MongoDB，还要备份 Docker volume `healthcare-dialogue-annotation_mongo_data`

常用命令：

```bash
docker compose logs -f server
docker compose logs -f web
docker compose restart server
docker compose down
docker compose up -d
```

如果使用自部署 MongoDB，建议使用 MongoDB 容器中的 `mongodump` 备份，或者在停止数据库后对 `mongo_data` volume 做快照。

## 14. 排障

如果前端请求了错误的 API 地址：

1. 检查 `deployment/.env` 中的 `REACT_APP_SERVER_URL`。
2. 重新构建 client 镜像。
3. 重启服务栈。

如果后端无法启动：

1. 检查 `MONGO_URI`。
2. 检查 `TASK_PATH`。
3. 检查 `secrets/openai.key` 是否存在。
4. 执行 `docker compose logs server` 查看日志。

如果任务无法分配：

1. 使用 `jq` 确认任务 JSON 格式正确。
2. 确认 MongoDB 中存在 `task_info` 集合。
3. 确认历史完成记录在 `final_submission` 集合中。
4. 检查该用户是否已达到 `TASK_THRESHOLD`。

如果自部署 MongoDB 无法连接：

1. 确认启动命令包含 `--profile local-mongo`。
2. 确认 `MONGO_URI` 使用主机名 `mongo` 和端口 `27017`。
3. 确认 `MONGO_INITDB_ROOT_USERNAME`、`MONGO_INITDB_ROOT_PASSWORD` 与 `MONGO_URI` 中的账号密码一致。
4. 执行 `docker compose --env-file .env --profile local-mongo logs mongo` 查看日志。

如果 HTTPS 不工作：

1. 确认 DNS 已解析到服务器。
2. 确认 `80` 和 `443` 端口开放。
3. 查看 Nginx Proxy Manager 的证书日志。
