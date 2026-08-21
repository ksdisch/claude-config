import inspect
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from validate_graph import (  # noqa: E402
    check_root,
    covered_by,
    main as validate_main,
    matches_glob,
    source_files,
    strongly_connected,
    validate,
)


class GraphCase(unittest.TestCase):
    """Each test builds a throwaway tree so the file:line checks run against
    files that really exist — the point of the validator is that it opens them."""

    def setUp(self):
        # Resolved because macOS hands out /var/... which is a symlink to
        # /private/var/... — the validator resolves, so the fixture must too or
        # every path comparison is off by that prefix.
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def write(self, rel, lines=5):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(f"line {n}\n" for n in range(1, lines + 1)))
        return path

    def module(self, module_id, parent=None, **extra):
        module = {
            "id": module_id,
            "name": module_id.rsplit("/", 1)[-1],
            "parent": parent,
            "path": module_id,
            "summary": f"what {module_id} is for.",
        }
        module.update(extra)
        return module

    def edge(self, source, target, evidence_file, line=1, **extra):
        edge = {
            "from": source,
            "to": target,
            "evidence": [{"file": evidence_file, "line": line}],
        }
        edge.update(extra)
        return edge

    def doc(self, modules, edges, roots=("src",), excluded=()):
        return {
            "schema": "arch-graph/v1",
            "repo": {"name": "demo", "root": str(self.root), "commit": "abc1234"},
            "roots": list(roots),
            "excluded": list(excluded),
            "modules": modules,
            "edges": edges,
        }

    def run_validate(self, doc, min_coverage=0.9):
        return validate(doc, self.root, min_coverage)

    def two_module_repo(self):
        self.write("src/game/main.ts")
        self.write("src/shared/protocol.ts")
        modules = [self.module("src/game"), self.module("src/shared")]
        edges = [self.edge("src/game", "src/shared", "src/game/main.ts", 3)]
        return modules, edges


class TestValidDocumentPasses(GraphCase):
    def test_minimal_valid_graph_is_clean(self):
        modules, edges = self.two_module_repo()
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["modules"], 2)
        self.assertEqual(summary["edges"], 1)
        self.assertEqual(summary["coverage"], 1.0)

    def test_empty_edge_list_is_allowed(self):
        """A repo of independent modules is a finding, not a malformed graph."""
        self.write("src/a/one.ts")
        self.write("src/b/two.ts")
        problems, summary = self.run_validate(
            self.doc([self.module("src/a"), self.module("src/b")], [])
        )
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["edges"], 0)
        self.assertEqual(len(summary["orphan_modules"]), 2)

    def test_a_parent_whose_submodules_carry_the_edges_is_not_an_orphan(self):
        """A parent module never has its own edges — its submodules do. Judging
        it on its own id alone reported every parent in the graph as isolated."""
        self.write("src/game/net/socket.ts")
        self.write("src/shared/protocol.ts")
        modules = [
            self.module("src/game"),
            self.module("src/game/net", parent="src/game"),
            self.module("src/shared"),
        ]
        edges = [self.edge("src/game/net", "src/shared", "src/game/net/socket.ts", 1)]
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(summary["orphan_modules"], [])
        self.assertEqual(problems.warnings, [])

    def test_a_parent_with_no_subtree_edges_at_all_is_still_an_orphan(self):
        self.write("src/tools/thing.ts")
        self.write("src/tools/inner/other.ts")
        self.write("src/shared/protocol.ts")
        modules = [
            self.module("src/tools"),
            self.module("src/tools/inner", parent="src/tools"),
            self.module("src/shared"),
        ]
        _, summary = self.run_validate(self.doc(modules, []))
        self.assertEqual(
            summary["orphan_modules"], ["src/shared", "src/tools", "src/tools/inner"]
        )

    def test_submodule_nesting_and_rollup(self):
        self.write("src/game/net/socket.ts")
        self.write("src/shared/protocol.ts")
        modules = [
            self.module("src/game"),
            self.module("src/game/net", parent="src/game"),
            self.module("src/shared"),
        ]
        edges = [self.edge("src/game/net", "src/shared", "src/game/net/socket.ts", 2)]
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["top_level_modules"], 2)


