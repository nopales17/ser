"""Deterministic authoring for tiny, opaque Static Semantic AuthzGym repositories."""

from __future__ import annotations

import hashlib
import random
from dataclasses import replace

from .model import (
    CANDIDATE_HYPOTHESES,
    ArtifactDescriptor,
    ArtifactSpec,
    AuthorizationTruth,
    AuthzEpisode,
    line_count,
)


AUTHZ_AUTHORING_SEED = 271_828_182
LOGICAL_ROLES = ("entry", "guard", "resolver", "policy", "service", "tests")
MECHANISMS = ("h1", "h2", "h3", "h4")
DISCRIMINATING_ROLE = {
    "h1": "service",
    "h2": "resolver",
    "h3": "policy",
    "h4": "guard",
}


def _digest(label: str, length: int = 10) -> str:
    return hashlib.sha256(
        f"authzgym-static-v1|{AUTHZ_AUTHORING_SEED}|{label}".encode("utf-8")
    ).hexdigest()[:length]


def _layout(split: str, layout_index: int) -> dict[str, dict[str, str]]:
    result = {}
    for role in LOGICAL_ROLES:
        token = _digest(f"{split}|layout-{layout_index}|{role}")
        result[role] = {
            "artifact_id": f"a-{token[:8]}",
            "path": f"unit_{token[2:8]}.py",
            "symbol": f"fn_{token[:9]}",
        }
    return result


def _neutral_tail(token: str) -> str:
    return f'''\n\ndef normalize_{token}(value):
    if value is None:
        return "unset"
    return str(value).strip().lower()


def combine_{token}(left, right):
    normalized_left = normalize_{token}(left)
    normalized_right = normalize_{token}(right)
    return (normalized_left, normalized_right)


def stable_{token}(items):
    return tuple(sorted(str(item) for item in items))
'''


def _entry_source(
    symbols: dict[str, str], mechanism: str, zero_variant: int
) -> tuple[str, tuple[str, ...]]:
    guard = symbols["guard"]
    resolver = symbols["resolver"]
    policy = symbols["policy"]
    service = symbols["service"]
    tests = symbols["tests"]
    clue = {
        "h1": f'''    owner_view = {service}(actor, item)
    if request.channel == "alternate":
        return {service}(actor, item)
''',
        "h2": f'''    membership_view = {resolver}(actor, item.group_id, direct_only=True)
''',
        "h3": f'''    role_view = {policy}(actor.role, fallback_role="reader")
''',
        "h4": f'''    context_view = {guard}(actor, item, token_scope=None, feature_context={{}})
''',
    }[mechanism]
    defaults = {
        "h1": f'''    membership_view = {resolver}(actor, item.group_id, include_inherited=True)
    role_view = {policy}(actor.role)
    context_view = {guard}(actor, item, token_scope=request.token.scope, feature_context=request.flags)
''',
        "h2": f'''    owner_view = {service}(actor, item, owner_id=item.owner_id)
    role_view = {policy}(actor.role)
    context_view = {guard}(actor, item, token_scope=request.token.scope, feature_context=request.flags)
''',
        "h3": f'''    owner_view = {service}(actor, item, owner_id=item.owner_id)
    membership_view = {resolver}(actor, item.group_id, include_inherited=True)
    context_view = {guard}(actor, item, token_scope=request.token.scope, feature_context=request.flags)
''',
        "h4": f'''    owner_view = {service}(actor, item, owner_id=item.owner_id)
    membership_view = {resolver}(actor, item.group_id, include_inherited=True)
    role_view = {policy}(actor.role)
''',
    }[mechanism]
    competitor = MECHANISMS[(MECHANISMS.index(mechanism) + 1) % len(MECHANISMS)]
    weak_line = {
        "h1": '    audit_record = ("owner", item.owner_id)\n',
        "h2": '    audit_record = ("membership", item.group_id)\n',
        "h3": '    audit_record = ("role", actor.role)\n',
        "h4": '    audit_record = ("context", request.channel)\n',
    }[competitor]
    weak_fact = {
        "h1": "weak-ownership-audit",
        "h2": "weak-membership-audit",
        "h3": "weak-role-audit",
        "h4": "weak-context-audit",
    }[competitor]
    if zero_variant == 0:
        weak_line = '    audit_record = ("request", request.channel)\n'
    source = f'''def handle_request(actor, item, request):
    test_view = {tests}(actor, item, request)
{clue}{defaults}{weak_line}    decision = (locals().get("owner_view"), locals().get("membership_view"), locals().get("role_view"), locals().get("context_view"))
    return decision if test_view else None
''' + _neutral_tail("entry")
    expected = {
        "h1": ("alternate-entry", "cross-layer-relationship"),
        "h2": ("direct-only-membership", "cross-layer-relationship"),
        "h3": ("role-fallback", "cross-layer-relationship"),
        "h4": (
            "missing-token-scope",
            "missing-feature-context",
            "cross-layer-relationship",
        ),
    }[mechanism]
    if zero_variant:
        expected = expected + (weak_fact,)
    return source, expected


