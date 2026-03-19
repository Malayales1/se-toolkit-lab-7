# LMS API deployment

<h2>Table of contents</h2>

- [About the LMS API deployment](#about-the-lms-api-deployment)
- [Deploy the LMS API on the VM](#deploy-the-lms-api-on-the-vm)
  - [Clone the repository (REMOTE)](#clone-the-repository-remote)
  - [Enter the repository directory (REMOTE)](#enter-the-repository-directory-remote)
  - [Configure the environment (REMOTE)](#configure-the-environment-remote)
  - [Start the services (REMOTE)](#start-the-services-remote)
  - [Populate the database (LOCAL)](#populate-the-database-local)
  - [View the dashboard (LOCAL)](#view-the-dashboard-local)

## About the LMS API deployment

This page describes how to deploy the [LMS API](./lms-api.md#about-the-lms-api) and additional [services](./docker-compose-yml.md#services) on [your VM](./vm.md#your-vm) using [`Docker Compose`](./docker-compose.md#what-is-docker-compose).

## Deploy the LMS API on the VM

1. [Connect to the VM as the user `admin` (LOCAL)](./vm-access.md#connect-to-the-vm-as-the-user-user-local).
2. [Clone the repository (REMOTE)](#clone-the-repository-remote).
3. [Switch to the necessary `<branch>` (REMOTE)](./git-vscode.md#switch-to-the-branch-using-the-vs-code-terminal).
4. [Hard reset the `<branch>`](./git-vscode.md#hard-reset-the-branch).
5. [Configure the environment (REMOTE)](#configure-the-environment-remote).
6. [Configure `Docker` DNS (REMOTE)](./docker.md#configure-docker-dns).
7. [Start the services (REMOTE)](#start-the-services-remote).
8. [Populate the database (LOCAL)](#populate-the-database-local).
9. [View the dashboard (LOCAL)](#view-the-dashboard-local).

### Clone the repository (REMOTE)

1. [Clone the repository](./git-vscode.md#clone-the-repository-using-the-vs-code-terminal)

   with the URL `https://github.com/<your-github-username>/se-toolkit-lab-6`

   to `~/se-toolkit-lab-6`.

   Replace the placeholder [`<your-github-username>`](./github.md#your-github-username).

### Enter the repository directory (REMOTE)

1. To enter the [directory](./file-system.md#directory) of your [repository](./git.md#repository),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cd ~/se-toolkit-lab-6
   ```

### Configure the environment (REMOTE)

1. To create [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   cp .env.docker.example .env.docker.secret
   ```

2. To open the file in `nano`,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   nano .env.docker.secret
   ```

3. Set the [`Autochecker` API credentials](./autochecker-api.md#autochecker-api-credentials):

   ```text
   AUTOCHECKER_API_LOGIN=<autochecker-api-login>
   AUTOCHECKER_API_PASSWORD=<autochecker-api-password>
   ```

   Replace the placeholders:

   - [`<autochecker-api-login>`](./autochecker-api.md#autochecker-api-login-placeholder)
   - [`<autochecker-api-password>`](./autochecker-api.md#autochecker-api-password-placeholder)

4. Set the [LMS API key](./lms-api.md#lms-api-key).

   ```text
   LMS_API_KEY=<lms-api-key>
   ```

   Replace the placeholder [`<lms-api-key>`](./lms-api.md#lms-api-key-placeholder).

   See [API key format](./web-api.md#api-key-format).

5. To write the changes:

   1. Press `Ctrl+O`.
   2. Press `Enter`.

6. To close the editor, press `Ctrl+X`.

### Start the services (REMOTE)

1. To start all services in the [background](./operating-system.md#background-process),

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose --env-file .env.docker.secret up --build -d
   ```

   > <h3>Troubleshooting</h3>
   >
   > **`permission denied while trying to connect to the Docker daemon socket ...`**
   >
   > 1. [Set up `Docker`](./docker.md#set-up-docker-as-the-user-user-remote).
   >
   > [**Port conflict (`port is already allocated`)**](./docker.md#port-conflict-port-is-already-allocated)
   >
   > [**Containers exit immediately**](./docker-compose.md#containers-exit-immediately)
   >
   > [**Image pull fails**](./docker.md#image-pull-fails)
   >
   > **`RUN npm install -g pnpm` hangs**
   >
   > 1. Press `Ctrl+C`.
   > 2. See [DNS resolution errors](./docker.md#dns-resolution-errors).
   >
   > **`getaddrinfo EAI_AGAIN`**
   >
   > 1. See [DNS resolution errors](./docker.md#dns-resolution-errors).
   >
   > **`=> ERROR [app builder 3/6] RUN --mount=type=cache,target=/root/.cache/uv`**
   >
   > 1. See [DNS resolution errors](./docker.md#dns-resolution-errors).

2. To check that the [containers](./docker.md#container) are running,

   [run in the `VS Code Terminal`](./vs-code.md#run-a-command-in-the-vs-code-terminal):

   ```terminal
   docker compose --env-file .env.docker.secret ps --format "table {{.Service}}\t{{.Status}}"
   ```

   You should see all four services running:

   ```text
   SERVICE    STATUS
   app        Up 50 seconds
   caddy      Up 49 seconds
   pgadmin    Up 50 seconds
   postgres   Up 55 seconds (healthy)
   ```

### Populate the database (LOCAL)

The [database](./database.md#what-is-a-database) starts empty.
You need to run the ETL pipeline to populate it with data from the [`Autochecker` API](./autochecker-api.md#about-the-autochecker-api).

1. Open in a browser: `<lms-api-base-url>/docs`.

   Replace the placeholders:

   - [`<lms-api-base-url>`](./lms-api.md#lms-api-base-url-placeholder)

   You should see the [`Swagger UI`](./swagger.md#what-is-swagger-ui) page.

2. [Authorize in `Swagger UI`](./swagger.md#authorize-in-swagger-ui) with the [`LMS_API_KEY`](./dotenv-docker-secret.md#lms_api_key) that you set in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret).

3. [Try the endpoint](./swagger.md#try-an-endpoint-in-swagger-ui) `POST /pipeline/sync`.

   You should get a response showing the number of records loaded:

   ```json
   {
     "new_records": 120,
     "total_records": 9502
   }
   ```

   > 🟦 **Note**
   >
   > The exact numbers depend on how much data the [`Autochecker` API](./autochecker-api.md#about-the-autochecker-api) has.
   > As long as both numbers are greater than 0, the sync worked.

4. [Try the endpoint](./swagger.md#try-an-endpoint-in-swagger-ui) `GET /items/`.

   You should get a non-empty array of items.

### View the dashboard (LOCAL)

1. Open in a browser: `<lms-api-base-url>/`.

   Replace the placeholder [`<lms-api-base-url>`](./lms-api.md#lms-api-base-url-placeholder).

   You should see the [frontend](./lms-frontend.md#about-the-lms-frontend).

2. Enter the [LMS API key](./lms-api.md#lms-api-key).

3. Switch to the **Dashboard** tab.

   You should see charts with analytics data:

   - submissions timeline
   - score distribution
   - group performance
   - task pass rates

   > <h3>Troubleshooting</h3>
   >
   > If the dashboard shows no data or errors, make sure that:
   >
   > - The ETL sync completed successfully ([Populate the database](#populate-the-database-local)).
   > - You entered the correct LMS API key in the frontend.
   > - At least one lab works:
   >    1. Select a different lab in the dropdown (e.g., `lab-04`).