class TestHallucinatedCitations(GraphCase):
    """The failure this validator primarily exists to catch."""

    def test_evidence_file_that_does_not_exist_fails(self):
        modules, _ = self.two_module_repo()
        edges = [self.edge("src/game", "src/shared", "src/game/imaginary.ts", 3)]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(
            any("does not exist" in e and "imaginary.ts" in e for e in problems.errors),
            problems.errors,
        )

    def test_line_past_end_of_file_fails(self):
        modules, _ = self.two_module_repo()
        edges = [self.edge("src/game", "src/shared", "src/game/main.ts", 999)]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(
            any("has 5 lines" in e for e in problems.errors), problems.errors
        )

    def test_final_line_without_trailing_newline_counts(self):
        (self.root / "src/game").mkdir(parents=True, exist_ok=True)
        (self.root / "src/game/main.ts").write_text("a\nb\nc")  # 3 lines, no final \n
        self.write("src/shared/protocol.ts")
        modules = [self.module("src/game"), self.module("src/shared")]
        problems, _ = self.run_validate(
            self.doc(modules, [self.edge("src/game", "src/shared", "src/game/main.ts", 3)])
        )
        self.assertEqual(problems.errors, [])

    def test_line_one_of_an_empty_file_fails(self):
        (self.root / "src/game").mkdir(parents=True, exist_ok=True)
        (self.root / "src/game/main.ts").write_text("")
        self.write("src/shared/protocol.ts")
        modules = [self.module("src/game"), self.module("src/shared")]
        problems, _ = self.run_validate(
            self.doc(modules, [self.edge("src/game", "src/shared", "src/game/main.ts", 1)])
        )
        self.assertTrue(any("has 0 lines" in e for e in problems.errors), problems.errors)

    def test_anchor_locations_are_checked_too(self):
        modules, edges = self.two_module_repo()
        modules[0]["anchors"] = [{"file": "src/game/nope.ts", "line": 1, "label": "entry"}]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("nope.ts" in e for e in problems.errors), problems.errors)

    def test_edge_with_no_evidence_fails(self):
        modules, _ = self.two_module_repo()
        edges = [{"from": "src/game", "to": "src/shared", "evidence": []}]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(
            any("at least one `evidence`" in e for e in problems.errors), problems.errors
        )


