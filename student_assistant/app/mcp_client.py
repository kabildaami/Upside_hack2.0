"""MCP client: run one stdio server per call and close it cleanly.

The public API remains: await tool_call(name, **kwargs).
Use a trusted student_id from authentication/session state, not a model-selected ID.
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "mcp_servers.json"


def _config() -> dict:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["servers"]


def _server_params(module: str) -> StdioServerParameters:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONUNBUFFERED"] = "1"

    return StdioServerParameters(
        command=sys.executable,
        args=["-m", module],
        env=env,
        cwd=str(ROOT),
    )

import time

async def _run_on_server(
    module: str,
    name: str | None = None,
    kwargs: dict | None = None,
    timeout: float = 120.0,
):
    started = time.perf_counter()

    def log(stage):
        elapsed = time.perf_counter() - started
        print(
            f"[MCP CLIENT] {module} | {stage} | {elapsed:.2f}s",
            file=sys.stderr,
            flush=True,
        )

    log("STARTING SUBPROCESS")

    async with stdio_client(
        _server_params(module),
        errlog=sys.stderr,
    ) as (read, write):

        log("SUBPROCESS CONNECTED")

        async with ClientSession(read, write) as session:

            await asyncio.wait_for(
                session.initialize(),
                timeout=20,
            )

            log("SESSION INITIALIZED")

            if name is None:
                result = await asyncio.wait_for(
                    session.list_tools(),
                    timeout=20,
                )
                log("TOOLS DISCOVERED")
                return [tool.name for tool in result.tools]

            log(f"CALLING TOOL: {name}")

            result = await asyncio.wait_for(
                session.call_tool(
                    name,
                    arguments=kwargs or {},
                ),
                timeout=timeout,
            )

            log(f"TOOL RESPONSE RECEIVED: {name}")

            if result.isError:
                raise RuntimeError(
                    f"MCP tool {name} returned error: {result.content}"
                )

            if result.structuredContent is not None:
                payload = result.structuredContent

                if isinstance(payload, dict) and set(payload) == {"result"}:
                    return payload["result"]

                return payload

            parts = [
                getattr(item, "text", "")
                for item in result.content
                if getattr(item, "type", "") == "text"
            ]

            if len(parts) == 1:
                try:
                    return json.loads(parts[0])
                except json.JSONDecodeError:
                    return parts[0]

            return parts



async def list_mcp_tools() -> dict[str, list[str]]:
    """Inspect each server once; unlike repeated per-tool discovery."""
    return {key: await _run_on_server(mod) for key, mod in _config().items()}


async def tool_call(name: str, **kwargs):
    """Call a named tool on the owning MCP server, with a bounded timeout."""
    servers = _config()
    # Cache tool-to-server mapping in-process, avoiding six ListTools requests per call.
    if not hasattr(tool_call, "_registry"):
        registry = {}
        for key, mod in servers.items():
            names = await _run_on_server(mod)
            for tool_name in names:
                if tool_name in registry:
                    raise RuntimeError(f"Duplicate MCP tool: {tool_name}")
                registry[tool_name] = mod
        tool_call._registry = registry
    module = tool_call._registry.get(name)
    if module is None:
        raise ValueError(f"Unknown MCP tool {name!r}; available: {sorted(tool_call._registry)}")
    return await _run_on_server(module, name, kwargs)
