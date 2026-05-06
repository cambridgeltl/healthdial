# Health Dialogue Human Evaluation Platform

This repository provides a reusable human-evaluation platform for comparing a
dialogue system with a reference health-information website. It was designed for
health dialogue evaluation, but the workflow can be adapted to other domains
where researchers want participants to compare a chatbot with an external
information source.

The platform includes:

- a React participant interface for consent, registration, task assignment,
  reference-site comparison, chatbot interaction, and questionnaire submission;
- a Flask backend for authentication, task assignment, and result storage;
- MongoDB storage for users and questionnaire responses;
- configurable scenario/task JSON files;
- a deterministic dummy Socket.IO dialogue server for local testing and full
  workflow reproduction.

The dummy dialogue server is an API-compatible stand-in for a real chatbot. It
is useful for testing the interface, but it is not a medical-advice system and
should be replaced by your real dialogue service for an actual participant
study.

## Repository Layout

```text
client/                 React evaluation interface
server/                 Flask API, MongoDB data models, task configuration
dummy_dialogue_server/  Local Socket.IO chatbot replacement for testing
docker-compose.yml      Optional one-command local stack
.env.example            Backend and Docker environment template
client/.env.example     Frontend environment template
```

Important source files:

- `client/src/Assignment.tsx`: participant instructions, chatbot panel, and
  questionnaire form.
- `client/src/ConsentForm.tsx`: consent text and study information.
- `client/src/Chatbox.tsx`: Socket.IO frontend client for the dialogue service.
- `client/src/configs.js`: frontend defaults and public contact values.
- `server/app.py`: Flask application entry point.
- `server/view/authentication.py`: login, registration, task, and result APIs.
- `server/dao/FeedBack.py`: questionnaire result schema.
- `server/config/test_goals.json`: default participant task scenarios.
- `dummy_dialogue_server/app.py`: reference implementation of the dialogue
  Socket.IO API.

## Quick Start with Docker

Prerequisites: Docker and Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Open the frontend at <http://localhost:3000>.

Local services:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:4000>
- Dummy dialogue server: <http://localhost:5050>
- MongoDB: `mongodb://localhost:27017/health_dialogue_human_eval`

Register a user with `admin@example.com` to receive the default admin role, or
change `ADMIN_EMAIL` in `.env` before starting the stack.

## Local Deployment without Docker

Prerequisites:

- Python 3.9 or 3.10. Python 3.13 is not recommended for the backend dependency
  set because older `gevent` wheels may not build.
- Node.js 18 or newer.
- MongoDB Community Server.

### 1. Create the Python Environment

Run from the repository root:

```bash
cd /path/to/health_dialogue_human_eval
cp .env.example .env

conda create -n health-eval python=3.10 -y
conda activate health-eval
pip install -r server/deploy/requirement.txt
pip install -r dummy_dialogue_server/requirements.txt
```