class TestStructuralIntegrity(GraphCase):
    def test_wrong_schema_version_refuses_immediately(self):
        doc = self.doc(*self.two_module_repo())
        doc["schema"] = "arch-graph/v2"
        problems, summary = self.run_validate(doc)
        self.assertFalse(summary["schema_ok"])
        self.assertTrue(any("refusing to guess" in e for e in problems.errors))

    def test_duplicate_module_id_fails(self):
        self.write("src/game/main.ts")
        modules = [self.module("src/game"), self.module("src/game")]
        problems, _ = self.run_validate(self.doc(modules, []))
        self.assertTrue(any("duplicate module id" in e for e in problems.errors))

    def test_absolute_or_dotted_ids_fail(self):
        self.write("src/game/main.ts")
        for bad in ("/src/game", "src/../game", "src/game/", "src\\game"):
            with self.subTest(bad=bad):
                problems, _ = self.run_validate(self.doc([self.module(bad)], []))
                self.assertTrue(problems.errors, f"{bad} should be rejected")

    def test_module_path_missing_on_disk_fails(self):
        modules, edges = self.two_module_repo()
        modules.append(self.module("src/ghost"))
        problems, _ = self.run_validate(self.doc(modules, edges), min_coverage=0.0)
        self.assertTrue(
            any("does not exist on disk" in e and "src/ghost" in e for e in problems.errors)
        )

    def test_path_must_equal_id_in_v1(self):
        modules, edges = self.two_module_repo()
        modules[0]["path"] = "src"
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("must equal `id`" in e for e in problems.errors))

    def test_missing_summary_fails(self):
        modules, edges = self.two_module_repo()
        modules[0]["summary"] = "  "
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("`summary`" in e for e in problems.errors))

    def test_unresolved_parent_fails(self):
        modules, edges = self.two_module_repo()
        modules[0]["parent"] = "src/nonexistent"
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("is not a module" in e for e in problems.errors))

    def test_parent_cycle_is_reported_not_hung(self):
        self.write("src/a/one.ts")
        self.write("src/b/two.ts")
        modules = [self.module("src/a", parent="src/b"), self.module("src/b", parent="src/a")]
        problems, _ = self.run_validate(self.doc(modules, []))
        self.assertTrue(any("cyclic" in e for e in problems.errors), problems.errors)

    def test_three_level_nesting_exceeds_v1_depth(self):
        self.write("src/a/b/c/deep.ts")
        modules = [
            self.module("src/a"),
            self.module("src/a/b", parent="src/a"),
            self.module("src/a/b/c", parent="src/a/b"),
        ]
        problems, _ = self.run_validate(self.doc(modules, []))
        self.assertTrue(any("v1 maps at most" in e for e in problems.errors), problems.errors)

    def test_self_edge_fails(self):
        modules, _ = self.two_module_repo()
        edges = [self.edge("src/game", "src/game", "src/game/main.ts", 1)]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("cannot depend on itself" in e for e in problems.errors))

    def test_parent_to_child_edge_is_containment_not_dependency(self):
        self.write("src/game/net/socket.ts")
        modules = [self.module("src/game"), self.module("src/game/net", parent="src/game")]
        edges = [self.edge("src/game", "src/game/net", "src/game/net/socket.ts", 1)]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("nested in each other" in e for e in problems.errors), problems.errors)

    def test_duplicate_edge_of_same_kind_fails(self):
        modules, _ = self.two_module_repo()
        edges = [
            self.edge("src/game", "src/shared", "src/game/main.ts", 1),
            self.edge("src/game", "src/shared", "src/game/main.ts", 2),
        ]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("duplicate" in e for e in problems.errors), problems.errors)

    def test_same_pair_with_different_kinds_is_allowed(self):
        modules, _ = self.two_module_repo()
        edges = [
            self.edge("src/game", "src/shared", "src/game/main.ts", 1, kind="import"),
            self.edge("src/game", "src/shared", "src/game/main.ts", 2, kind="type-only"),
        ]
        problems, _ = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])

    def test_unknown_edge_kind_warns_but_passes(self):
        modules, _ = self.two_module_repo()
        edges = [self.edge("src/game", "src/shared", "src/game/main.ts", 1, kind="grpc")]
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["unknown_edge_kinds"], ["grpc"])
        self.assertTrue(any("grpc" in w for w in problems.warnings))


