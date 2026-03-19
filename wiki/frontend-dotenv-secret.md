# `frontend/.env.secret`

<h2>Table of contents</h2>

- [What is `frontend/.env.secret`](#what-is-frontendenvsecret)
- [`VITE_API_TARGET`](#vite_api_target)

## What is `frontend/.env.secret`

`frontend/.env.secret` is an [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for the `Vite` dev server.

`Vite` loads the values when running `pnpm run dev`.

Docs:

- [Vite env and mode](https://vite.dev/guide/env-and-mode)

Default values: [`frontend/.env.example`](../frontend/.env.example)

> [!NOTE]
> The file `frontend/.env.secret` was added to [`frontend/.gitignore`](./git.md#gitignore) because you may specify there
> [secrets](./environments.md#secrets) such as the [address of your VM](./vm.md#your-vm-ip-address).

## `VITE_API_TARGET`

The [LMS API base URL](./lms-api.md#lms-api-base-url) that the `Vite` dev server [proxies](./web-infrastructure.md#reverse-proxy) requests to.

Default: `http://127.0.0.1:42002`
