# Eval: offline on test (279 rows, 1 run(s))

Date: 2026-11-07. Model: none (keyword router + template drafter). Golden set: data/eval/golden.jsonl.

| Metric | Mean | Lowest run |
|---|---:|---:|
| rows | 279 | 279 |
| errors | 0 | 0 |
| type_accuracy | 74.9 | 74.9 |
| type_macro_f1 | 75.8 | 75.8 |
| segment_accuracy | 90.7 | 90.7 |
| retrieval_hit_at_3 | 70.2 | 70.2 |
| retrieval_hit_at_3_when_type_correct | 94.0 | 94.0 |
| retrieval_skip_accuracy | 61.8 | 61.8 |
| team_accuracy | 73.5 | 73.5 |
| priority_accuracy | 79.2 | 79.2 |
| handoff_accuracy | 70.3 | 70.3 |
| safety_recall | 71.4 | 71.4 |
| safety_precision | 83.3 | 83.3 |
| drafts_with_promise_language | 0 | 0 |
| drafts_removed_by_guard | 0 | 0 |
| shipped_drafts_with_violations | 0 | 0 |
| injection_rows_handled | 5/5 |  |
| cost_usd_per_inquiry | 0 | 0 |
| tokens_per_inquiry | 0 | 0 |
| seconds_median | 0.0 | 0.0 |
| seconds_p95 | 0.0 | 0.0 |

## Confusion matrix (rows = label, columns = prediction), run 1

| label \ predicted | machine_trouble | quality_complaint | partner_request | unclear_other | error |
|---|---:|---:|---:|---:|---:|
| machine_trouble | 66 | 7 | 0 | 9 | 0 |
| quality_complaint | 20 | 51 | 0 | 4 | 0 |
| partner_request | 0 | 0 | 43 | 12 | 0 |
| unclear_other | 10 | 6 | 2 | 49 | 0 |

## Breakdown, run 1

| Group | n | Type accuracy | Hand-off accuracy |
|---|---:|---:|---:|
| segment=b2b | 139 | 74.8 | 67.6 |
| segment=dtc | 140 | 75.0 | 72.9 |
| tag=angry | 6 | 66.7 | 50.0 |
| tag=hidden_safety | 12 | 25.0 | 25.0 |
| tag=injection | 5 | 100.0 | 100.0 |
| tag=long_rambling | 9 | 100.0 | 88.9 |
| tag=mixed_intent | 9 | 77.8 | 66.7 |
| tag=no_model | 6 | 66.7 | 66.7 |
| tag=none | 190 | 78.4 | 74.2 |
| tag=spanish | 11 | 27.3 | 27.3 |
| tag=typos | 18 | 88.9 | 83.3 |
| tag=very_short | 13 | 69.2 | 61.5 |
| type=machine_trouble | 82 | 80.5 | 72.0 |
| type=partner_request | 55 | 78.2 | 78.2 |
| type=quality_complaint | 75 | 68.0 | 61.3 |
| type=unclear_other | 67 | 73.1 | 71.6 |

## Failures, run 1 (105 rows; first 60 shown, all in the JSON file)