class TestCoverage(GraphCase):
    def test_unmapped_directory_fails_the_floor(self):
        modules, edges = self.two_module_repo()
        for n in range(6):
            self.write(f"src/forgotten/file{n}.ts")
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertTrue(any("coverage is" in e for e in problems.errors), problems.errors)
        self.assertTrue(any("src/forgotten/file0.ts" in e for e in problems.errors))
        self.assertLess(summary["coverage"], 0.9)

    def test_excluded_globs_do_not_count_against_coverage(self):
        modules, edges = self.two_module_repo()
        for n in range(6):
            self.write(f"src/game/thing{n}.test.ts")
        doc = self.doc(modules, edges, excluded=["**/*.test.ts"])
        problems, summary = self.run_validate(doc)
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["coverage"], 1.0)

    def test_build_output_is_never_scanned(self):
        modules, edges = self.two_module_repo()
        for n in range(20):
            self.write(f"src/node_modules/pkg/index{n}.js")
        self.write("src/dist/bundle.js")
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["scanned_files"], 2)

    def test_slightly_uncovered_warns_instead_of_failing(self):
        modules, edges = self.two_module_repo()
        for n in range(30):
            self.write(f"src/game/f{n}.ts")
        self.write("src/stray.ts")
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertTrue(any("belong to no module" in w for w in problems.warnings))
        self.assertEqual(summary["uncovered_files"], ["src/stray.ts"])

    def test_a_root_that_does_not_exist_is_an_error_not_a_silent_pass(self):
        """The whole coverage gate used to switch itself off on a typo: a missing
        root scans nothing, and nothing divided out to a clean 100%."""
        modules, edges = self.two_module_repo()
        doc = self.doc(modules, edges, roots=["srcc"])
        problems, summary = self.run_validate(doc)
        self.assertTrue(any("does not exist under" in e for e in problems.errors), problems.errors)
        self.assertEqual(summary["scanned_files"], 0)
        self.assertEqual(summary["coverage"], 0.0)

    def test_scanning_zero_files_is_an_error_even_with_a_real_root(self):
        (self.root / "src").mkdir(parents=True, exist_ok=True)
        self.write("lib/a.ts")
        modules = [self.module("lib")]
        problems, _ = self.run_validate(self.doc(modules, [], roots=["src"]))
        self.assertTrue(
            any("coverage of nothing is not coverage" in e for e in problems.errors),
            problems.errors,
        )

    def test_everything_excluded_is_also_zero_scanned_and_an_error(self):
        modules, edges = self.two_module_repo()
        doc = self.doc(modules, edges, excluded=["**"])
        problems, _ = self.run_validate(doc)
        self.assertTrue(any("no source files were scanned" in e for e in problems.errors))

    def test_dot_means_the_whole_repo_is_source(self):
        """`"."` is the only way to say it, and a flat repo has no substitute:
        without it the author must enumerate top-level files, and every file
        added later falls silently outside the coverage denominator."""
        self.write("main.ts")
        self.write("helper.ts")
        modules = [self.module("main.ts"), self.module("helper.ts")]
        problems, summary = self.run_validate(self.doc(modules, [], roots=["."]))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["scanned_files"], 2)
        self.assertEqual(summary["coverage"], 1.0)

    def test_equivalent_root_spellings_all_work(self):
        modules, edges = self.two_module_repo()
        for spelling in ("src", "src/", "./src", "src//"):
            with self.subTest(root=spelling):
                problems, summary = self.run_validate(
                    self.doc(modules, edges, roots=[spelling])
                )
                self.assertEqual(problems.errors, [], spelling)
                self.assertEqual(summary["scanned_files"], 2)

    def test_check_root_normalises_rather_than_rejecting(self):
        for spelling, expected in [
            ("src", "src"),
            ("src/", "src"),
            ("./src", "src"),
            (".", "."),
            ("./", "."),
            ("src//lib", "src/lib"),
        ]:
            with self.subTest(root=spelling):
                normalized, reason = check_root(spelling)
                self.assertIsNone(reason, spelling)
                self.assertEqual(normalized, expected)

    def test_check_root_still_refuses_to_leave_the_repo(self):
        for bad in ("/etc", "../x", "src/../..", "src\\game", "", "   ", None, 3):
            with self.subTest(root=bad):
                normalized, reason = check_root(bad)
                self.assertIsNone(normalized, bad)
                self.assertIsNotNone(reason, bad)

    def test_absolute_and_dotdot_roots_are_rejected_before_they_can_crash(self):
        """`root / '/etc'` lets the absolute component win outright, and the walk
        then raised an uncaught ValueError out of `relative_to`."""
        modules, edges = self.two_module_repo()
        for bad in ("/etc", "../", "src/../..", "src\\game"):
            with self.subTest(root=bad):
                problems, _ = self.run_validate(self.doc(modules, edges, roots=[bad]))
                self.assertTrue(
                    any("`roots` entry" in e for e in problems.errors),
                    f"{bad} should be rejected: {problems.errors}",
                )

    def test_a_valid_root_alongside_a_bad_one_still_reports_the_bad_one(self):
        modules, edges = self.two_module_repo()
        problems, _ = self.run_validate(self.doc(modules, edges, roots=["src", "/etc"]))
        self.assertTrue(any("/etc" in e for e in problems.errors), problems.errors)

    def test_dot_directories_are_skipped(self):
        found = []
        self.write("src/game/main.ts")
        (self.root / "src/.cache").mkdir(parents=True, exist_ok=True)
        (self.root / "src/.cache/junk.ts").write_text("x\n")
        found = source_files(self.root, ["src"], [])
        self.assertEqual(found, ["src/game/main.ts"])

    def test_root_that_is_a_single_file(self):
        self.write("build.ts")
        self.assertEqual(source_files(self.root, ["build.ts"], []), ["build.ts"])

    def test_missing_root_is_skipped_not_crashed(self):
        self.write("src/a.ts")
        self.assertEqual(source_files(self.root, ["src", "nope"], []), ["src/a.ts"])


