# Terminology

Prefer stable concept IDs over near-synonyms. The canonical identity and status
of each concept live in `theory/IDEA_MAP.yaml`.

| Term | Preferred meaning | Important boundary |
| --- | --- | --- |
| SER | provisional name for the research project and a possible controller that selects, targets, times, and stops resource-consuming epistemic actions (`M-012`) | expansion and name are unresolved (`Q-008`); MicroGym policies are experimental instruments, not a production or validated SER runtime |
| SERT | provisional name for a possible learned routing policy or training regime (`H-014`) | late-stage seed, not implemented |
| WorldState | environment-owned latent facts and dynamics (`C-001`) | never directly visible to a normal policy |
| Observation | provenance-bearing information legitimately released to a controller (`C-002`) | not assumed true, textual, current, or equivalent to a hypothesis |
| epistemic resource | a named quantity with a declared unit in a raw cost vector (`P-005`, `C-007`) | broader than LLM tokens; no universal scalar conversion |
| epistemic action | a domain-typed controller choice that may acquire information, transform state, intervene, or stop (`P-004`, `C-005`) | descriptive categories are not a universal enum |
| epistemic state | controller-entitled decision state (`P-001`, `C-003`) | may be history or structured state; never latent or evaluator-only truth |
| epistemic unit | rejected universal semantic supertype (`P-002`, `C-022`) | retained for provenance; a future common infrastructure envelope remains possible |
| scope | optional domain-typed applicability metadata (`P-003`, `C-020`) | no universal algebra; distinct from gating, action legality, or a code class |
| Signal | reserved but deferred candidate role (`P-009`, `C-021`) | no semantics beyond Observation, ActionResult, state, relations, or reliability metadata have been justified |
| ActionResult | execution/failure/cost record returned from an action (`C-006`) | not the evaluator's task judgment |
| Outcome | evaluator-produced terminal or trajectory judgment (`C-016`) | may use restricted truth but is not policy-visible during a normal episode |
| STOP | first-class controller action with submission or abstention (`C-011`) | distinct from environment termination and runner/evaluator truncation |
| evidence | observation from a specified protocol with provenance, scope, and limitations | not interchangeable with a hypothesis |
| experimentally supported | maturity backed by scoped experimental evidence | not universal truth and not necessarily an accepted invariant |
| cold | slow-changing authoritative conceptual storage | does not imply the content is mature |
| warm | plan and roadmap cursor | does not own scientific truth |
| hot-ish | current implementation/evidence state or a generated projection | generated views do not become sources of truth |
| MicroGym | implemented zero-LLM synthetic control-validation environment family (`M-011`) | scoped benchmark instrument, not the practical research trunk or evidence of semantic/general intelligence |
| Value of Adaptivity (VOA) | routing-v1's exact open-loop expected loss minus exact closed-loop expected loss | experiment-specific evaluator quantity, not a universal SER objective |
| Adaptivity Capture | routing-v1's fraction of positive oracle VOA recovered by the candidate relative to exact open- and closed-loop loss | undefined at zero VOA and incomparable across unrelated objectives without justification |
| oscillation rate | frequency of switching between external acquisition and internal inference (`H-007`) | measured trajectory property, not a constant |
| oscillation depth | resource spent within a mode before switching (`H-007`) | measured trajectory property, not a constant |
| active observation | choose an intervention/input, then observe its result (`H-009`) | distinct from passive world-to-observation flow |
| promotion | explicit maturity change with reason and evidence/ADR as required | conversation or implementation alone never promotes |
| PROMOTE | preserved candidate runtime coupling operator (`M-009`) | unrelated to documentation maturity promotion |
