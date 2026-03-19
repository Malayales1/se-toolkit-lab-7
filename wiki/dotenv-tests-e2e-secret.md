# `.env.tests.e2e.secret`

- [What is `.env.tests.e2e.secret`](#what-is-envtestse2esecret)
- [`API_BASE_URL`](#api_base_url)
- [`LMS_API_KEY`](#lms_api_key)

## What is `.env.tests.e2e.secret`

`.env.tests.e2e.secret` is an [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for running [end-to-end tests](./quality-assurance.md#end-to-end-test).

Default values: [`.env.tests.e2e.example`](../.env.tests.e2e.example)

> It was added to [`.gitignore`](./git.md#gitignore) because it may contain [secrets](./environments.md#secrets) such as the [LMS API key](./lms-api.md#lms-api-key) or the [VM IP address](./vm.md#your-vm-ip-address).

## `API_BASE_URL`

The base [URL](./computer-networks.md#url) of the deployed API.

Example: `http://192.0.2.1:42002`

## `LMS_API_KEY`

The [LMS API key](./lms-api.md#lms-api-key).

It value must match the value of [`LMS_API_KEY`](./dotenv-docker-secret.md#lms_api_key) in [`.env.docker.secret`](./dotenv-docker-secret.md#what-is-envdockersecret) on the VM.