def _guard_source(symbol: str, mechanism: str) -> tuple[str, tuple[str, ...]]:
    if mechanism == "h4":
        body = '''    policy_result = authorize(actor, item, token_scope=None, feature_context={})
    return bool(policy_result)
'''
        facts = ("missing-token-scope", "missing-feature-context", "guard-context-loss")
    else:
        body = '''    policy_result = authorize(actor, item, token_scope=token_scope, feature_context=feature_context)
    return bool(policy_result)
'''
        facts = ("token-scope-forwarded", "feature-context-forwarded")
    return (
        f'''def {symbol}(actor, item, token_scope, feature_context):
{body}'''
        + _neutral_tail("guard"),
        facts,
    )


def _resolver_source(symbol: str, mechanism: str) -> tuple[str, tuple[str, ...]]:
    if mechanism == "h2":
        body = '''    records = membership_store.lookup(actor.id, group_id, direct_only=True)
    return strongest_role(records)
'''
        facts = ("direct-only-membership", "inherited-membership-omitted")
    else:
        body = '''    records = membership_store.lookup(actor.id, group_id, include_inherited=True)
    return strongest_role(records)
'''
        facts = ("inherited-membership-included",)
    return (
        f'''def {symbol}(actor, group_id, **options):
{body}'''
        + _neutral_tail("resolver"),
        facts,
    )


def _policy_source(symbol: str, mechanism: str) -> tuple[str, tuple[str, ...]]:
    if mechanism == "h3":
        body = '''    propagated_role = role_map.get(source_role, fallback_role)
    return propagated_role in {"editor", "manager"}
'''
        facts = ("role-map-transform", "role-fallback")
    else:
        body = '''    propagated_role = source_role
    return propagated_role in {"editor", "manager"}
'''
        facts = ("role-preserved",)
    return (
        f'''def {symbol}(source_role, fallback_role="reader"):
{body}'''
        + _neutral_tail("policy"),
        facts,
    )


def _service_source(symbol: str, mechanism: str) -> tuple[str, tuple[str, ...]]:
    if mechanism == "h1":
        body = '''    return apply_change(actor, item)
'''
        facts = ("sensitive-without-owner-check", "alternate-entry-bypass")
    else:
        body = '''    if actor.owner_id == item.owner_id:
        return apply_change(actor, item)
    return False
'''
        facts = ("ownership-compared",)
    return (
        f'''def {symbol}(actor, item, owner_id=None):
{body}'''
        + _neutral_tail("service"),
        facts,
    )


def _tests_source(symbol: str, mechanism: str) -> tuple[str, tuple[str, ...]]:
    assertion = {
        "h1": "    return alternate_result == standard_result\n",
        "h2": "    return inherited_result == direct_result\n",
        "h3": "    return propagated_role == source_role\n",
        "h4": "    return scoped_result == contextual_result\n",
    }[mechanism]
    source = f'''def {symbol}(actor, item, request):
    alternate_result = request.channel == "alternate"
    standard_result = request.channel == "standard"
    inherited_result = getattr(actor, "inherited_role", None)
    direct_result = getattr(actor, "direct_role", None)
    propagated_role = getattr(actor, "propagated_role", None)
    source_role = getattr(actor, "role", None)
    scoped_result = getattr(request.token, "scope", None)
    contextual_result = getattr(request, "flags", None)
{assertion}''' + _neutral_tail("tests")
    facts = (f"{mechanism}-behavioral-expectation", "test-implementation-relationship")
    return source, facts