class TestCycleReporting(GraphCase):
    def test_cycle_is_reported_but_does_not_fail(self):
        self.write("src/a/one.ts")
        self.write("src/b/two.ts")
        modules = [self.module("src/a"), self.module("src/b")]
        edges = [
            self.edge("src/a", "src/b", "src/a/one.ts", 1),
            self.edge("src/b", "src/a", "src/b/two.ts", 1),
        ]
        problems, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(problems.errors, [])
        self.assertEqual(summary["cycles"], [["src/a", "src/b"]])
        self.assertEqual(summary["top_level_cycles"], [["src/a", "src/b"]])

    def test_submodule_cycle_rolls_up_to_its_parents(self):
        self.write("src/a/net/one.ts")
        self.write("src/b/core/two.ts")
        modules = [
            self.module("src/a"),
            self.module("src/a/net", parent="src/a"),
            self.module("src/b"),
            self.module("src/b/core", parent="src/b"),
        ]
        edges = [
            self.edge("src/a/net", "src/b/core", "src/a/net/one.ts", 1),
            self.edge("src/b/core", "src/a/net", "src/b/core/two.ts", 1),
        ]
        _, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(summary["top_level_cycles"], [["src/a", "src/b"]])

    def test_acyclic_graph_reports_no_cycles(self):
        modules, edges = self.two_module_repo()
        _, summary = self.run_validate(self.doc(modules, edges))
        self.assertEqual(summary["cycles"], [])


