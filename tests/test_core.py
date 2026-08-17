from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError

from ser.core.types import (
    Action,
    ActionResult,
    Budget,
    Observation,
    ResourceDimension,
    ResourceSchema,
    TerminationCause,
    TerminationEvent,
    Trace,
    Transition,
)


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.schema = ResourceSchema(
            (ResourceDimension("calls", "count"), ResourceDimension("time", "step"))
        )

    def test_vector_fills_declared_omissions_with_zero(self):
        self.assertEqual(self.schema.vector({"calls": 2}).as_dict(), {"calls": 2.0, "time": 0.0})

    def test_vector_rejects_unknown_dimensions(self):
        with self.assertRaises(ValueError):
            self.schema.vector({"money": 1})

    def test_vector_rejects_negative_values(self):
        with self.assertRaises(ValueError):
            self.schema.vector({"calls": -1})

    def test_vector_addition_is_componentwise(self):
        total = self.schema.vector({"calls": 1, "time": 3}) + self.schema.vector(
            {"calls": 2, "time": 4}
        )
        self.assertEqual(total.as_dict(), {"calls": 3.0, "time": 7.0})

    def test_vectors_from_different_schemas_cannot_be_added(self):
        other = ResourceSchema((ResourceDimension("calls", "request"),))
        with self.assertRaises(ValueError):
            self.schema.vector() + other.vector()

    def test_partial_budget_constrains_only_named_dimensions(self):
        budget = Budget.create(self.schema, {"calls": 2})
        charged = budget.charge(self.schema.vector({"calls": 2, "time": 100}))
        self.assertEqual(dict(charged.remaining()), {"calls": 0.0})

    def test_budget_rejects_overspend(self):
        budget = Budget.create(self.schema, {"calls": 1})
        with self.assertRaises(ValueError):
            budget.charge(self.schema.vector({"calls": 2}))


class TraceTests(unittest.TestCase):
    def test_trace_append_is_immutable_and_records_stop(self):
        schema = ResourceSchema((ResourceDimension("calls", "count"),))
        observation = Observation("o0", {"value": "x"}, "reset", 0)
        trace = Trace(1, "episode", (observation,))
        stop = TerminationEvent(TerminationCause.CONTROLLER_STOP, 1, "done")
        transition = Transition(
            "t1",
            1,
            "before",
            Action("a1", "stop"),
            ActionResult("r1", "a1", "completed", schema.vector(), termination=stop),
            "after",
            (("calls", 1.0),),
            (("calls", 1.0),),
            "rng",
        )
        updated = trace.append(transition)
        self.assertEqual(trace.transitions, ())
        self.assertEqual(updated.termination, stop)
        with self.assertRaises(ValueError):
            updated.append(transition)

    def test_trace_records_are_frozen(self):
        trace = Trace(1, "episode", ())
        with self.assertRaises(FrozenInstanceError):
            trace.episode_id = "changed"


if __name__ == "__main__":
    unittest.main()