- `inq-0007` ['spanish'] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fh210-hydraulic', 'man-fh210'] not in []
- `inq-0008` ['hidden_safety'] docs ['ts-engine-general'] not in ['man-fhg7', 'ts-fhg7-output', 'ts-fhg7-nostart']
- `inq-0011` ['hidden_safety'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/urgent; docs ['man-fh210'] not in []
- `inq-0013` [] docs ['war-summary'] not in ['man-fh520', 'ts-fh520-teeth', 'ts-engine-general']
- `inq-0016` ['angry'] type machine_trouble -> quality_complaint; handoff Service desk/normal -> Customer care/normal; docs ['ts-fh340-jam'] not in ['qa-returns-dtc', 'qa-safety-escalation', 'war-summary']
- `inq-0020` ['very_short'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/low; docs ['ts-fhp90-pressure'] not in []
- `inq-0032` ['spanish'] type machine_trouble -> unclear_other; segment dtc -> b2b; handoff Service desk/normal -> Front desk/low; docs ['ts-fh340-vibration'] not in []
- `inq-0035` ['hidden_safety'] type machine_trouble -> quality_complaint; handoff Service desk/urgent -> Customer care/urgent; docs ['ts-fhp90-pressure'] not in ['qa-defect-report', 'qa-safety-escalation', 'war-summary']
- `inq-0054` [] type machine_trouble -> quality_complaint; handoff Service desk/normal -> Customer care/normal; docs ['ts-fh210-hydraulic'] not in ['war-summary', 'qa-safety-escalation', 'qa-returns-dtc']
- `inq-0065` ['long_rambling'] handoff Service desk/normal -> Service desk/urgent
- `inq-0073` ['hidden_safety'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/urgent; docs ['ts-fhp90-pressure'] not in ['gen-parts-order', 'gen-contact', 'gen-shipping']
- `inq-0083` [] docs ['war-summary'] not in ['man-fh340', 'ts-fh340-jam', 'ts-fh340-vibration']
- `inq-0084` ['long_rambling'] docs ['ts-fhg7-nostart'] not in ['ts-fhg7-output', 'ts-engine-general', 'man-fhg7']
- `inq-0090` ['hidden_safety'] type machine_trouble -> quality_complaint; handoff Service desk/urgent -> Customer care/normal; docs ['ts-fhp90-pressure'] not in ['war-summary', 'qa-safety-escalation', 'qa-returns-dtc']
- `inq-0101` ['hidden_safety'] type machine_trouble -> unclear_other; handoff Service desk/urgent -> Front desk/urgent; docs ['ts-engine-general'] not in []
- `inq-0113` ['hidden_safety'] type machine_trouble -> quality_complaint; handoff Service desk/urgent -> Customer care/urgent; docs ['man-fh210'] not in ['war-summary', 'qa-safety-escalation', 'qa-returns-dtc']
- `inq-0118` ['very_short'] type machine_trouble -> unclear_other; handoff Service desk/normal -> Front desk/low; docs ['ts-fhg7-output'] not in []
- `inq-0126` [] handoff Customer care/urgent -> Customer care/normal
- `inq-0128` [] docs ['qa-returns-dtc'] not in ['qa-parts-replacement', 'qa-safety-escalation', 'war-summary']
- `inq-0130` ['mixed_intent'] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/normal; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['man-fhg7', 'ts-fhg7-nostart', 'ts-engine-general']
- `inq-0148` [] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['man-fhg7', 'ts-engine-general', 'ts-fhg7-nostart']
- `inq-0156` ['angry'] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc'] not in ['man-fh340', 'ts-fh340-jam', 'ts-fh340-vibration']
- `inq-0157` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'war-summary'] not in ['man-fh520', 'ts-fh520-teeth', 'ts-engine-general']
- `inq-0160` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'qa-parts-replacement'] not in ['man-fh340', 'war-summary', 'ts-fh340-jam']
- `inq-0163` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc'] not in ['man-fh210', 'ts-fh210-hydraulic', 'ts-engine-general']
- `inq-0165` ['typos'] type quality_complaint -> unclear_other; handoff Customer care/normal -> Front desk/low; docs ['qa-returns-dtc', 'qa-parts-replacement'] not in []
- `inq-0171` [] docs ['qa-returns-dtc'] not in ['qa-parts-replacement', 'war-summary', 'qa-safety-escalation']
- `inq-0172` ['typos'] docs ['qa-returns-dtc'] not in ['qa-safety-escalation', 'war-summary', 'qa-defect-report']
- `inq-0177` [] segment dtc -> b2b; handoff Customer care/normal -> Quality team/urgent
- `inq-0178` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'war-summary'] not in ['man-fh340', 'ts-fh340-jam', 'ts-fh340-vibration']
- `inq-0179` [] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['man-fhp90', 'ts-fhp90-pressure', 'ts-engine-general']
- `inq-0181` [] type quality_complaint -> machine_trouble; handoff Customer care/urgent -> Service desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['ts-fhg7-nostart', 'man-fhg7', 'ts-engine-general']
- `inq-0188` [] type quality_complaint -> machine_trouble; handoff Customer care/normal -> Service desk/normal; docs ['qa-returns-dtc', 'war-summary'] not in ['man-fh520', 'ts-fh520-teeth', 'ts-engine-general']
- `inq-0189` ['hidden_safety'] type quality_complaint -> unclear_other; handoff Customer care/urgent -> Front desk/urgent; docs ['qa-safety-escalation', 'qa-returns-dtc'] not in ['gen-shipping', 'gen-contact', 'gen-parts-order']
- `inq-0198` ['no_model'] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['man-fhg7', 'ts-engine-general', 'ts-fhg7-output']
- `inq-0207` [] type unclear_other -> quality_complaint; segment dtc -> b2b; handoff Front desk/low -> Quality team/high; retrieved ['qa-returns-dtc', 'qa-parts-replacement', 'war-summary'] but none needed
- `inq-0209` ['very_short'] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['man-fh520', 'ts-fh520-teeth', 'war-summary']
- `inq-0213` [] segment dtc -> b2b
- `inq-0214` [] type unclear_other -> machine_trouble; segment dtc -> b2b; handoff Front desk/low -> Service desk/high; retrieved ['man-fh520', 'man-fh340', 'man-fh210'] but none needed
- `inq-0215` ['typos'] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-shipping'] not in ['ts-fh340-jam', 'man-fh340', 'man-fh210']
- `inq-0218` [] retrieved ['gen-contact', 'gen-parts-order', 'gen-shipping'] but none needed
- `inq-0220` [] type unclear_other -> quality_complaint; handoff Front desk/low -> Customer care/normal; docs ['gen-parts-order'] not in ['qa-defect-report', 'war-summary', 'qa-safety-escalation']
- `inq-0224` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['man-fh340', 'ts-fh340-vibration', 'ts-fh340-jam']
- `inq-0231` [] segment dtc -> b2b; retrieved ['gen-contact', 'gen-shipping', 'gen-parts-order'] but none needed
- `inq-0234` ['spanish'] docs ['gen-parts-order'] not in []
- `inq-0236` ['typos'] retrieved ['gen-contact', 'gen-shipping', 'gen-parts-order'] but none needed
- `inq-0239` [] segment dtc -> b2b
- `inq-0244` [] retrieved ['gen-shipping', 'gen-contact', 'gen-parts-order'] but none needed
- `inq-0253` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['man-fh210', 'ts-fh210-hydraulic', 'war-summary']
- `inq-0257` [] type unclear_other -> quality_complaint; handoff Front desk/low -> Customer care/normal; retrieved ['qa-defect-report', 'qa-safety-escalation', 'qa-returns-dtc'] but none needed
- `inq-0265` [] type unclear_other -> machine_trouble; segment dtc -> b2b; handoff Front desk/low -> Service desk/high; docs ['gen-parts-order'] not in ['man-fh340', 'ts-fh340-jam', 'ts-fh340-vibration']
- `inq-0278` [] type unclear_other -> machine_trouble; handoff Front desk/low -> Service desk/normal; docs ['gen-parts-order'] not in ['man-fh520', 'war-summary', 'ts-fh520-teeth']
- `inq-0289` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-apply', 'par-overview'] not in ['gen-parts-order', 'gen-contact', 'gen-shipping']
- `inq-0300` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-overview', 'par-apply'] not in ['gen-parts-order', 'gen-shipping', 'gen-contact']
- `inq-0303` ['spanish'] type partner_request -> unclear_other; segment b2b -> dtc; handoff Partner team/normal -> Front desk/low; docs ['par-territory'] not in []
- `inq-0316` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-territory', 'par-overview'] not in []
- `inq-0325` [] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-territory', 'par-overview'] not in []
- `inq-0339` [] type partner_request -> unclear_other; segment b2b -> dtc; handoff Partner team/normal -> Front desk/low; docs ['par-territory', 'par-overview'] not in []
- `inq-0348` ['spanish'] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-tiers'] not in []
- `inq-0360` ['spanish'] type partner_request -> unclear_other; handoff Partner team/normal -> Front desk/low; docs ['par-territory'] not in []
