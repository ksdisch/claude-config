import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from render_map import (  # noqa: E402
    back_edges,
    build_views,
    embed,
    layout,
    main as render_main,
    order_layers,
    rank_nodes,
    render,
    roll_up,
)


def module(module_id, parent=None, **extra):
    base = {
        "id": module_id,
        "name": module_id.rsplit("/", 1)[-1],
        "parent": parent,
        "path": module_id,
        "summary": f"what {module_id} does.",
    }
    base.update(extra)
    return base


def edge(source, target, **extra):
    base = {
        "from": source,
        "to": target,
        "evidence": [{"file": f"{source}/index.ts", "line": 1}],
    }
    base.update(extra)
    return base


def document(modules, edges, **extra):
    doc = {
        "schema": "arch-graph/v1",
        "repo": {"name": "demo", "root": "/tmp/demo", "commit": "0123456789abcdef"},
        "roots": ["src"],
        "modules": modules,
        "edges": edges,
    }
    doc.update(extra)
    return doc


def node(node_id, label=None, sublabel="", has_children=False):
    return {
        "id": node_id,
        "label": label or node_id,
        "sublabel": sublabel,
        "has_children": has_children,
    }


class TestLayering(unittest.TestCase):
    def test_dependency_sits_below_its_dependent(self):
        ranks = rank_nodes(["ui", "core"], [("ui", "core")])
        self.assertLess(ranks["ui"], ranks["core"])

    def test_longest_path_not_shortest(self):
        """ui → core → db and ui → db must put db below core, not beside it."""
        ranks = rank_nodes(["ui", "core", "db"], [("ui", "core"), ("core", "db"), ("ui", "db")])
        self.assertEqual(ranks["ui"], 0)
        self.assertEqual(ranks["core"], 1)
        self.assertEqual(ranks["db"], 2)

    def test_isolated_node_ranks_at_the_top(self):
        self.assertEqual(rank_nodes(["lonely"], []), {"lonely": 0})

    def test_back_edges_found_in_a_two_cycle(self):
        found = back_edges(["a", "b"], [("a", "b"), ("b", "a")])
        self.assertEqual(len(found), 1)
        self.assertTrue(found <= {("a", "b"), ("b", "a")})

    def test_acyclic_graph_has_no_back_edges(self):
        self.assertEqual(back_edges(["a", "b", "c"], [("a", "b"), ("b", "c"), ("a", "c")]), set())

    def test_back_edge_detection_is_iterative(self):
        """A long chain must not blow the recursion limit — the deepest graphs
        are exactly the ones a reader most needs drawn."""
        ids = [f"n{i}" for i in range(4000)]
        pairs = [(f"n{i}", f"n{i + 1}") for i in range(3999)] + [("n3999", "n0")]
        self.assertEqual(len(back_edges(ids, pairs)), 1)

    def test_layer_ordering_is_deterministic(self):
        layers = {0: ["a", "b"], 1: ["x", "y"]}
        pairs = [("a", "y"), ("b", "x")]
        first = order_layers(layers, pairs)
        second = order_layers({0: ["a", "b"], 1: ["x", "y"]}, pairs)
        self.assertEqual(first, second)

    def test_layer_ordering_pulls_a_child_under_its_parent(self):
        layers = {0: ["a", "b", "c"], 1: ["z"]}
        ordered = order_layers(layers, [("c", "z")])
        self.assertEqual(ordered[0], ["a", "b", "c"])
        self.assertEqual(ordered[1], ["z"])


