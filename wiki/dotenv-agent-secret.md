# `.env.agent.secret`

<h2>Table of contents</h2>

- [About `.env.agent.secret`](#about-envagentsecret)
- [`LLM_API_KEY`](#llm_api_key)
- [`LLM_API_BASE_URL`](#llm_api_base_url)
- [`LLM_API_MODEL`](#llm_api_model)

## About `.env.agent.secret`

`.env.agent.secret` is a [`.env` file](./environments.md#env-file) that stores [environment variables](./environments.md#environment-variable) for `agent.py`.

The values configure the [LLM](./llm.md) that powers your agent.

Default values: [`.env.agent.example`](../.env.agent.example)

> [!NOTE]
> `.env.agent.secret` was added to [`.gitignore`](./git.md#gitignore) because you may specify there
> [secrets](./environments.md#secrets) such as the [`LLM_API_KEY`](#llm_api_key).

## `LLM_API_KEY`

The [API key](./web-api.md#api-key) for your [LLM provider API](./llm.md#llm-provider-api).

- For the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api):
  
  the value of [`QWEN_CODE_API_KEY`](./qwen-code-api-dotenv-secret.md#qwen_code_api_key) from [`qwen-code-api/.env.secret`](./qwen-code-api-dotenv-secret.md#about-qwen-code-apienvsecret).

- For the [`OpenRouter` API](./llm.md#openrouter-api):
  
  your `OpenRouter` API key.

Default: `your-llm-api-key-here`

## `LLM_API_BASE_URL`

The base URL of the [OpenAI-compatible API](./llm.md#openai-compatible-api) endpoint.

- For the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api) on your VM:
  
  `<lms-api-url>/utils/qwen-code-api/v1`.

  See [`<lms-api-url>`](./lms-api.md#lms-api-base-url-placeholder).

- For the [`OpenRouter` API](./llm.md#openrouter-api):
  
  `https://openrouter.ai/api/v1`.

Default: `<lms-api-url>/utils/qwen-code-api/v1`

## `LLM_API_MODEL`

The name of the [LLM model](./llm.md#model) to use via the [LLM provider API](./llm.md#llm-provider-api).

- For the [`Qwen Code` API](./qwen-code-api.md#what-is-qwen-code-api) on your VM:
  
  `coder-model`.
  
  See [View available models](./qwen-code.md#view-available-models).

- For the [`OpenRouter` API](./llm.md#openrouter-api):
  
  `meta-llama/llama-3.3-70b-instruct:free`.

Default: `coder-model`
