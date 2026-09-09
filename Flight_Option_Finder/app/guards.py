"""Unit 2-style defended tool executor.

Defences:
1. whitelist
2. argument/type failures are not retried
3. transient failures can be retried
4. unusable output is converted into an honest observation
"""

from dataclasses import dataclass
import time


@dataclass
class ToolResult:
    name: str
    ok: bool
    observation: str
    attempts: int = 1


def _looks_usable(value):
    if not isinstance(value, str):
        return False
    cleaned = value.strip()
    if not cleaned:
        return False
    if "\x00" in cleaned:
        return False
    if "<html" in cleaned.lower() or "502 bad gateway" in cleaned.lower():
        return False
    return True


def call_tool(name, args, registry, retries=2, backoff=0.0):
    if name not in registry:
        return ToolResult(
            name=name,
            ok=False,
            observation=f"Error: no tool named '{name}'. Available: {list(registry)}",
            attempts=1,
        )

    attempts = 0
    while attempts <= retries:
        attempts += 1
        try:
            result = registry[name](**args)
        except TypeError as exc:
            return ToolResult(
                name=name,
                ok=False,
                observation=f"Tool '{name}' received invalid arguments: {exc}",
                attempts=attempts,
            )
        except Exception as exc:
            if attempts <= retries:
                if backoff:
                    time.sleep(backoff)
                continue
            return ToolResult(
                name=name,
                ok=False,
                observation=f"Tool '{name}' failed after {attempts} attempts. Last error: {exc}",
                attempts=attempts,
            )

        if not _looks_usable(result):
            return ToolResult(
                name=name,
                ok=False,
                observation=(
                    f"Tool '{name}' returned unusable output. Treat it as no data "
                    "and either try a different approach or say so."
                ),
                attempts=attempts,
            )

        return ToolResult(name=name, ok=True, observation=result, attempts=attempts)

    return ToolResult(
        name=name,
        ok=False,
        observation=f"Tool '{name}' failed after {attempts} attempts.",
        attempts=attempts,
    )
