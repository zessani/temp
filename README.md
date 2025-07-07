# website-backend-resume-parser-v2

## Initial Code Setup (PLEASE READ!)

### `.env` Files

#### Context

- Notice that the Python FastAPI system and the database system both require username/password authentication (which means usernames and passwords need to be defined).
- The usernames and passwords are defined with `.env` files. You need to create these `.env` files (`.env.backend` and `.env.db` in the root of the repository directory) based on the `.template.env` files (`.template.env.backend` and `.template.env.db` respectively).
- Once you create the `.env` files, ensure that you NEVER commit them into the repository. Consider them as sensitive and as containing secret information that should not be publicly available.
- The templates fill out most of the fields for you (including the usernames). All you need to define are decent passwords.
- Technically when you run these Docker containers locally on your machine, unless you have port-forwarding set up, they are NOT exposed to the internet, so having strong passwords is not extremely important, but a nice precaution.

#### Remember to Check...

- Ensure that `DB_PASSWORD` in `.env.backend` and `MONGO_INITDB_ROOT_PASSWORD` in `.env.db` have the same value.
- Ensure that `DB_USERNAME` in `.env.backend` and `MONGO_INITDB_ROOT_USERNAME` in `.env.db` have the same value.

## How to Run

### Prerequisites

Ensure that...

- You have Docker already installed on your system. See the [Docker installation page](https://docs.docker.com/engine/install/).
- The Docker engine/daemon is running in the background (otherwise the Docker containers in this project would not be able to start).
- You have followed the initial setup instructions above.

### Steps

**NOTE**: these are assuming that you are running macOS/Linux.

1. Open up your terminal app.
2. `cd` inside of the repository directory
3. Run: `docker compose up --build`