def _artifact_sources(
    layout: dict[str, dict[str, str]], mechanism: str, zero_variant: int
) -> dict[str, tuple[str, tuple[str, ...]]]:
    symbols = {role: item["symbol"] for role, item in layout.items()}
    return {
        "entry": _entry_source(symbols, mechanism, zero_variant),
        "guard": _guard_source(symbols["guard"], mechanism),
        "resolver": _resolver_source(symbols["resolver"], mechanism),
        "policy": _policy_source(symbols["policy"], mechanism),
        "service": _service_source(symbols["service"], mechanism),
        "tests": _tests_source(symbols["tests"], mechanism),
    }


def _truth(
    mechanism: str, decision_group: str, control_type: str, layout: dict[str, dict[str, str]]
) -> AuthorizationTruth:
    role = DISCRIMINATING_ROLE[mechanism]
    explanation = {
        "h1": "An alternate entry reaches the sensitive service without preserving the ownership check used by the standard path.",
        "h2": "Membership resolution requests direct records and omits inherited membership used elsewhere.",
        "h3": "A fallback role transformation changes the effective role before the policy decision.",
        "h4": "The guard invokes authorization without forwarding token scope and request feature context.",
    }[mechanism]
    relationships = {
        "h1": ("entry delegates to service", "standard ownership guard is bypassed"),
        "h2": ("entry requests membership", "resolver excludes inherited records"),
        "h3": ("entry supplies source role", "policy transforms role with a fallback"),
        "h4": ("entry receives token/context", "guard drops both before authorization"),
    }[mechanism]
    return AuthorizationTruth(
        mechanism,
        explanation,
        ("entry", role, "tests"),
        (layout[role]["symbol"], "handle_request"),
        relationships,
        role,
        mechanism,
        decision_group,
        control_type,
    )


def _episode(
    split: str,
    layout_index: int,
    mechanism: str,
    *,
    decision_group: str,
    control_type: str,
    zero_variant: int = 0,
) -> AuthzEpisode:
    layout = _layout(split, layout_index)
    authored = _artifact_sources(layout, mechanism, zero_variant)
    discriminator = DISCRIMINATING_ROLE[mechanism]
    usefulness = {
        "entry": 0.40,
        "guard": 0.25,
        "resolver": 0.25,
        "policy": 0.25,
        "service": 0.25,
        "tests": 0.65,
    }
    usefulness[discriminator] = 1.0
    artifacts = []
    for role in LOGICAL_ROLES:
        source, facts = authored[role]
        descriptor = ArtifactDescriptor(
            layout[role]["artifact_id"],
            layout[role]["path"],
            (layout[role]["symbol"],) if role != "entry" else ("handle_request",),
            line_count(source),
        )
        artifacts.append(
            ArtifactSpec(descriptor, source, role, facts, usefulness[role])
        )
    seed = int(_digest(f"{split}|{layout_index}|{mechanism}|{zero_variant}", 16), 16)
    rng = random.Random(seed)
    remaining = [role for role in LOGICAL_ROLES if role != "entry"]
    rng.shuffle(remaining)
    order = ("entry", *remaining)
    artifact_order = tuple(layout[role]["artifact_id"] for role in order)
    episode_id = f"asv1-{split[0]}-{_digest(f'{split}|{layout_index}|{mechanism}|{zero_variant}', 12)}"
    return AuthzEpisode(
        episode_id=episode_id,
        split=split,
        task=(
            "Inspect at most four purchased artifacts and select the candidate "
            "hypothesis that best explains the authorization discrepancy."
        ),
        candidates=CANDIDATE_HYPOTHESES,
        artifacts=tuple(artifacts),
        artifact_order=artifact_order,
        entry_artifact_id=layout["entry"]["artifact_id"],
        max_inspections=4,
        authoring_seed=seed,
        truth=_truth(mechanism, decision_group, control_type, layout),
    )


