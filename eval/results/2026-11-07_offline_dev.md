# Eval: offline on dev (281 rows, 1 run(s))

Date: 2026-11-07. Model: none (keyword router + template drafter). Golden set: data/eval/golden.jsonl.

| Metric | Mean | Lowest run |
|---|---:|---:|
| rows | 281 | 281 |
| errors | 0 | 0 |
| type_accuracy | 76.9 | 76.9 |
| type_macro_f1 | 77.4 | 77.4 |
| segment_accuracy | 94.3 | 94.3 |
| retrieval_hit_at_3 | 75.3 | 75.3 |
| retrieval_hit_at_3_when_type_correct | 95.2 | 95.2 |
| retrieval_skip_accuracy | 47.6 | 47.6 |
| team_accuracy | 76.2 | 76.2 |
| priority_accuracy | 78.6 | 78.6 |
| handoff_accuracy | 73.0 | 73.0 |
| safety_recall | 63.0 | 63.0 |
| safety_precision | 73.9 | 73.9 |
| drafts_with_promise_language | 0 | 0 |
| drafts_removed_by_guard | 0 | 0 |
| shipped_drafts_with_violations | 0 | 0 |
| injection_rows_handled | 7/9 |  |
| cost_usd_per_inquiry | 0 | 0 |
| tokens_per_inquiry | 0 | 0 |
| seconds_median | 0.0 | 0.0 |
| seconds_p95 | 0.0 | 0.0 |

## Confusion matrix (rows = label, columns = prediction), run 1

| label \ predicted | machine_trouble | quality_complaint | partner_request | unclear_other | error |
|---|---:|---:|---:|---:|---:|
| machine_trouble | 66 | 4 | 0 | 11 | 0 |
| quality_complaint | 12 | 57 | 0 | 7 | 0 |
| partner_request | 2 | 3 | 44 | 6 | 0 |
| unclear_other | 8 | 8 | 4 | 49 | 0 |

## Breakdown, run 1

| Group | n | Type accuracy | Hand-off accuracy |
|---|---:|---:|---:|
| segment=b2b | 141 | 73.8 | 70.2 |
| segment=dtc | 140 | 80.0 | 75.7 |
| tag=angry | 7 | 85.7 | 85.7 |
| tag=hidden_safety | 12 | 33.3 | 25.0 |
| tag=injection | 9 | 77.8 | 77.8 |
| tag=long_rambling | 9 | 77.8 | 55.6 |
| tag=mixed_intent | 13 | 84.6 | 84.6 |
| tag=no_model | 7 | 100.0 | 100.0 |
| tag=none | 188 | 78.7 | 74.5 |
| tag=spanish | 11 | 45.5 | 45.5 |
| tag=typos | 18 | 77.8 | 77.8 |
| tag=very_short | 7 | 100.0 | 100.0 |
| type=machine_trouble | 81 | 81.5 | 70.4 |
| type=partner_request | 55 | 80.0 | 80.0 |
| type=quality_complaint | 76 | 75.0 | 72.4 |
| type=unclear_other | 69 | 71.0 | 71.0 |

## Failures, run 1 (95 rows; first 60 shown, all in the JSON file)

