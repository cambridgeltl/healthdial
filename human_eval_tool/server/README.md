# Human Evaluation Tool Backend

This section details the setup and usage of the Flask backend for the Human Evaluation Tool.

## Prerequisites

Before setting up the backend, ensure that you have the following prerequisites installed:

- Python 3.9 or 3.10
- MongoDB
- Python packages listed in `deploy/requirement.txt`

## Installation

To install the required Python environment, execute the following command:

```
pip install -r server/deploy/requirement.txt
```

## Configuration

The application configuration relies on environment variables. Set up your configuration by creating a `.env` file in the project root directory. See `../.env.example`.


   - `SECRET_KEY`: Used for JWT token encryption.
   - `MONGO_URI`: The URI of your MongoDB database.
   - `TASK_CONFIG_PATH`: Task JSON file for participants. Follow the format in [./config/test_goals.json](./config/test_goals.json).
   - `TASK_LANGUAGE`: Human-readable task language label.
   - `TASK_DATASET`: Dataset or study label.
   - `ADMIN_EMAIL`: Email address that receives the admin role at registration.

## Usage

To start the application, execute the following command in the repository root:

```bash
python server/app.py
```

Upon running this command, the application will become accessible at http://localhost:4000.

## API Endpoints

For detailed information about the backend endpoints, refer to the `view/authentication.py` file.

The dialogue Socket.IO service is separate from the Flask backend. For local reproduction, use `../dummy_dialogue_server`.


---