class TestLayout(unittest.TestCase):
    def test_nodes_get_geometry_and_ranks(self):
        placed = layout(
            [node("ui"), node("core")],
            [{"from": "ui", "to": "core", "kind": "import"}],
        )
        positions = {n["id"]: n for n in placed["nodes"]}
        self.assertLess(positions["ui"]["y"], positions["core"]["y"])
        self.assertGreater(placed["width"], 0)
        self.assertGreater(placed["height"], positions["core"]["y"])

    def test_edge_path_runs_downward_for_a_forward_edge(self):
        placed = layout(
            [node("ui"), node("core")], [{"from": "ui", "to": "core", "kind": "import"}]
        )
        drawn = placed["edges"][0]
        self.assertFalse(drawn["cycle"])
        start_y = float(drawn["d"].split()[1].split(",")[1])
        end_y = float(drawn["d"].split()[-1].split(",")[1])
        self.assertLess(start_y, end_y)

    def test_cycle_edge_is_marked_and_drawn_upward(self):
        placed = layout(
            [node("a"), node("b")],
            [{"from": "a", "to": "b", "kind": "import"}, {"from": "b", "to": "a", "kind": "import"}],
        )
        cyclic = [e for e in placed["edges"] if e["cycle"]]
        self.assertEqual(len(cyclic), 1)
        drawn = cyclic[0]
        start_y = float(drawn["d"].split()[1].split(",")[1])
        end_y = float(drawn["d"].split()[-1].split(",")[1])
        self.assertGreater(start_y, end_y)

    def test_parallel_edges_of_different_kinds_do_not_overlap(self):
        placed = layout(
            [node("ui"), node("core")],
            [
                {"from": "ui", "to": "core", "kind": "import"},
                {"from": "ui", "to": "core", "kind": "type-only"},
            ],
        )
        self.assertNotEqual(placed["edges"][0]["d"], placed["edges"][1]["d"])

    def test_an_edge_skipping_a_rank_is_bowed_around_it(self):
        """A straight line from rank 0 to rank 2 passes through whatever sits on
        rank 1, which reads as a dependency on that module rather than past it."""
        placed = layout(
            [node("ui"), node("core"), node("db")],
            [
                {"from": "ui", "to": "core", "kind": "import"},
                {"from": "core", "to": "db", "kind": "import"},
                {"from": "ui", "to": "db", "kind": "import"},
            ],
        )
        short = next(e for e in placed["edges"] if (e["from"], e["to"]) == ("ui", "core"))
        long = next(e for e in placed["edges"] if (e["from"], e["to"]) == ("ui", "db"))
        control_x = lambda d: [float(p.split(",")[0]) for p in d.replace("M ", "").replace("C ", "").split()]
        self.assertEqual(len(set(control_x(short["d"]))), 1, "a one-rank edge stays vertical")
        self.assertGreater(len(set(control_x(long["d"]))), 1, "a two-rank edge must bow")

    def test_bowed_edges_stay_inside_the_canvas(self):
        placed = layout(
            [node("a"), node("b"), node("c"), node("d")],
            [
                {"from": "a", "to": "b", "kind": "import"},
                {"from": "b", "to": "c", "kind": "import"},
                {"from": "c", "to": "d", "kind": "import"},
                {"from": "a", "to": "d", "kind": "import"},
            ],
        )
        xs = []
        for drawn in placed["edges"]:
            xs += [float(p.split(",")[0]) for p in drawn["d"].replace("M ", "").replace("C ", "").split()]
        self.assertGreaterEqual(min(xs), 0)
        self.assertLessEqual(max(xs), placed["width"])
        self.assertGreaterEqual(min(n["x"] for n in placed["nodes"]), 0)

    def test_wide_label_widens_its_node(self):
        narrow = layout([node("a")], [])["nodes"][0]["w"]
        wide = layout([node("b", label="a-very-long-module-name-indeed")], [])["nodes"][0]["w"]
        self.assertGreater(wide, narrow)

    def test_layout_is_stable_across_runs(self):
        nodes = [node("a"), node("b"), node("c")]
        edges = [{"from": "a", "to": "c", "kind": "import"}, {"from": "b", "to": "c", "kind": "import"}]
        first = layout([dict(n) for n in nodes], [dict(e) for e in edges])
        second = layout([dict(n) for n in nodes], [dict(e) for e in edges])
        self.assertEqual(
            [(n["id"], n["x"], n["y"]) for n in first["nodes"]],
            [(n["id"], n["x"], n["y"]) for n in second["nodes"]],
        )

    def test_edges_to_nodes_outside_the_view_are_dropped(self):
        placed = layout([node("a")], [{"from": "a", "to": "elsewhere", "kind": "import"}])
        self.assertEqual(placed["edges"], [])


class TestRollUp(unittest.TestCase):
    def setUp(self):
        self.parents = {
            "src/game": None,
            "src/game/net": "src/game",
            "src/shared": None,
        }

    def test_submodule_edge_rolls_up_to_the_parent(self):
        rolled = roll_up(
            [edge("src/game/net", "src/shared", count=4)], {"src/game", "src/shared"}, self.parents
        )
        self.assertEqual(len(rolled), 1)
        self.assertEqual((rolled[0]["from"], rolled[0]["to"]), ("src/game", "src/shared"))
        self.assertEqual(rolled[0]["count"], 4)
        self.assertEqual(rolled[0]["via"], [{"from": "src/game/net", "to": "src/shared"}])

    def test_two_edges_between_the_same_pair_merge_and_sum(self):
        rolled = roll_up(
            [edge("src/game/net", "src/shared", count=2), edge("src/game", "src/shared", count=3)],
            {"src/game", "src/shared"},
            self.parents,
        )
        self.assertEqual(len(rolled), 1)
        self.assertEqual(rolled[0]["count"], 5)

    def test_different_kinds_stay_separate_edges(self):
        rolled = roll_up(
            [
                edge("src/game", "src/shared", kind="import"),
                edge("src/game", "src/shared", kind="type-only"),
            ],
            {"src/game", "src/shared"},
            self.parents,
        )
        self.assertEqual(len(rolled), 2)

    def test_an_edge_internal_to_one_view_node_is_not_drawn(self):
        parents = {"src/game": None, "src/game/net": "src/game", "src/game/ui": "src/game"}
        rolled = roll_up([edge("src/game/ui", "src/game/net")], {"src/game"}, parents)
        self.assertEqual(rolled, [])

    def test_an_edge_leaving_the_view_entirely_is_not_drawn(self):
        rolled = roll_up([edge("src/game", "src/shared")], {"src/game"}, self.parents)
        self.assertEqual(rolled, [])


