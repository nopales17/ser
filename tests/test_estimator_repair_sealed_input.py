from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ser.evaluation.authz_v1_3_1_harness import (
    build_component_input,
    load_development_bundle,
)
from ser.evaluation.authz_v1_3_1_sealed_input import (
    ALLOWLISTED_ITEMS,
    ComponentAllowlistError,
    ForbiddenComponentInput,
    SealedComponentInput,
    check_component_module,
)


CONFORMING_FIXTURE = '''
"""A minimal conforming component: sealed input only."""


class FixtureComponent:
    def values(self, sealed):
        support = {
            slot
            for slot, family, _ in sealed.candidate_hypotheses
            if sealed.candidate_effects[slot] == "support"
        }
        order = sealed.contract_constants["relation_slots"]
        index_of = {name: int(name[1:]) for name in order}
        out = {}
        for slot in sealed.legal_target_slots:
            vector = sealed.category_vector(slot)
            out[slot] = 1.0 if any(vector[index_of[name]] for name in support) else 0.0
        return out

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]
'''

FORBIDDEN_FIXTURES = {
    "hidden_roles": "from ser.authzgym.generation import LOGICAL_ROLES\n",
    "discriminating_role": "DISCRIMINATING_ROLE = {}\n",
    "mechanism_ids": "MECHANISMS = ('h1', 'h2')\n",
    "retired_labels": "RETAINED = ('f17', 'f18')\n",
    "restricted_ordinals": (
        "def rank(sealed):\n"
        "    return sealed.canonical_source_ordinal_by_variant_slot\n"
    ),
    "evaluator_metadata": (
        "def rank(case):\n"
        "    return case['usefulness_by_variant_target_slot']\n"
    ),
    "annotation_loader": "from ser.authzgym.v1_3_annotation_builder import *\n",
    "restricted_reader": "from ser.evaluation.authz_v1_3 import action_diagnostic\n",
    "confirmation_identifiers": (
        "PATH = 'CONFIRMATION_PUBLIC_POPULATION.json'\n"
    ),
    "surface_line_count": (
        "def rank(item):\n"
        "    return item.line_count\n"
    ),
    "surface_public_id": (
        "def rank(item):\n"
        "    return item.public_id\n"
    ),
    "surface_path": (
        "def rank(item):\n"
        "    return item.path\n"
    ),
    "surface_symbols": (
        "def rank(item):\n"
        "    return item.exported_symbols\n"
    ),
    "surface_label": (
        "def rank(item):\n"
        "    return item.public_label\n"
    ),
}


class SealedInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()
        cls.case = cls.bundle.canonical_cases()[0]
        cls.case_id = str(cls.case["case_id"])
        cls.sealed = build_component_input(
            cls.case, cls.bundle.response_for(cls.case_id), cls.bundle.contract
        )

    def test_allowlist_surface_is_exactly_the_seven_items(self):
        self.assertIsInstance(self.sealed, SealedComponentInput)
        for item in ALLOWLISTED_ITEMS:
            self.assertTrue(hasattr(self.sealed, item), msg=item)
        self.assertEqual(self.sealed.legal_target_count, 5)
        self.assertEqual(tuple(self.sealed.legal_target_slots), (1, 2, 3, 4, 5))
        self.assertEqual(self.sealed.current_artifact_slot, 0)

    def test_attribute_access_outside_allowlist_raises(self):
        for forbidden in (
            "line_count",
            "public_id",
            "path",
            "exported_symbols",
            "public_label",
            "artifact_id",
            "restricted_case",
            "annotations",
            "case",
        ):
            with self.assertRaises(ForbiddenComponentInput, msg=forbidden):
                getattr(self.sealed, forbidden)

    def test_sealed_input_is_immutable(self):
        with self.assertRaises(ForbiddenComponentInput):
            self.sealed.facts = {}
        with self.assertRaises(TypeError):
            self.sealed.facts["f0"] = True
        with self.assertRaises(TypeError):
            self.sealed.unresolved_targets[1] = (True, False, False, False, False)
        with self.assertRaises(TypeError):
            self.sealed.contract_constants["fact_slots"] = {}

    def test_sealed_input_holds_no_reference_to_restricted_data(self):
        restricted = self.bundle.restricted[self.case_id]
        annotation = self.bundle.annotations[self.case_id]
        transformation_maps = self.bundle.transformation_maps

        def walk(value, seen):
            self.assertNotIn(
                id(value),
                {id(restricted), id(annotation), id(transformation_maps)},
            )
            if id(value) in seen:
                return
            seen.add(id(value))
            if isinstance(value, dict) or type(value).__name__ == "mappingproxy":
                for key, item in value.items():
                    self.assertIsInstance(key, (str, int))
                    walk(item, seen)
            elif isinstance(value, (list, tuple)):
                for item in value:
                    walk(item, seen)
            else:
                self.assertTrue(
                    value is None or isinstance(value, (str, int, float, bool)),
                    msg=type(value).__name__,
                )

        seen: set[int] = set()
        for item in ALLOWLISTED_ITEMS:
            walk(getattr(self.sealed, item), seen)
        # No forbidden surface token appears anywhere in the object's values.
        flat = repr(
            {
                slot: getattr(self.sealed, slot)
                for slot in ("facts", "candidate_effects", "unresolved_targets")
            }
        )
        for token in ("line_count", "public_id", "exported_symbols", "public_label"):
            self.assertNotIn(token, flat)

    def test_static_checker_accepts_conforming_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_component.py"
            path.write_text(CONFORMING_FIXTURE, encoding="utf-8")
            result = check_component_module(path)
            self.assertEqual(result["violations"], [])

    def test_static_checker_rejects_every_forbidden_class(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, source in FORBIDDEN_FIXTURES.items():
                path = Path(directory) / f"fixture_{name}.py"
                path.write_text(source, encoding="utf-8")
                with self.assertRaises(ComponentAllowlistError, msg=name):
                    check_component_module(path)


if __name__ == "__main__":
    unittest.main()
