# Agent Skills

Skills for AI Agents.

## About Agent Skills

See [Anthropic official document](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## Usage

### Pre-required

- [mise](https://mise.jdx.dev)

### Setup

1. Trust project directory and install tools.

    ```sh
    mise trust -q && mise install
    ```

2. Setup tools.

    ```sh
    mise setup
    ```

### Use skills as global

Create a symbolic link to your Claude directory to use skills as global.

```sh
mise run link
```
