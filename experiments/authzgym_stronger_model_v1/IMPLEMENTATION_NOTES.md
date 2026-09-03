# AuthzGym stronger-model semantic capability v1 implementation notes

The experiment reused semantic contract v1.2 and the supervised transport envelope without changing semantic content. The sole intervention was `patchersniper_praneeth/gpt-5.4-mini`.

The configured endpoint was accessed through the existing local SSH/SOCKS hop with the user-approved endpoint-scoped insecure TLS flag. The API credential remained in an anonymous local curl configuration pipe and was stripped from the SSH child environment. No live software target or remote workspace was used.

The terminal classification was `semantic_capability_below_threshold` after 24 logical calls and 24 provider attempts, with $0.066072750 accounted usage.

All population, prompt, schema, configuration, implementation, raw-response, transport-attempt, run, and summary identities are content-addressed. No manual response repair or post-result tuning occurred.