If you prefer `venv`, use a Python 3.10 interpreter:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r server/deploy/requirement.txt
pip install -r dummy_dialogue_server/requirements.txt
```

### 2. Start MongoDB

On macOS with Homebrew:

```bash
brew tap mongodb/brew
brew install mongodb-community@8.0
brew services start mongodb/brew/mongodb-community@8.0
```

Check that MongoDB is running:

```bash
brew services list | grep mongodb
```

If you want to run MongoDB manually:

```bash
mkdir -p /tmp/health_dialogue_mongo
mongod --dbpath /tmp/health_dialogue_mongo
```

### 3. Start the Backend

Open a new terminal:

```bash
cd /path/to/health_dialogue_human_eval
conda activate health-eval
python server/app.py
```

Smoke test:

```bash
curl http://localhost:4000/healthz
```

Expected response:

```json
{"status":"ok"}
```

### 4. Start the Dummy Dialogue Server

Open a new terminal:

```bash
cd /path/to/health_dialogue_human_eval
conda activate health-eval
python dummy_dialogue_server/app.py
```

Smoke test:

```bash
curl http://localhost:5050/healthz
```

Expected response:

```json
{"service":"dummy-dialogue-server","status":"ok"}
```

### 5. Start the Frontend

Open a new terminal:

```bash
cd /path/to/health_dialogue_human_eval/client
cp .env.example .env
npm ci
npm start
```

Open <http://localhost:3000>.

## Manual End-to-End Test

Use this checklist after MongoDB, the backend, the dummy dialogue server, and
the frontend are all running:

1. Open <http://localhost:3000>.
2. Register a participant account. Registering with the email in `ADMIN_EMAIL`
   creates an admin user.
3. Confirm that the assignment page displays a health scenario from
   `server/config/test_goals.json`.
4. Open the reference website link from the interface.
5. Send a chatbot message, for example:

```text
What should I do about a fever?
```

6. Confirm that the dummy dialogue server returns a response and expandable
   evidence snippets.
7. Complete the questionnaire and submit it.
8. Confirm that the result page appears.

This verifies the frontend, backend, MongoDB storage path, and Socket.IO
dialogue path together.

## Adapting the Tool for a New Study

Researchers usually need to change four parts of the platform:

1. Replace the participant scenarios in `server/config/test_goals.json`.
2. Update the consent/contact text and public contact values.
3. Connect a real dialogue system by implementing the Socket.IO API described
   below, then set `REACT_APP_DIALOGUE_SERVER_URL`.
4. Modify the questionnaire in `client/src/Assignment.tsx` and the backend
   result schema in `server/dao/FeedBack.py` if your study uses different
   measures.

Common files to edit:

- `server/config/test_goals.json`: participant scenarios.
- `client/.env`: public contact information and local service URLs.
- `client/src/ConsentForm.tsx`: consent language and study-specific ethics
  text.
- `client/src/Assignment.tsx`: participant instructions, reference website
  link, chatbot section, and questionnaire items.
- `server/dao/FeedBack.py`: stored result schema.
- `server/view/authentication.py`: `/api/save_result` parsing logic.

Run the verification commands below after each study-specific change.

## Configuration

Copy `.env.example` to `.env` for Docker or backend local runs. Copy
`client/.env.example` to `client/.env` for local React runs with `npm start`.

Key backend variables:

- `SECRET_KEY`: Flask and JWT signing secret for your local or deployed backend.
- `MONGO_URI`: MongoDB connection string for the backend.
- `TASK_CONFIG_PATH`: scenario JSON file used by the backend.
- `TASK_LANGUAGE`: human-readable language label returned with assigned tasks.
- `TASK_DATASET`: dataset or study label returned with assigned tasks.
- `ADMIN_EMAIL`: email address that receives the admin role at registration.
- `PORT`: backend port, default `4000`.

Key frontend variables:

- `REACT_APP_SERVER_URL`: frontend URL for the Flask API.
- `REACT_APP_DIALOGUE_SERVER_URL`: frontend URL for the Socket.IO dialogue API.
- `REACT_APP_CONTACT_NAME`: public research contact name.
- `REACT_APP_CONTACT_ADDRESS`: public research contact affiliation/address.
- `REACT_APP_CONTACT_EMAIL`: public research contact email.

For a local study pilot, the default localhost values in `.env.example` and
`client/.env.example` are usually enough.

## Task Scenario Format

The task file is a JSON object. Each key is a stable task identifier and each
value is a list of instruction strings shown in the assignment timeline.

Example:

```json
{
  "task_001": [
    "You are comparing two tools for finding vaccine information.",
    "Search the reference website first, then ask the dialogue system.",
    "Afterwards, complete the comparison questionnaire."
  ]
}
```

The bundled default file is `server/config/test_goals.json`.

To use another task file:

```bash
TASK_CONFIG_PATH=/absolute/path/to/tasks.json python server/app.py
```

Recommendations:

- Keep task IDs stable, because they are useful during analysis.
- Keep each timeline item short enough for participants to scan.
- Avoid including personally identifying information in task scenarios.
- If your study has multiple conditions, encode condition labels in the task ID
  or add a separate condition field to the result schema.

## Study Text and Consent

The public contact block is configured through:

- `REACT_APP_CONTACT_NAME`
- `REACT_APP_CONTACT_ADDRESS`
- `REACT_APP_CONTACT_EMAIL`

The consent page also contains study-specific text in
`client/src/ConsentForm.tsx`. Researchers should review and update that file so
the displayed information matches their approved ethics/IRB protocol.

Common study-text edits:

- project title;
- research team;
- contact email;
- consent statements;
- data retention and repository language;
- participant time estimate;
- reference website name if you are not using WHO.

## Replacing the Reference Website

The current interface asks participants to compare the dialogue system with the
WHO website. If your study uses another reference source:

1. Update participant instructions in `client/src/Assignment.tsx`.
2. Replace the external link in the "Step 2" panel.
3. Rename questionnaire items that mention WHO.
4. Update the data schema notes below if labels change.

## Dialogue Server API

The React frontend connects to the dialogue service with Socket.IO. The URL is
configured with `REACT_APP_DIALOGUE_SERVER_URL`.

The bundled `dummy_dialogue_server/` implements this contract and can be used as
a reference adapter for a real dialogue system.

### Client Event: `user_message`

Sent when a participant submits text.

Payload:

```json
"What should I do about a fever?"
```

### Client Event: `user_voice`

Sent when a participant records audio.

Payload:

```json
{
  "audio": "data:audio/webm;base64,..."
}
```

The dummy server acknowledges the event but does not perform speech recognition.

### Server Event: `system_message`

The frontend accepts either a plain string or an object. The recommended object
format is:

```json
{
  "type": "text",
  "system_text": "Example assistant response.",
  "snippet": [
    {
      "url": "https://www.who.int/health-topics",
      "data": {
        "title": "Evidence title",
        "content": "Evidence preview shown in the UI."
      }
    }
  ]
}
```

Voice responses are also supported:

```json
{
  "type": "voice",
  "audio_url": "https://example.com/response.webm",
  "audio_dur": "5",
  "snippet": []
}
```

Before running a participant study with a real dialogue system, check that:

- `user_message` accepts plain text.
- `user_voice` either supports browser audio data URLs or returns a clear
  fallback response.
- `system_message` always emits one of the supported response shapes.
- CORS allows the frontend origin.
- The service remains responsive after multiple messages in one browser session.
- The response text shown to participants matches your study protocol and
  safety requirements.

## Questionnaire and Data Schema

The questionnaire is defined in `client/src/Assignment.tsx`. The backend expects
matching fields in `/api/save_result`.

When adding, removing, or renaming questionnaire items:

1. Update the frontend form field type in `client/src/Assignment.tsx`.
2. Update the submitted `payload` in `client/src/Assignment.tsx`.
3. Update `FeedBack` in `server/dao/FeedBack.py`.
4. Update `feedback_data` in `server/view/authentication.py`.
5. Update the schema table below.
6. Run the frontend test/build and backend unit checks.

### MongoDB Collections

#### `user`

Created during registration.

Fields:

- `_id`: MongoDB object ID.
- `username`: participant-provided username.
- `email`: participant-provided email address.
- `password`: bcrypt password hash.
- `country`: participant-provided country of residence.
- `date_added`: registration timestamp.
- `role`: role object with `name` and `permissions`.

The email configured as `ADMIN_EMAIL` receives the admin role when registered.

#### `result`

Created when a participant submits the evaluation questionnaire.

| Field | Type | Meaning |
| --- | --- | --- |
| `usefulness` | integer | Rating for whether the dialogue system helped the participant understand health information better than the reference website. |
| `easeOfUse` | integer | Rating for whether the dialogue system was easier to use than the reference website. |
| `outputQuality` | integer | Rating for whether the dialogue system gave more useful answers. |
| `intentionToUse` | integer | Rating for future preference to use the dialogue system. |
| `overall` | integer | Overall satisfaction with the dialogue system. |
| `goal` | integer | Whether the participant found the answers: `1` yes, `2` partially, `3` no. |
| `trust` | integer | Trust rating for dialogue-system information compared with the reference website. |
| `preferredTool` | string | Participant preference: `dialogue`, `who`, or `depends`. |
| `preferredReason` | string | Optional explanation for the preferred tool. |
| `whoOverall` | integer | Overall satisfaction with the reference website. |
| `taskCompletion` | integer | How much information the participant found: `1` all, `2` most, `3` some, `4` little or none. |
| `feedback` | string | Optional free-text feedback. |
| `create_time` | datetime | Server-side submission timestamp. |
| `feedback_user` | string | Email address of the submitting user. |

Important limitations:

- The current backend does not store full dialogue transcripts.
- The current backend does not store the sampled `task_id` with the submitted
  questionnaire. If task-level analysis is required, add `task_id` to the
  frontend payload and `FeedBack` schema before running the study.
- The current backend stores participant email addresses with questionnaire
  results. For stricter anonymization, replace `feedback_user` with a
  participant code or hashed identifier before data collection.

## Exporting Results

Authenticated API export:

```bash
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://localhost:4000/api/get_all_results
```

MongoDB shell check:

```bash
mongosh
use health_dialogue_human_eval
db.result.find().limit(3)
```

MongoDB JSON export:

```bash
mongoexport \
  --db health_dialogue_human_eval \
  --collection result \
  --type=json \
  --out result_export.json
```

Review your ethics and data-management plan before exporting or sharing
participant data.

## Verification

Backend and dummy dialogue unit checks:

```bash
python -m unittest server/test_task_environment.py
python -m unittest dummy_dialogue_server/test_dummy_server.py
python -m compileall -q server dummy_dialogue_server
```

Frontend checks:

```bash
cd client
npm test -- --watchAll=false
npm run build
```

Notes:

- React Router may print v7 future-flag warnings during tests. These warnings do
  not indicate a failed test.
- `npm install` may report audit warnings from the legacy Create React App
  dependency tree. Avoid `npm audit fix --force` unless you are intentionally
  doing a dependency-upgrade pass.