class TestViewsAndPanels(unittest.TestCase):
    def modules(self):
        return [
            module("src/game", layer="client", file_count=20),
            module("src/game/net", parent="src/game", file_count=3),
            module("src/game/ui", parent="src/game", file_count=17),
            module("src/shared", layer="contract", file_count=5),
        ]

    def test_root_view_holds_only_top_level_modules(self):
        views, _ = build_views(document(self.modules(), [edge("src/game/net", "src/shared")]))
        self.assertEqual(sorted(n["id"] for n in views[""]["nodes"]), ["src/game", "src/shared"])
        self.assertEqual(len(views[""]["edges"]), 1)

    def test_a_module_with_children_gets_a_drill_view(self):
        views, _ = build_views(
            document(self.modules(), [edge("src/game/ui", "src/game/net"), edge("src/game/net", "src/shared")])
        )
        self.assertIn("src/game", views)
        drill = views["src/game"]
        self.assertEqual(sorted(n["id"] for n in drill["nodes"]), ["src/game/net", "src/game/ui"])
        self.assertEqual(len(drill["edges"]), 1)

    def test_a_leaf_module_gets_no_drill_view(self):
        views, _ = build_views(document(self.modules(), []))
        self.assertNotIn("src/shared", views)

    def test_node_sublabel_shows_layer_and_file_count(self):
        views, _ = build_views(document(self.modules(), []))
        shared = next(n for n in views[""]["nodes"] if n["id"] == "src/shared")
        self.assertEqual(shared["sublabel"], "contract · 5 files")

    def test_has_children_flag_drives_the_drill_affordance(self):
        views, _ = build_views(document(self.modules(), []))
        flags = {n["id"]: n["has_children"] for n in views[""]["nodes"]}
        self.assertTrue(flags["src/game"])
        self.assertFalse(flags["src/shared"])

    def test_panel_relations_count_the_whole_subtree(self):
        _, panels = build_views(
            document(self.modules(), [edge("src/game/net", "src/shared", count=7)])
        )
        game = panels["src/game"]
        self.assertEqual(len(game["outbound"]), 1)
        self.assertEqual(game["outbound"][0]["other"], "src/shared")
        self.assertEqual(game["outbound"][0]["via"], "src/game/net")
        self.assertEqual(panels["src/shared"]["inbound"][0]["other"], "src/game/net")

    def test_panel_ignores_edges_internal_to_the_subtree(self):
        _, panels = build_views(document(self.modules(), [edge("src/game/ui", "src/game/net")]))
        self.assertEqual(panels["src/game"]["outbound"], [])
        self.assertEqual(panels["src/game"]["inbound"], [])

    def test_panel_carries_anchors_and_children(self):
        modules = self.modules()
        modules[0]["anchors"] = [{"file": "src/game/main.ts", "line": 9, "label": "boot"}]
        _, panels = build_views(document(modules, []))
        self.assertEqual(panels["src/game"]["anchors"][0]["line"], 9)
        self.assertEqual(panels["src/game"]["children"], ["src/game/net", "src/game/ui"])


