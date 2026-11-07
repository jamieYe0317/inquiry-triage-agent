from eval.run_eval import score


def row(i, **kw):
    base = dict(
        id=f"r{i}",
        type="machine_trouble",
        segment="dtc",
        safety=False,
        expected_docs=["ts-fh340-jam"],
        team="Service desk",
        priority="normal",
        tags=[],
    )
    base.update(kw)
    return base


def pred(i, **kw):
    base = dict(
        id=f"r{i}",
        type="machine_trouble",
        segment="dtc",
        safety=False,
        confidence=0.9,
        retrieved=["ts-fh340-jam"],
        team="Service desk",
        cc=[],
        priority="normal",
        draft_removed=False,
        violations=[],
        input_flags=[],
        input_tokens=0,
        output_tokens=0,
        cost_usd=0.0,
        seconds=0.1,
    )
    base.update(kw)
    return base


def test_score_counts_hits_and_misses():
    rows = [
        row(1),
        row(2),
        row(3, type="unclear_other", expected_docs=[], team="Front desk", priority="low"),
        row(4, safety=True, priority="urgent", tags=["injection"]),
    ]
    preds = {
        p["id"]: p
        for p in [
            pred(1),
            pred(2, type="quality_complaint", team="Customer care", retrieved=["qa-returns-dtc"]),
            pred(3, type="unclear_other", team="Front desk", priority="low", retrieved=[]),
            pred(4, priority="urgent"),
        ]
    }
    m = score(rows, preds)
    assert m["type_accuracy"] == 75.0
    assert m["retrieval_hit_at_3"] == round(100 * 2 / 3, 1)
    assert m["retrieval_skip_accuracy"] == 100.0
    assert m["handoff_accuracy"] == 75.0
    assert m["safety_recall"] == 100.0
    assert m["injection_rows_handled"] == "1/1"


def test_score_counts_errors_as_wrong():
    rows = [row(1), row(2)]
    preds = {"r1": pred(1), "r2": {"id": "r2", "error": "boom", "seconds": 0.0}}
    m = score(rows, preds)
    assert m["errors"] == 1 and m["type_accuracy"] == 50.0
