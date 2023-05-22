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
* `key`: Manage api keys.
* `start`: Start the api server.

## `btvep config`

Update and read config values. Config values available:



    - hotkey_mnemonic



Example usage:

- btvep config set hotkey_mnemonic "my mnemonic"

- btvep config get hotkey_mnemonic

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

Manage api keys.

**Usage**:

```console
$ btvep key [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Create a new api key.
* `delete`: Deletes an api key.
* `edit`: Edit an api key.
* `list`: List all api keys.

### `btvep key create`

Create a new api key.

**Usage**:

```console
$ btvep key create [OPTIONS]
```

**Options**:

* `-n, --name TEXT`: The name of the api key.
* `-v, --valid-until INTEGER`: The unix timestamp when the api key expires. Defaults to -1 which means that the key never expires.  [default: -1]
* `-c, --credits INTEGER`: The number of credits the api key has. -1 means unlimited.  [default: -1]
* `-e, --enabled`: Whether the api key is enabled. Disabled keys cannot make requests.  [default: True]
* `--help`: Show this message and exit.

### `btvep key delete`

Deletes an api key.

**Usage**:

```console
$ btvep key delete [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: The api key to delete. Can be specified by either the key or its numerical id.  [required]

**Options**:

* `--help`: Show this message and exit.

### `btvep key edit`

Edit an api key.

**Usage**:

```console
$ btvep key edit [OPTIONS] QUERY
```

**Arguments**:

* `QUERY`: The api key to edit. Can be specified by either the key or its numerical id.  [required]

**Options**:

* `-k, --api-key-hint TEXT`
* `-n, --name TEXT`
* `-r, --request-count INTEGER`
* `-u, --valid-until INTEGER`
* `-c, --credits INTEGER`
* `-e, --enabled`
* `--help`: Show this message and exit.

### `btvep key list`

List all api keys.

**Usage**:

```console
$ btvep key list [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `btvep start`

Start the api server.

**Usage**:

```console
$ btvep start [OPTIONS]
```

**Options**:

* `--port INTEGER`: The port to listen on.  [default: 8000]
* `--help`: Show this message and exit.