class TestHtmlOutput(unittest.TestCase):
    def setUp(self):
        self.doc = document(
            [
                module("src/game", layer="client", file_count=2),
                module("src/game/net", parent="src/game", file_count=1),
                module("src/shared", layer="contract", file_count=1),
            ],
            [edge("src/game/net", "src/shared", count=3)],
            notes=["`src/legacy` was left unmapped on purpose."],
        )
        self.html = render(self.doc)

    def test_page_is_well_formed_enough_to_open(self):
        self.assertTrue(self.html.startswith("<!doctype html>"))
        for tag in ("<html", "<head>", "<body>", "<title>"):
            self.assertEqual(self.html.count(tag), 1, tag)
        self.assertIn("</html>", self.html)

    def test_no_external_resource_is_loaded(self):
        self.assertEqual(re.findall(r'src="https?://', self.html), [])
        self.assertEqual(re.findall(r'<link[^>]+href="https?://', self.html), [])
        self.assertNotIn("@import", self.html)
        self.assertEqual(re.findall(r'url\(\s*["\']?https?://', self.html), [])

    def test_every_css_variable_is_defined_in_all_four_theme_blocks(self):
        used = set(re.findall(r"var\((--[a-z0-9-]+)\)", self.html))
        blocks = re.findall(
            r"(?::root\s*\{|:root\[data-theme=\"(?:dark|light)\"\]\s*\{|@media \(prefers-color-scheme: dark\) \{\s*:root \{)(.*?)\}",
            self.html,
            re.S,
        )
        self.assertEqual(len(blocks), 4, "expected :root, the dark media query, and both overrides")
        for index, block in enumerate(blocks):
            defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", block))
            # The base :root also carries structural variables the overrides
            # need not restate; every *colour* must be in all four.
            missing = {v for v in used if v not in defined and v.startswith("--")} if index == 0 else set()
            self.assertEqual(missing, set(), f"block {index} is missing {missing}")

    def test_theme_overrides_follow_the_media_query(self):
        """`[data-theme]` must win over `prefers-color-scheme`, which in a
        same-specificity stylesheet means it has to come later."""
        media = self.html.index("@media (prefers-color-scheme: dark)")
        for override in ('[data-theme="light"]', '[data-theme="dark"]'):
            self.assertGreater(self.html.index(override), media, override)

    def test_graph_data_is_embedded_not_fetched(self):
        self.assertIn("const VIEWS =", self.html)
        self.assertIn("const PANELS =", self.html)
        self.assertNotIn("fetch(", self.html)
        self.assertNotIn("XMLHttpRequest", self.html)

    def test_notes_and_cycle_state_reach_the_findings_banner(self):
        self.assertIn("No cycles at the top level", self.html)
        self.assertIn("left unmapped on purpose", self.html)

    def test_cycle_is_announced_in_the_banner(self):
        doc = document(
            [module("src/a"), module("src/b")],
            [edge("src/a", "src/b"), edge("src/b", "src/a")],
        )
        html = render(doc)
        self.assertIn("dependency cycle", html)
        self.assertIn("src/a", html)

    def test_uncommitted_tree_is_stated_rather_than_implied(self):
        doc = document([module("src/a")], [])
        doc["repo"].pop("commit")
        self.assertIn("uncommitted tree", render(doc))

    def test_title_can_be_overridden(self):
        self.assertIn("<title>my map</title>", render(self.doc, "my map"))


class TestEmbedding(unittest.TestCase):
    def test_a_closing_script_tag_in_the_data_cannot_end_the_block(self):
        payload = embed({"summary": "handles </script><script>alert(1)</script> input"})
        self.assertNotIn("</script>", payload)
        self.assertEqual(
            json.loads(payload)["summary"], "handles </script><script>alert(1)</script> input"
        )

    def test_embedded_json_round_trips(self):
        data = {"a": [1, 2, {"b": "x & y < z"}]}
        self.assertEqual(json.loads(embed(data)), data)

    def test_markup_in_a_summary_stays_text_in_the_page(self):
        doc = document([module("src/a", summary="uses <b>bold</b> & </script> in prose")], [])
        html = render(doc)
        self.assertNotIn("<b>bold</b>", html)
        self.assertEqual(html.count("</script>"), 2)  # the page's own two blocks, nothing more


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp()).resolve()
        self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)

    def test_writes_a_map_and_exits_zero(self):
        graph = self.dir / "architecture.json"
        graph.write_text(json.dumps(document([module("src/a"), module("src/b")], [edge("src/a", "src/b")])))
        out = self.dir / "map.html"
        self.assertEqual(render_main([str(graph), "-o", str(out)]), 0)
        self.assertIn("<!doctype html>", out.read_text())

    def test_refuses_a_document_of_another_schema(self):
        graph = self.dir / "architecture.json"
        doc = document([module("src/a")], [])
        doc["schema"] = "arch-graph/v9"
        graph.write_text(json.dumps(doc))
        with self.assertRaises(SystemExit):
            render_main([str(graph), "-o", str(self.dir / "map.html")])

    def test_refuses_a_document_with_no_modules(self):
        graph = self.dir / "architecture.json"
        graph.write_text(json.dumps(document([], [])))
        with self.assertRaises(SystemExit):
            render_main([str(graph), "-o", str(self.dir / "map.html")])


if __name__ == "__main__":
    unittest.main()