class TestPureHelpers(unittest.TestCase):
    def test_strongly_connected_finds_only_multi_node_components(self):
        nodes = ["a", "b", "c", "d"]
        edges = [("a", "b"), ("b", "a"), ("c", "d")]
        self.assertEqual(strongly_connected(nodes, edges), [["a", "b"]])

    def test_strongly_connected_handles_a_deep_chain_without_recursion_limit(self):
        nodes = [f"n{i}" for i in range(5000)]
        edges = [(f"n{i}", f"n{i + 1}") for i in range(4999)]
        edges.append(("n4999", "n0"))
        components = strongly_connected(nodes, edges)
        self.assertEqual(len(components), 1)
        self.assertEqual(len(components[0]), 5000)

    def test_strongly_connected_ignores_edges_to_unknown_nodes(self):
        self.assertEqual(strongly_connected(["a"], [("a", "ghost")]), [])

    def test_covered_by_requires_a_path_boundary(self):
        self.assertTrue(covered_by("src/game/main.ts", ["src/game"]))
        self.assertTrue(covered_by("src/game", ["src/game"]))
        self.assertFalse(covered_by("src/gameplay/main.ts", ["src/game"]))

    def test_matches_glob_handles_recursive_patterns(self):
        self.assertTrue(matches_glob("src/a/b.test.ts", "**/*.test.ts"))
        self.assertTrue(matches_glob("b.test.ts", "**/*.test.ts"))
        self.assertFalse(matches_glob("src/a/b.ts", "**/*.test.ts"))
        self.assertTrue(matches_glob("src/generated/api.ts", "src/generated/*"))

    def test_a_star_never_crosses_a_path_separator(self):
        """The bug this replaced: `fnmatch`'s `*` crosses `/`, so these matched on
        one interpreter and not another — and `excluded` feeds the coverage
        denominator, so the same graph's coverage depended on where it ran."""
        self.assertFalse(matches_glob("src/generated/deep/api.ts", "src/generated/*"))
        self.assertFalse(matches_glob("a/b.md", "*.md"))
        self.assertTrue(matches_glob("b.md", "*.md"))
        self.assertTrue(matches_glob("src/generated/deep/api.ts", "src/generated/**"))

    def test_double_star_matches_zero_or_more_segments(self):
        self.assertTrue(matches_glob("a.ts", "**/a.ts"))
        self.assertTrue(matches_glob("x/a.ts", "**/a.ts"))
        self.assertTrue(matches_glob("x/y/z/a.ts", "**/a.ts"))
        self.assertTrue(matches_glob("src/x/y/tests/a.ts", "src/**/tests/*.ts"))
        self.assertFalse(matches_glob("src/x/y/tests/deep/a.ts", "src/**/tests/*.ts"))

    def test_question_mark_matches_one_character_within_a_segment(self):
        self.assertTrue(matches_glob("src/a.ts", "src/?.ts"))
        self.assertFalse(matches_glob("src/ab.ts", "src/?.ts"))

    def test_matches_glob_is_not_exponential_on_many_double_stars(self):
        """A memo-free recursive matcher hangs here rather than answering."""
        rel = "/".join(["a"] * 40) + "/b.ts"
        pattern = "/".join(["**"] * 20) + "/nope.ts"
        self.assertFalse(matches_glob(rel, pattern))

    def test_matches_glob_does_not_depend_on_pathlib_full_match(self):
        """One implementation, one behaviour: nothing here defers to a method
        whose presence varies by interpreter version."""
        import validate_graph

        source = inspect.getsource(validate_graph.matches_glob)
        self.assertNotIn("full_match", source.split('"""')[-1])


class TestCommandLine(GraphCase):
    def test_clean_run_exits_zero_and_writes_summary(self):
        modules, edges = self.two_module_repo()
        graph = self.root / "architecture.json"
        graph.write_text(json.dumps(self.doc(modules, edges)))
        out = self.root / "summary.json"
        self.assertEqual(validate_main([str(graph), "-o", str(out)]), 0)
        summary = json.loads(out.read_text())
        self.assertEqual(summary["modules"], 2)
        self.assertEqual(summary["repo_root"], str(self.root))

    def test_broken_graph_exits_one(self):
        modules, _ = self.two_module_repo()
        graph = self.root / "architecture.json"
        edges = [self.edge("src/game", "src/shared", "src/game/gone.ts", 1)]
        graph.write_text(json.dumps(self.doc(modules, edges)))
        self.assertEqual(validate_main([str(graph)]), 1)

    def test_malformed_json_exits_one(self):
        graph = self.root / "architecture.json"
        graph.write_text("{not json")
        self.assertEqual(validate_main([str(graph)]), 1)

    def test_summary_path_gets_its_parent_directory_created(self):
        modules, edges = self.two_module_repo()
        graph = self.root / "architecture.json"
        graph.write_text(json.dumps(self.doc(modules, edges)))
        out = self.root / "docs" / "architecture" / "summary.json"
        self.assertEqual(validate_main([str(graph), "-o", str(out)]), 0)
        self.assertTrue(out.is_file())

    def test_repo_root_override_wins_over_the_document(self):
        modules, edges = self.two_module_repo()
        doc = self.doc(modules, edges)
        doc["repo"]["root"] = "/definitely/not/here"
        graph = self.root / "architecture.json"
        graph.write_text(json.dumps(doc))
        self.assertEqual(validate_main([str(graph)]), 1)
        self.assertEqual(validate_main([str(graph), "--repo-root", str(self.root)]), 0)


if __name__ == "__main__":
    unittest.main()