def build_development_episodes() -> tuple[AuthzEpisode, ...]:
    episodes = []
    for layout_index in range(2):
        group = f"development-eligible-{layout_index}"
        for mechanism in MECHANISMS:
            episodes.append(
                _episode(
                    "development",
                    layout_index,
                    mechanism,
                    decision_group=group,
                    control_type="eligible_branch",
                )
            )
    return tuple(episodes)


def build_evaluation_episodes() -> tuple[AuthzEpisode, ...]:
    episodes = []
    for layout_index in range(10, 14):
        group = f"evaluation-eligible-{layout_index}"
        for mechanism in MECHANISMS:
            episodes.append(
                _episode(
                    "evaluation",
                    layout_index,
                    mechanism,
                    decision_group=group,
                    control_type="eligible_branch",
                )
            )
    for offset, mechanism in enumerate(MECHANISMS):
        layout_index = 20 + offset
        group = f"evaluation-zero-{layout_index}"
        for variant in (0, 1):
            episodes.append(
                _episode(
                    "evaluation",
                    layout_index,
                    mechanism,
                    decision_group=group,
                    control_type="zero_value_control",
                    zero_variant=variant,
                )
            )
    return tuple(episodes)


def permuted_episode(episode: AuthzEpisode) -> AuthzEpisode:
    """Return a semantically equivalent identifier/order perturbation for tests."""

    id_map = {
        item.descriptor.artifact_id: f"p-{_digest(f'permute|{item.descriptor.artifact_id}', 8)}"
        for item in episode.artifacts
    }
    symbol_map = {
        symbol: f"gx_{_digest(f'permute|{symbol}', 9)}"
        for item in episode.artifacts
        for symbol in item.descriptor.exported_symbols
        if symbol != "handle_request"
    }

    def renamed_source(source: str) -> str:
        placeholders = {}
        for index, (old, new) in enumerate(symbol_map.items()):
            placeholder = f"__AUTHZ_SYMBOL_{index}__"
            source = source.replace(old, placeholder)
            placeholders[placeholder] = new
        for placeholder, new in placeholders.items():
            source = source.replace(placeholder, new)
        return source

    artifacts = []
    for item in episode.artifacts:
        exports = tuple(symbol_map.get(symbol, symbol) for symbol in item.descriptor.exported_symbols)
        descriptor = ArtifactDescriptor(
            id_map[item.descriptor.artifact_id],
            f"unit_{_digest(f'permute-path|{item.descriptor.path}', 7)}.py",
            exports,
            item.descriptor.line_count,
        )
        artifacts.append(
            ArtifactSpec(
                descriptor,
                renamed_source(item.source),
                item.logical_role,
                item.expected_fact_keys,
                item.evaluator_usefulness,
            )
        )
    candidate_id_map = {
        candidate.hypothesis_id: f"q{index + 5}"
        for index, candidate in enumerate(reversed(episode.candidates))
    }
    candidates = tuple(
        replace(candidate, hypothesis_id=candidate_id_map[candidate.hypothesis_id])
        for candidate in reversed(episode.candidates)
    )
    remaining = [
        id_map[item]
        for item in reversed(episode.artifact_order)
        if item != episode.entry_artifact_id
    ]
    relevant_functions = tuple(symbol_map.get(item, item) for item in episode.truth.relevant_functions)
    truth = replace(
        episode.truth,
        mechanism_id=f"opaque-{_digest(f'permute-mechanism|{episode.truth.mechanism_id}', 6)}",
        relevant_functions=relevant_functions,
        correct_conclusion=candidate_id_map[episode.truth.correct_conclusion],
        decision_group=f"{episode.truth.decision_group}-permuted",
    )
    return replace(
        episode,
        episode_id=f"{episode.episode_id}-permuted",
        candidates=candidates,
        artifacts=tuple(artifacts),
        artifact_order=(id_map[episode.entry_artifact_id], *remaining),
        entry_artifact_id=id_map[episode.entry_artifact_id],
        truth=truth,
    )


def build_perturbation_episodes() -> tuple[AuthzEpisode, ...]:
    return tuple(
        replace(permuted_episode(item), split="perturbation_audit")
        for item in build_evaluation_episodes()
    )
