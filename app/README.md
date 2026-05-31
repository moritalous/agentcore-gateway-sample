# Strands Agents Tool Search Sample

This sample starts a Strands agent with only a local `tool_search` tool.
The tool searches an AgentCore Gateway, loads the matched MCP tools, and registers them on the running agent.

## Setup

Copy `.env.sample` to `.env` and set your AgentCore Gateway ID.

```bash
cp .env.sample .env
```

```env
AWS_REGION=ap-northeast-1
MODEL_ID=jp.anthropic.claude-haiku-4-5-20251001-v1:0
GATEWAY_ID=your-gateway-id
```

The sample uses the default AWS credential chain.

## Run

```bash
uv run main.py
```
