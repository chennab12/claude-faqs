"""Transparent arithmetic behind the calculators and the quiz. Illustrations, not vendor quotes."""
import math
import random
import zlib
from datetime import timedelta

WORDS_PER_TOKEN = 0.75  # common rule of thumb for English text; varies by tokenizer, language and code
PRICES_AS_OF = "6 October 2026"

# Example list prices in USD per million tokens for the Claude API (Anthropic first-party), as cached on PRICES_AS_OF.
# "cache_read" is the price of input served from the prompt cache. Haiku's cache-read price is assumed at 10% of input.
# Always confirm on https://platform.claude.com/docs/en/about-claude/pricing before relying on a number.
MODEL_PRICES = {
    "Claude Opus 5.5": {"input": 4.00, "output": 20.00, "cache_read": 0.20},
    "Claude Sonnet 5.5": {"input": 2.00, "output": 10.00, "cache_read": 0.20},
    "Claude Haiku 5.5": {"input": 0.10, "output": 0.50, "cache_read": 0.01},
    "Claude Fable 5.1": {"input": 10.00, "output": 50.00, "cache_read": 0.25},
}
CACHE_WRITE_MULTIPLIER = 1.25  # typical 5-minute cache write premium over the base input price
BATCH_DISCOUNT_PCT = 50.0  # Message Batches API discount for asynchronous work

# From the "Manage costs effectively" docs page: ≈ $13 per developer per active day on average; under $30 for 90% of users.
DOCS_AVG_COST_PER_ACTIVE_DAY = 13.0


def words_to_tokens(words):
    return math.ceil(words / WORDS_PER_TOKEN)


def tokens_to_words(tokens):
    return math.floor(tokens * WORDS_PER_TOKEN)


def api_cost(requests_per_day, input_tokens, output_tokens, price_in, price_out, cached_share_pct=0.0, cache_read_price=None, batch_share_pct=0.0):
    """Cost per request, day, 30-day month and year for an inference workload.

    `cached_share_pct` of input tokens are billed at `cache_read_price` (default 10% of input).
    `batch_share_pct` of requests get the Batch API discount on both input and output.
    """
    if cache_read_price is None:
        cache_read_price = price_in * 0.1
    cached = input_tokens * cached_share_pct / 100
    input_cost = ((input_tokens - cached) * price_in + cached * cache_read_price) / 1_000_000
    output_cost = output_tokens * price_out / 1_000_000
    full = input_cost + output_cost
    per_request = full * (1 - batch_share_pct / 100 * BATCH_DISCOUNT_PCT / 100)
    per_day = per_request * requests_per_day
    return {"per_request": per_request, "per_1k": per_request * 1000, "per_day": per_day, "per_month": per_day * 30, "per_year": per_day * 365}


def cost_per_success(cost_per_call, pass_rate):
    """What one good output really costs when some outputs fail and must be redone or discarded."""
    return cost_per_call / pass_rate if pass_rate else None


def caching_savings(prefix_tokens, calls, price_in, cache_read_price=None, write_multiplier=CACHE_WRITE_MULTIPLIER):
    """Cost of sending the same prompt prefix `calls` times, without and with prompt caching (one write, then reads)."""
    if cache_read_price is None:
        cache_read_price = price_in * 0.1
    without = prefix_tokens * calls * price_in / 1_000_000
    with_cache = (prefix_tokens * price_in * write_multiplier + prefix_tokens * max(calls - 1, 0) * cache_read_price) / 1_000_000 if calls else 0.0
    saved = without - with_cache
    return {"without": without, "with_cache": with_cache, "saved": saved, "saved_pct": saved / without if without else None}


def team_cost(developers, active_days_per_month, cost_per_active_day):
    """Monthly and yearly Claude Code spend for a team on usage-based billing."""
    monthly = developers * active_days_per_month * cost_per_active_day
    return {"monthly": monthly, "yearly": monthly * 12, "per_dev_month": monthly / developers if developers else None}


def productivity_roi(developers, hours_saved_per_week, loaded_hourly_cost, tool_cost_per_dev_month, weeks_per_month=4.33):
    """Monthly value of time saved vs tool cost. Time saved should come from measured pilot data, not hope."""
    value = developers * hours_saved_per_week * weeks_per_month * loaded_hourly_cost
    cost = developers * tool_cost_per_dev_month
    net = value - cost
    return {"value": value, "cost": cost, "net": net, "roi_multiple": value / cost if cost else None,
            "break_even_hours_per_week": tool_cost_per_dev_month / (weeks_per_month * loaded_hourly_cost) if loaded_hourly_cost else None}


def compound_success(step_success_pct, steps):
    """Chance an agent finishes when every one of `steps` must succeed independently."""
    return (step_success_pct / 100) ** steps


def parallel_throughput(tasks, agent_minutes_per_task, review_minutes_per_task, sessions):
    """Wall-clock hours for a batch of tasks with `sessions` parallel agents and one human reviewer.

    Agent work runs in parallel; your review is serial, so it becomes the bottleneck as sessions grow.
    """
    sessions = max(1, sessions)
    sequential = tasks * (agent_minutes_per_task + review_minutes_per_task) / 60
    agent_wall = math.ceil(tasks / sessions) * agent_minutes_per_task
    review_total = tasks * review_minutes_per_task
    # Review can overlap with later agent work; the batch can't finish before either stream does.
    parallel = max(agent_wall + review_minutes_per_task, review_total + agent_minutes_per_task) / 60 if tasks else 0.0
    return {"sequential_h": sequential, "parallel_h": parallel, "speedup": sequential / parallel if parallel else None,
            "review_bound": review_total >= agent_wall}


def weeks_to_finish(total_hours, hours_per_week):
    return total_hours / hours_per_week if hours_per_week > 0 else None


def study_schedule(items, hours_per_week, start):
    """Start and finish dates for each (title, hours) studied one after another."""
    if hours_per_week <= 0:
        return None
    rows = []
    day = start
    for title, hours in items:
        days = max(1, math.ceil(hours * 7 / hours_per_week))
        finish = day + timedelta(days=days - 1)
        rows.append({"Resource": title, "Hours (≈)": hours, "Start": day, "Finish": finish})
        day = finish + timedelta(days=1)
    return rows


def shuffled_options(item):
    """Options in a stable shuffled order (same every run) and the new index of the right answer."""
    order = list(range(len(item["options"])))
    random.Random(zlib.crc32(item["q"].encode())).shuffle(order)
    return [item["options"][i] for i in order], order.index(item["answer"])


def quiz_score(items, picks):
    """Number of picks (shown option text, or None) matching each item's correct answer."""
    return sum(1 for item, pick in zip(items, picks) if pick == item["options"][item["answer"]])
