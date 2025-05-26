# `filter`
A CLI tool for detecting if text is relevant to a prompt

I'm putting this here so I read it later - currently this tool
only looks at the first 10k characters of the very first chunk
of documents. This is a hack to save runtime, and not an
ideal long term approach

## Setup
### Installation
```bash
uv tool install git+https://github.com/WillChangeThisLater/filter
```

### Upgrade
```bash
uv tool upgrade filter
```

## Usage
```bash
QUERY="which of these documents are relevant to MCP"
vault search "$QUERY" --top-k 7 | filter "$QUERY"
```

## Roadmap
- Improve error messages
- Leverage the context window better
- Figure out why throttling errors are happening so often
