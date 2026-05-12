"""Claude Code Status Line command.
Reads JSON from stdin, outputs a compact status line showing:
  model_id | usage_pct%% used/total | cache_hit%% | Effort:level
Example:  deepseek-v4-pro[1M] | 12% 24K/200K | Cache:8% | XHIGH
"""
import json
import sys


def fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.0f}K"
    return str(n)


def get_effort(data: dict) -> str:
    """Extract effort / thinking level from statusline JSON."""
    for path in [
        'effort_level',
        'effortLevel',
        'effort',
        'thinking_level',
        'thinkingLevel',
    ]:
        val = data.get(path)
        if val:
            return str(val).upper()
    # Also check nested under model
    model = data.get('model', {})
    if isinstance(model, dict):
        for path in ['effort_level', 'effortLevel', 'effort']:
            val = model.get(path)
            if val:
                return str(val).upper()
    return ''


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("--")
        return

    model_id = data.get("model", {}).get("id", "?")
    ctx = data.get("context_window", {})
    used_pct = ctx.get("used_percentage")
    usage = ctx.get("current_usage", {})
    input_tokens = usage.get("input_tokens", 0)
    ctx_size = ctx.get("context_window_size", 0)
    cache_read = usage.get("cache_read_input_tokens", 0)
    cache_create = usage.get("cache_creation_input_tokens", 0)
    cache_total = cache_read + cache_create

    parts = [model_id]

    if used_pct is not None:
        pct_str = f"{used_pct:.0f}%"
        used_str = fmt_tokens(input_tokens)
        total_str = fmt_tokens(ctx_size)
        parts.append(f"{pct_str} {used_str}/{total_str}")
    else:
        parts.append(f"0% 0/{fmt_tokens(ctx_size)}")

    if cache_total > 0:
        hit_pct = cache_read * 100 // cache_total
        parts.append(f"Cache:{hit_pct}%")

    effort = get_effort(data)
    if effort:
        parts.append(f"Effort:{effort}")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
