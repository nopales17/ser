# Semantic observation schema v1.2

The exact strict JSON Schema is generated per stress case and frozen inside
`STRESS_POPULATION.json`. Dynamic `unresolved_targets` properties exist only for
currently legal uninspected integer slots. Each property contains nine fixed
boolean relation slots, permitting more than one public relation without any
model-generated symbol, relation name, duplicate, or illegal target.

The shared vocabulary is frozen in `semantic_vocabulary_v1_2.json`. The schema
contains no model-generated artifact ID, candidate ID, symbol, prose, free-form
uncertainty field, recommendation, or evaluator-only identifier.
