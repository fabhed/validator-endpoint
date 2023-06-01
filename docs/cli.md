# `btvep`

Bitensor Validator Endpoint CLI

**Usage**:

```console
$ btvep [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --version`: Show the application's version and exit.
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `config`: Update and read config values.
* `key`: Manage API keys.
* `logs`: Inspect request logs.
* `ratelimit`: Global & API Key-specific Rate limit...
* `start`: Start the API server.

## `btvep config`

Update and read config values. Config values are stored in a json file at /Users/fabian/git/validator-endpoint/config.json

General Config values available:

- hotkey_mnemonic - The hotkey mnemonic for the validator. This is required as the validator will be signing the prompts to miners.


Rate Limiting Config values available:

- rate_limiting_enabled - Whether to enable rate limiting. If enabled, the global_rate_limits will be used.
- redis_url - The redis url to use for rate limiting.
- global_rate_limits - A list of rate limits. Prefer to use btvep ratelimit to manage rate limits.


Example usage:

1. Set hotkey_mnemonic:
    `btvep config set hotkey_mnemonic "my_validators_secret_mnemonic_phrase_here"`

2. Get hotkey_mnemonic:
    `btvep config get hotkey_mnemonic`

**Usage**:

```console
$ btvep config [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `get`: Prints a config value.
* `set`: Set a config value.

### `btvep config get`

Prints a config value.

**Usage**:

```console
$ btvep config get [OPTIONS] [KEY]
```

**Arguments**:

* `[KEY]`: The config key to get.

**Options**:

* `--help`: Show this message and exit.

### `btvep config set`

Set a config value.

**Usage**:

```console
$ btvep config set [OPTIONS] KEY VALUE
```

**Arguments**:

* `KEY`: The config key to set.  [required]
* `VALUE`: The config value to set.  [required]

**Options**:

* `--help`: Show this message and exit.

## `btvep key`

Manage API keys.

**Usage**:

```console
$ btvep key [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new API key.
* `delete`: Deletes an API key.
* `edit`: Edit an API key.
* `list`: List all API keys.

### `btvep key create`

Create a new API key.

**Usage**:

```console
$ btvep key create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: The name of the API key.
* `-v, --valid-until INTEGER`: The unix timestamp when the API key expires. Defaults to -1 which means that the key never expires.  [default: -1]
* `-c, --credits INTEGER`: The number of credits the API key has. -1 means unlimited.  [default: -1]
* `-e, --enable / -d, --disable`: Whether the API key is enabled or not. Disabled keys cannot make requests.  [default: enable]
* `--help`: Show this message and exit.

### `btvep key delete`

Deletes an API key.

**Usage**:

```console
$ btvep key delete [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: The API key to delete. Can be specified by either the key or its numerical id.  [required]

**Options**:

* `--help`: Show this message and exit.

### `btvep key edit`

Edit an API key.

**Usage**:

```console
$ btvep key edit [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: The API key to edit. Can be specified by either the key or its numerical id.  [required]

**Options**:

* `-k, --api_key_hint TEXT`
* `-n, --name TEXT`
* `-r, --request_count INTEGER`
* `-u, --valid_until TEXT`: When the API key expires.
Set to false to disable expiration.
You can specify the expiry in natural language (e.g. 'in 1 month', 'in 10 days', 'December 2025', 'next year', 'tomorrow', 'next week', etc.)
or as a date (e.g. '2025-01-01').
or as an epoch timestamp (e.g. '1735603200')
Parsing of relative dates will be relative to the current date but ignore the current time of day.
* `-c, --credits INTEGER`
* `-e, --enable / -d, --disable`: Enable or disable the API key.
* `--help`: Show this message and exit.

### `btvep key list`

List all API keys.

**Usage**:

```console
$ btvep key list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `btvep logs`

Inspect request logs.

**Usage**:

```console
$ btvep logs [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-k, --key TEXT`: Filter logs by API key.
* `-r, --responder-hotkey TEXT`: Filter logs by responder hotkey.
* `-l, --lines INTEGER`: Maximum number of lines to print.  [default: 100]
* `-s, --start [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]`: The start of the time range to inspect.
* `-e, --end [%Y-%m-%d|%Y-%m-%dT%H:%M:%S|%Y-%m-%d %H:%M:%S]`: The end of the time range to inspect.
* `--help`: Show this message and exit.

## `btvep ratelimit`

Global & API Key-specific Rate limit settings. Rate limits requires a Redis server.
Global rate limits can be overridden by setting rate limits on an api key.

**Usage**:

```console
$ btvep ratelimit [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-k, --key TEXT`: The API key (ID or the key itself) to view rate limits for.
* `--help`: Show this message and exit.

**Commands**:

* `add`: Add a rate limit.
* `delete`: Delete a rate limit.
* `disable`: Disable rate limiting.
* `enable`: Enable rate limiting.
* `set-redis-url`: Set the redis url to use for rate limiting.
* `status`: If rate limiting is enabled or not.

### `btvep ratelimit add`

Add a rate limit. Global rate limits do not apply to API keys with their own rate limits.

**Usage**:

```console
$ btvep ratelimit add [OPTIONS] TIMES SECONDS
```

**Arguments**:

* `TIMES`: How many times to allow in the given time period.  [required]
* `SECONDS`: The time period in seconds.  [required]

**Options**:

* `-k, --key TEXT`: The api key (ID or the key itself) to add the rate limit to. If not specified, the rate limit will be added to the global rate limits.
* `--help`: Show this message and exit.

### `btvep ratelimit delete`

Delete a rate limit.

**Usage**:

```console
$ btvep ratelimit delete [OPTIONS] INDEX
```

**Arguments**:

* `INDEX`: The index (starts at 0) of the rate limit to delete.  [required]

**Options**:

* `-k, --key TEXT`: The api key (ID or the key itself) to add the rate limit to. If not specified, the rate limit will be removed from the global rate limits.
* `--help`: Show this message and exit.

### `btvep ratelimit disable`

Disable rate limiting.
Alias for btvep config set rate_limiting_enabled False

**Usage**:

```console
$ btvep ratelimit disable [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `btvep ratelimit enable`

Enable rate limiting.

**Usage**:

```console
$ btvep ratelimit enable [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `btvep ratelimit set-redis-url`

Set the redis url to use for rate limiting. Defaults to redis://localhost
Alias for btvep config set redis_url <url>

**Usage**:

```console
$ btvep ratelimit set-redis-url [OPTIONS] URL
```

**Arguments**:

* `URL`: The redis url to set.  [required]

**Options**:

* `--help`: Show this message and exit.

### `btvep ratelimit status`

If rate limiting is enabled or not.

**Usage**:

```console
$ btvep ratelimit status [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `btvep start`

Start the API server.

**Usage**:

```console
$ btvep start [OPTIONS]
```

**Options**:

* `--port INTEGER`: The port to listen on.  [default: 8000]
* `-r, --reload`: Enable auto-reload on changes (for development).
* `--help`: Show this message and exit.
