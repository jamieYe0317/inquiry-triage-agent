# Label agreement: golden labels versus a blind second annotator

A second Claude agent labeled 80 random rows from `LABELING.md` alone, without the golden labels. This measures how clear the labels are. It is not a human check.

| Label | Agreement |
|---|---:|
| type | 76/80 (95%) |
| segment | 80/80 (100%) |
| safety | 80/80 (100%) |

## Disagreements

- `inq-0460` (QB-safety, tags ['hidden_safety']): type: golden `quality_complaint`, blind `unclear_other`. Blind note: invoice request main; fuel leak and heat reported secondhand, safety borderline
- `inq-0081` (MT-fuel-leak, tags ['angry']): type: golden `machine_trouble`, blind `quality_complaint`. Blind note: fuel leak on new-sounding unit with refund demand; could be machine_trouble
- `inq-0072` (MT-340-vibe, tags ['angry']): type: golden `machine_trouble`, blind `quality_complaint`
- `inq-0465` (QB-safety, tags ['hidden_safety']): type: golden `quality_complaint`, blind `unclear_other`. Blind note: three mixed asks, none dominant; secondhand fuel seep and heat report

## What changed after the review

The numbers above compare the blind labels with the golden labels before review. I read the 4 disagreements on 2026-11-07:

- `inq-0072`, `inq-0081`, `inq-0460`: the writer drifted from the scenario. The blind label was closer to `LABELING.md`. I changed these labels in `scripts/label_fixes.json`, with a reason for each.
- `inq-0465`: kept as `quality_complaint`. The safety report takes the most words of the three requests (rule 1).

These rows also show a real limit: some inquiries hold two or three requests, and "the main request" is a judgment call.
