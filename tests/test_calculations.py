from datetime import date

import pytest

from calculations import (
    MODEL_PRICES,
    api_cost,
    caching_savings,
    compound_success,
    cost_per_success,
    parallel_throughput,
    productivity_roi,
    quiz_score,
    shuffled_options,
    study_schedule,
    team_cost,
    tokens_to_words,
    weeks_to_finish,
    words_to_tokens,
)


def test_tokens_round_trip():
    assert words_to_tokens(750) == 1000
    assert tokens_to_words(1000) == 750


def test_api_cost():
    c = api_cost(1000, 1_000_000, 0, 3.0, 15.0)
    assert c["per_request"] == pytest.approx(3.0)
    assert c["per_month"] == pytest.approx(90_000) and c["per_year"] == pytest.approx(1_095_000)
    full = api_cost(1, 1_000_000, 0, 10, 0)["per_request"]
    assert api_cost(1, 1_000_000, 0, 10, 0, cached_share_pct=100)["per_request"] == pytest.approx(full * 0.1)
    assert api_cost(1, 1_000_000, 0, 10, 0, cached_share_pct=100, cache_read_price=2)["per_request"] == pytest.approx(2)
    assert api_cost(1, 1_000_000, 0, 10, 0, batch_share_pct=100)["per_request"] == pytest.approx(full * 0.5)


def test_model_prices_are_sane():
    for name, p in MODEL_PRICES.items():
        assert 0 < p["cache_read"] < p["input"] < p["output"], name


def test_cost_per_success():
    assert cost_per_success(0.01, 0.5) == pytest.approx(0.02)
    assert cost_per_success(0.01, 0) is None


def test_caching_savings():
    c = caching_savings(1_000_000, 10, 10.0, 1.0)
    assert c["without"] == pytest.approx(100)
    assert c["with_cache"] == pytest.approx(12.5 + 9)
    assert c["saved_pct"] == pytest.approx(0.785)
    assert caching_savings(1_000_000, 1, 10.0)["saved"] < 0  # a single call only pays the write premium
    assert caching_savings(1000, 0, 10.0)["saved_pct"] is None


def test_team_cost():
    c = team_cost(10, 20, 13)
    assert c["monthly"] == 2600 and c["yearly"] == 31_200 and c["per_dev_month"] == 260
    assert team_cost(0, 20, 13)["per_dev_month"] is None


def test_productivity_roi():
    r = productivity_roi(10, 2, 100, 200, weeks_per_month=4)
    assert r["value"] == 8000 and r["cost"] == 2000 and r["net"] == 6000 and r["roi_multiple"] == 4
    assert r["break_even_hours_per_week"] == pytest.approx(0.5)
    assert productivity_roi(10, 2, 100, 0)["roi_multiple"] is None


def test_compound_success():
    assert compound_success(100, 50) == 1
    assert compound_success(90, 2) == pytest.approx(0.81)


def test_parallel_throughput():
    one = parallel_throughput(12, 40, 0, 1)
    assert one["sequential_h"] == pytest.approx(8) and one["parallel_h"] == pytest.approx(8)
    four = parallel_throughput(12, 40, 0, 4)
    assert four["speedup"] == pytest.approx(4)
    review_heavy = parallel_throughput(12, 10, 30, 6)
    assert review_heavy["review_bound"]
    assert parallel_throughput(12, 10, 30, 10)["parallel_h"] == pytest.approx(review_heavy["parallel_h"])
    assert parallel_throughput(0, 10, 10, 2)["speedup"] is None


def test_study_time():
    assert weeks_to_finish(100, 5) == 20 and weeks_to_finish(10, 0) is None
    rows = study_schedule([("A", 10), ("B", 5)], 5, date(2026, 1, 5))
    assert rows[0]["Finish"] == date(2026, 1, 18) and rows[1]["Start"] == date(2026, 1, 19)
    assert study_schedule([("A", 1)], 0, date(2026, 1, 5)) is None


def test_quiz_helpers():
    item = {"q": "Which?", "options": ["a", "b", "c", "d"], "answer": 2}
    options, answer = shuffled_options(item)
    assert sorted(options) == item["options"] and options[answer] == "c"
    assert shuffled_options(item) == (options, answer)  # stable across runs
    assert quiz_score([item, item], ["c", None]) == 1
