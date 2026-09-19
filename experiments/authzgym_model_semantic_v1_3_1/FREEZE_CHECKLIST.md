# Freeze checklist -- `model-semantic-v1.3.1-N1`

Handoff step 6C / preregistration section 18, rebuilt over the complete
Step-6A dormant implementation. Every item is recorded with its status,
evidence and authority. `not_satisfied` items are blocking for development
inference.

- Condition: `model-semantic-v1.3.1-N1`
- Authority: ADR-0023
- Repository commit: `9beded780b5d3c83b7c60f9f70c3860953164dba`
- Date: 2026-09-19
- Reviewer: senior_reasoning_agent (review required by Sol/Astra before any development call; signature pending_separate_step_7_authorization)
- Freeze complete: `true`
- Model or provider calls made: 0

| # | Item | Status | Evidence |
| --- | --- | --- | --- |
| 1 | step 1 integrity baseline and hash restatement | `pass` | {"accepted_governance_transitions_matched": ["MAP.md", "plan/ROADMAP.md", "state/CONTEXT_PACKET.md", "state/STATUS.yaml"], "baseline_clean_except_condition_directory": true, "clean_except_condition_directory": true, "governance_rebaseline": {"accepted_paths": ["MAP.md", "plan/ROADMAP.md", "state/CONTEXT_PACKET.md", "state/STATUS.yaml"], "accepted_transition_count": 4, "additional_transitions_ac... |
| 2 | step 2 model-condition verification (zero inference) | `pass` | {"catalog_snapshot_file_sha256": "f3ca49bf1d16c3c9891bbdbe7c69ec8146bcfc6ab29474f72002207b143960e6", "chat_completions_submissions": 0, "immutable_revision": "unavailable_without_inference", "paid_inference": false, "route_model_entry_count": 1, "route_model_identifier": "patchersniper_praneeth/gpt-5.4-nano"} |
| 3 | step 2 cost gate under section 9.5 | `pass` | {"hard_spend_ceiling_usd": 2.5, "max_submissions": 336, "projected_worst_case_usd": 0.69888, "verified_pricing": {"cached_input": 0.02, "input": 0.2, "output": 1.25}} |
| 4 | step 3 audited reader and access ledger | `pass` | {"ledger": {"ledger_file_sha256": "7d5bbfe1dfbde8c93ef44867383e7f61af96d59210d477c7a58b56dc1db80ee3", "ledger_path": "experiments/authzgym_model_semantic_v1_3_1/ACCESS_LEDGER.jsonl", "malformed_record_indices": [], "missing_tool_sha256_indices": [], "never_open_open_count": 0, "never_open_open_paths": [], "passes": true, "record_count": 2514, "retrospective_disclosure_count": 1, "retrospective_... |
| 5 | step 4 client and retry state machine | `pass` | {"client_and_retry_tests": {"errors": 0, "failures": 0, "modules": ["tests.test_model_semantic_v1_3_1_client", "tests.test_model_semantic_v1_3_1_retry"], "status": "pass", "tests_run": 20}} |
| 6 | step 5 gold adequacy (S-3) on development | `pass` | {"canonical_gold_aggregate": {"case_count": 8, "discriminating_case_count": 8, "illegal_target_count": 0, "mean_normalized_regret": 0.11666666666666665, "nondiscriminating_case_count": 0, "top1": 0.75, "top2": 1.0}, "degenerate_gold_choice_set_sources": [], "gold_adequacy_file_sha256": "371bc7815d8b2e8f8274f62da75d0a85d01264671055bc09ebd8d572823e4ff8", "recorded_figure_reproduction": {"authorit... |
| 7 | section 18 inherited-input and artifact references present by hash | `pass` | {"missing": [], "referenced_file_count": 53} |
| 8 | section 18 condition runner present and hashed | `pass` | {"executed": false, "runner_file_sha256": "6f629316b24095f11d2d16098bba6403808a83a376194f23473cecd96f97600e"} |
| 9 | section 12.1 structural guarantee that S-7 cannot gate | `pass` | {"authority": "PREREGISTRATION.md section 12.1", "gates_tests": {"errors": 0, "failures": 0, "modules": ["tests.test_model_semantic_v1_3_1_gates"], "status": "pass", "tests_run": 25}, "machine_probe": {"diagnostic_only_verdict_access_raises": true, "gated_development_items_excludes_s7": true, "passes": true, "synthetic_probe_outcome": {"base_label": "development_eligible", "s7_violation_count":... |
| 10 | section 18 complete condition implementation and tests, hashed | `pass` | {"implementation_file_sha256": {"src/ser/authzgym/semantic_contract_v1_3.py": "b76b31e9b0f56c08223236699753bf2351aa13548559f7b3aaa0657962db8fa6", "src/ser/authzgym/supervised_transport_v1_3.py": "714d2841aabf31498371bed897a0bb3bc2bad20a51a0134ec5fe053ff3b0caf4", "src/ser/evaluation/authz_model_semantic_v1_3_1.py": "74ce8f75fce643b713544945d79076c9bc73060f3c736f3ed660faeef061f8f2", "tests/test_m... |
| 11 | no model or provider call made at any point | `pass` | {"catalog_probe_is_not_paid_inference": true, "chat_completions_submissions": 0, "paid_inference": false} |
| 12 | step 13 confirmation runner absent (not required pre-inference) | `pass` | {"deferred_by_design": ["tools/run_authzgym_model_semantic_confirmation.py"]} |
| 13 | governance items recorded for Sol/Astra acknowledgement | `acknowledged` | {"DEV-1": "handoff step-1 item 3 names a section-0.2 never-open path as the `0e20284b...` restatement source; resolved fail-closed (stat-ed, never opened) and restated from authorized readable records", "DEV-2": {"classification": "procedural_deviation_not_retroactively_authorized", "content_parsed_or_used": false, "convention_violation": "raw-file SHA-256 over a file named `*CONFIRMATION*`, of... |

## Outstanding blocking items

## Next authorization

a separate Step-7 inference authorization, after the frozen manifest and checklist pass in full

## Governance items recorded for acknowledgement

- `DEV-1` -- status `acknowledged`
  - Resolution applied: fail closed: the v1_3_1 freeze record was stat-ed for existence and never opened; `0e20284b...` is restated from the authorized readable records that carry it

- `DEV-2` -- status `acknowledged`
  - Resolution applied: preserved as a recorded procedural deviation; not retroactively authorized, not treated as a satisfied re-derivation, and the condition's harness refuses the path; the single `retrospective_disclosure` ledger record required by IMPLEMENTATION_CLARIFICATION.md section 4.2 is appended at step 6B with `occurred_before_audited_reader: true` and no fabricated original timestamp
