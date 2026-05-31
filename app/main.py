import os

from dotenv import load_dotenv
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
from strands import Agent, ToolContext, tool
from strands.hooks import BeforeModelCallEvent, HookRegistry
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient

load_dotenv()

AWS_REGION = os.environ["AWS_REGION"]
MODEL_ID = os.environ["MODEL_ID"]
GATEWAY_ID = os.environ["GATEWAY_ID"]

GATEWAY_URL = (
    f"https://{GATEWAY_ID}.gateway.bedrock-agentcore.{AWS_REGION}.amazonaws.com/mcp"
)

PROMPT = "Bedrock AgentCoreの最新情報を教えて"


class ModelCallToolLogger:
    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeModelCallEvent, self.log_tools)

    def log_tools(self, event: BeforeModelCallEvent) -> None:
        tool_names = event.agent.tool_names
        print(f"tools: count={len(tool_names)} names={tool_names}")


def main():
    with MCPClient(
        lambda: aws_iam_streamablehttp_client(
            endpoint=GATEWAY_URL,
            aws_region=AWS_REGION,
            aws_service="bedrock-agentcore",
        )
    ) as mcp_client:

        @tool(context=True)
        def tool_search(query: str, tool_context: ToolContext) -> str:
            """Search the AgentCore gateway for the best matching tools and load them."""

            # ツール検索ツールを実行
            search_result = mcp_client.call_tool_sync(
                tool_use_id="agentcore-tool-search",
                name="x_amz_bedrock_agentcore_search",
                arguments={"query": query},
            )

            # 見つかったツール名
            matched_tool_names = [
                tool["name"]
                for tool in search_result["structuredContent"].get("tools", [])
            ]

            # 見つかったツール
            mcp_tools = mcp_client.list_tools_sync(
                tool_filters={"allowed": matched_tool_names}
            )

            # 見つかったツールを追加
            tool_context.agent.tool_registry.process_tools(mcp_tools)

            # ツール検索ツールの実行結果を返却
            return "Loaded tools: " + ", ".join(matched_tool_names)

        agent = Agent(
            model=BedrockModel(model_id=MODEL_ID, region_name=AWS_REGION),
            tools=[tool_search],
            hooks=[ModelCallToolLogger()],
            callback_handler=None,
        )

        print(agent(PROMPT))


if __name__ == "__main__":
    main()
