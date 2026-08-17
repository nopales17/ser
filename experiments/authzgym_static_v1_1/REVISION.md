# Calibration revision 1.1

Protocol 1.1 exists solely because the preserved v1 mock calibration revealed
that deterministic omissions depended on opaque artifact IDs. The corrected
mock condition hashes semantic fact/relation roles instead. This makes the test
double's intended semantic quality stable under identifier and symbol renaming.

No real-model call or outcome preceded this correction. See
`../authzgym_static_v1/FIRST_RUN_FAILURE.json` and
`../authzgym_static_v1/IMPLEMENTATION_NOTES.md` for the complete preserved v1
history. Protocol 1.1 remains construction calibration, not evidence.