- `inq-0001` [] handoff Service desk/normal -> Service desk/urgent
- `inq-0015` ['spanish'] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fhg7-nostart'] not in []
- `inq-0022` [] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/urgent; docs ['ts-fhg7-output'] not in []
- `inq-0026` [] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/urgent; docs ['man-fh210'] not in []
- `inq-0033` ['long_rambling'] segment dtc -> b2b; handoff Service desk/normal -> Service desk/high
- `inq-0038` ['spanish'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/low; docs ['ts-engine-general'] not in []
- `inq-0042` [] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fhg7-nostart'] not in []
- `inq-0048` ['hidden_safety'] handoff Service desk/urgent -> Service desk/normal
- `inq-0051` ['hidden_safety'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/low; docs ['ts-fhp90-pressure'] not in []
- `inq-0052` ['long_rambling'] handoff Service desk/normal -> Service desk/urgent; docs ['ts-fhg7-nostart'] not in ['war-summary', 'ts-fhg7-output', 'man-fhg7']
- `inq-0055` [] handoff Service desk/normal -> Service desk/urgent
- `inq-0067` ['hidden_safety'] type machine_trouble -> quality_complaint; handoff Service desk/urgent -> Customer care/urgent; docs ['man-fh210'] not in ['qa-safety-escalation', 'qa-defect-report', 'war-summary']
- `inq-0077` [] handoff Service desk/normal -> Service desk/urgent; docs ['war-summary'] not in ['ts-fh210-hydraulic', 'ts-engine-general', 'man-fh210']
- `inq-0086` ['spanish'] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fh520-teeth'] not in []
- `inq-0087` [] type machine_trouble -> quality_complaint; handoff Service desk/urgent -> Customer care/urgent; docs ['man-fh210'] not in ['war-summary', 'qa-parts-replacement', 'qa-safety-escalation']
- `inq-0089` ['spanish'] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fh210-hydraulic', 'man-fh210'] not in []
- `inq-0093` [] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/urgent; docs ['ts-fh210-hydraulic'] not in []
- `inq-0104` [] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fhg7-nostart'] not in []
- `inq-0106` ['hidden_safety'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/low; docs ['ts-fhp90-pressure'] not in ['gen-parts-order', 'gen-shipping', 'gen-contact']
- `inq-0139` ['typos'] type quality_complaint -> unclear_other; handoff Customer care/urgent -> Front desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['gen-shipping', 'gen-parts-order', 'gen-contact']
- `inq-0149` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'war-summary'] not in ['ts-fh340-jam', 'man-fh340', 'ts-fh340-vibration']
- `inq-0153` ['hidden_safety'] type quality_complaint -> unclear_other; handoff Customer care/urgent -> Front desk/low; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in []
- `inq-0155` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'war-summary'] not in ['man-fh210', 'ts-fh210-hydraulic', 'ts-engine-general']
- `inq-0159` [] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['man-fhg7', 'ts-fhg7-nostart', 'ts-engine-general']
- `inq-0162` [] docs ['qa-returns-dtc'] not in ['qa-safety-escalation', 'war-summary', 'qa-defect-report']
- `inq-0164` [] docs ['qa-returns-dtc'] not in ['qa-safety-escalation', 'qa-parts-replacement', 'war-summary']
- `inq-0166` ['hidden_safety'] type quality_complaint -> unclear_other; handoff Customer care/urgent -> Front desk/low; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['gen-parts-order', 'gen-shipping', 'gen-contact']
- `inq-0168` [] type quality_complaint -> unclear_other; handoff Customer care/normal -> Front desk/low; docs ['qa-returns-dtc', 'war-summary'] not in []
- `inq-0174` [] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['man-fh210', 'ts-fh210-hydraulic', 'ts-engine-general']
- `inq-0196` ['long_rambling'] type unclear_other -> machine_trouble; segment dtc -> b2b; handoff Front desk/low -> Service desk/high; docs ['gen-contact'] not in ['man-fh520', 'ts-engine-general', 'man-fhp90']
- `inq-0202` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['war-summary', 'man-fh340', 'ts-fh340-vibration']
- `inq-0217` [] type unclear_other -> partner_request; segment dtc -> b2b; handoff Front desk/low -> Partner team/normal; retrieved ['par-marketing', 'par-territory', 'par-overview'] but none needed
- `inq-0225` ['injection'] segment dtc -> b2b
- `inq-0228` ['typos'] retrieved ['gen-contact', 'gen-shipping', 'gen-parts-order'] but none needed
- `inq-0229` [] segment dtc -> b2b; retrieved ['gen-contact', 'gen-parts-order', 'gen-shipping'] but none needed
- `inq-0251` [] type unclear_other -> partner_request; segment dtc -> b2b; handoff Front desk/low -> Partner team/normal; retrieved ['par-territory', 'par-overview', 'par-apply'] but none needed
- `inq-0254` ['spanish'] docs ['gen-contact'] not in []
- `inq-0256` [] segment dtc -> b2b
- `inq-0258` ['typos'] retrieved ['gen-shipping', 'gen-contact', 'gen-parts-order'] but none needed
- `inq-0262` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; retrieved ['man-fh340', 'ts-fh340-jam', 'man-fh210'] but none needed
- `inq-0268` ['long_rambling'] retrieved ['gen-shipping', 'gen-parts-order'] but none needed
- `inq-0274` [] retrieved ['gen-shipping', 'gen-parts-order', 'gen-contact'] but none needed
- `inq-0276` [] type unclear_other -> quality_complaint; handoff Front desk/low -> Customer care/normal; retrieved ['qa-defect-report', 'qa-returns-dtc', 'qa-safety-escalation'] but none needed
- `inq-0279` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-contact'] not in ['war-summary', 'ts-fh210-hydraulic', 'man-fh210']
- `inq-0301` [] type partner_request -> quality_complaint; handoff Partner team/normal -> Quality team/high; docs ['par-overview', 'par-tiers'] not in ['war-summary', 'qa-safety-escalation', 'qa-defect-report']
- `inq-0302` ['typos'] type partner_request -> machine_trouble; handoff Partner team/normal -> Service desk/high; docs ['par-apply'] not in ['ts-engine-general', 'war-summary', 'ts-fh210-hydraulic']
- `inq-0311` [] type partner_request -> quality_complaint; handoff Partner team/normal -> Quality team/high; docs ['par-overview', 'par-tiers'] not in ['war-summary', 'qa-safety-escalation', 'qa-parts-replacement']
- `inq-0323` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-apply', 'par-overview'] not in []
- `inq-0327` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-overview', 'par-tiers'] not in []
- `inq-0331` [] docs ['par-tiers'] not in ['par-apply', 'par-territory', 'par-overview']
- `inq-0346` ['injection'] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-apply', 'par-overview'] not in ['gen-contact', 'gen-parts-order', 'gen-shipping']
- `inq-0349` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-territory', 'par-overview'] not in ['gen-parts-order', 'gen-contact']
- `inq-0359` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-apply', 'par-overview'] not in []
- `inq-0372` ['long_rambling'] type partner_request -> machine_trouble; handoff Partner team/normal -> Service desk/high; docs ['par-territory', 'par-overview'] not in ['ts-engine-general', 'ts-fhp90-pressure', 'man-fh340']
- `inq-0373` [] type partner_request -> quality_complaint; handoff Partner team/normal -> Quality team/high; docs ['par-apply'] not in ['qa-defect-report', 'qa-returns-dtc', 'qa-safety-escalation']
- `inq-0385` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-apply', 'par-overview'] not in []
- `inq-0391` ['typos'] type quality_complaint -> machine_trouble; segment b2b -> dtc; handoff Quality team/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-defect-report'] not in ['ts-fhg7-nostart', 'man-fhg7', 'ts-fhg7-output']
- `inq-0403` [] docs ['qa-defect-report'] not in ['war-summary', 'qa-freight-damage', 'qa-safety-escalation']
- `inq-0409` ['very_short'] docs ['qa-defect-report'] not in ['qa-freight-damage', 'qa-safety-escalation', 'qa-parts-replacement']
- `inq-0411` [] type quality_complaint -> unclear_other; handoff Quality team/urgent -> Front desk/urgent; docs ['qa-safety-escalation', 'qa-defect-report'] not in ['gen-parts-order', 'gen-contact', 'gen-shipping']
