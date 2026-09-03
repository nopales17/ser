import unittest

from ser.authzgym.generation import (
    build_confirmation_episodes,
    build_development_episodes,
    build_evaluation_episodes,
    build_perturbation_episodes,
)
from ser.authzgym.semantic_contract import VARIANTS, build_stress_cases


class StrongerModelPopulationTests(unittest.TestCase):
    def test_confirmation_reuses_families_with_fresh_identities(self):
        confirmation = build_confirmation_episodes()
        exposed = (
            *build_development_episodes(),
            *build_evaluation_episodes(),
            *build_perturbation_episodes(),
        )
        self.assertEqual(len(confirmation), 8)
        self.assertEqual(
            [item.truth.mechanism_id for item in confirmation],
            ["h1", "h2", "h3", "h4", "h1", "h2", "h3", "h4"],
        )
        self.assertTrue(all(item.split == "confirmation" for item in confirmation))
        self.assertFalse(
            {item.episode_id for item in confirmation}
            & {item.episode_id for item in exposed}
        )

    def test_confirmation_has_all_v12_stress_variants(self):
        cases = build_stress_cases(build_confirmation_episodes())
        self.assertEqual(len(cases), 64)
        by_source = {}
        for case in cases:
            by_source.setdefault(case["source_episode_id"], set()).add(case["variant"])
        self.assertEqual(len(by_source), 8)
        self.assertTrue(all(value == set(VARIANTS) for value in by_source.values()))

    def test_user_ceiling_projection(self):
        maximum_submissions = (4 + 32 + 64) * 3
        projected = (
            maximum_submissions * 4000 * 0.75
            + maximum_submissions * 1024 * 4.5
        ) / 1_000_000
        self.assertEqual(maximum_submissions, 300)
        self.assertAlmostEqual(projected, 2.2824)
        self.assertLess(projected, 2.5)


if __name__ == "__main__":
    unittest.main()
