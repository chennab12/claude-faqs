"""Smoke tests: every section, lab and calculator renders; navigation, plan and quiz work."""
from streamlit.testing.v1 import AppTest

from content import FAST_TRACK, STAGES
from resources import RESOURCES

CALCS = ["👥 Team cost", "📈 Productivity ROI", "🔢 Tokens & context", "🧊 Prompt caching savings",
         "💸 API inference cost", "🦾 Agent reliability", "🤖 Parallel throughput", "⏱️ Study time"]


def run(section=None):
    at = AppTest.from_file("../app.py", default_timeout=30)
    if section is not None:
        at.session_state["section"] = section
    at.run()
    assert not at.exception, at.exception
    return at


def test_every_section_renders():
    at = run()
    for section in at.sidebar.radio[0].options:
        run(section)


def test_next_stage_button_advances():
    at = run(STAGES[0]["name"])
    [b for b in at.button if b.label == "Next stage →"][0].click().run()
    assert at.session_state["section"] == STAGES[1]["name"]


def test_fast_track_fills_plan():
    at = run()
    [b for b in at.button if b.label.startswith("➕ Add the fast track")][0].click().run()
    assert at.session_state["plan"] == [k for k in FAST_TRACK if RESOURCES[k]["hours"]]
    at.session_state["section"] = "🗓️ My learning plan"
    at.run()
    assert not at.exception, at.exception


def test_quick_check_gives_feedback():
    key = f"tq_{STAGES[0]['topics'][0]['title']}_0"
    at = run(STAGES[0]["name"])
    at.radio(key=key).set_value(at.radio(key=key).options[0]).run()
    assert not at.exception, at.exception
    assert len(at.success) + len(at.error) >= 2  # gist banner plus the answer feedback


def test_every_concept_shows_tpm_takeaway_and_docs():
    at = run(STAGES[3]["name"])
    tpm = [w for w in at.warning if "TPM takeaway" in w.value]
    assert len(tpm) == len(STAGES[3]["topics"])
    assert any("code.claude.com/docs/en/" in m.value for m in at.markdown)


def test_stage_quiz_button_filters_quiz_and_scores():
    at = run(STAGES[2]["name"])
    [b for b in at.button if b.label.startswith("📝 Take the full")][0].click().run()
    assert at.session_state["section"] == "📝 Quiz center"
    assert at.session_state["quiz_stages"] == [STAGES[2]["name"]]
    radios = [r for r in at.radio if r.key and r.key.startswith("quiz_")]
    assert radios
    for r in radios:
        r.set_value(r.options[0])
    [b for b in at.button if b.label == "✅ Check my answers"][0].click().run()
    assert not at.exception, at.exception
    assert len(at.session_state["quiz_history"]) == 1
    score, total = at.session_state["quiz_history"][0]
    assert total == len(radios) and 0 <= score <= total


def test_each_calculator_renders():
    at = run("🧮 Calculators")
    for option in CALCS:
        at.button_group[0].set_value(option).run()
        assert not at.exception, at.exception


def test_deep_link_opens_section():
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.query_params["page"] = "hooks-automation"
    at.run()
    assert not at.exception, at.exception
    assert at.session_state["section"] == STAGES[6]["name"]


def test_missed_questions_feed_review_mode():
    at = run("📝 Quiz center")
    [b for b in at.button if b.label == "✅ Check my answers"][0].click().run()  # all unanswered = all missed
    missed = at.session_state["missed"]
    assert len(missed) == 10
    at.button_group(key="quiz_mode").set_value("🔁 My missed questions (10)").run()
    assert not at.exception, at.exception
    shown = [r.label for r in at.radio if r.key and r.key.startswith("quiz_")]
    assert shown and all(any(q in label for q in missed) for label in shown)
    assert at.session_state["quiz_stats"]


def test_search_finds_concepts():
    at = run("🔎 Search everything")
    at.text_input[0].set_value("worktree").run()
    assert not at.exception, at.exception
    assert any(b.label == "Open stage →" for b in at.button)


def test_continue_button_opens_first_unmastered_stage():
    at = run()
    [b for b in at.button if b.label.startswith("▶️ Continue")][0].click().run()
    assert at.session_state["section"] == STAGES[0]["name"]


def test_permission_lab_classifies_commands():
    at = run(STAGES[3]["name"])
    table = at.dataframe[[i for i, d in enumerate(at.dataframe) if "Decision" in d.value.columns][0]].value
    decisions = dict(zip(table["Command"], table["Decision"]))
    assert decisions["rm -rf build"].startswith("⛔")
    assert decisions["git push origin main"].startswith("❓")
    assert decisions["npm run test"].startswith("✅")
    assert decisions["npm install"].startswith("➖")
    at.text_area(key="lab_perm_deny").set_value("Bash(npm *)").run()
    assert not at.exception, at.exception


def test_labs_respond_to_input():
    at = run(STAGES[8]["name"])
    at.selectbox(key="lab_hl_fmt").set_value("stream-json").run()
    assert not at.exception, at.exception
    assert any("--verbose" in c.value for c in at.code)
    at = run(STAGES[7]["name"])
    at.slider(key="lab_par_sessions").set_value(10).run()
    assert not at.exception, at.exception
    at = run(STAGES[2]["name"])
    at.slider(key="lab_ctx_files").set_value(300).run()
    assert not at.exception, at.exception


def test_prerequisite_review_button_goes_to_earlier_stage():
    at = run(STAGES[4]["name"])
    [b for b in at.button if b.label == f"↩️ Review {STAGES[2]['name']}"][0].click().run()
    assert at.session_state["section"] == STAGES[2]["name"]
