# AuthzGym semantic bottleneck v1 implementation notes

The diagnostic tool reads only the prior exposed development population, its 16
stored run records, stored provider-response hashes, the v1.2 public prompt and
vocabulary, and the prior summary/validation. It does not load the stronger-model
confirmation population and does not contain an inference execution command.

Fact answerability is reconstructed from the literal frozen slot definitions and
current visible source without consulting evaluator `expected_fact_keys`.
Unresolved targets are independently regenerated from visible calls and public
exported symbols. Transformation comparisons reuse the existing normalization by
candidate relation and logical target role only after stored inference.

The four-case challenge set and offline taxonomy were content-addressed before
the terminal report. The answerability stop leaves conditions B and C explicitly
null. No network, tunnel, endpoint, credential, or insecure-TLS path was used.
