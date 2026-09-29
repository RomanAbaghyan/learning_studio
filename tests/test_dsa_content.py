"""Execute lesson implementations against independent small-input oracles."""
import bisect
import contextlib
import io
import json
from pathlib import Path
import random
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1] / 'content' / 'dsa'


def lesson(name):
    return json.loads((ROOT / 'lessons' / f'{name}.json').read_text())


def implementation(name):
    namespace = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(lesson(name)['implementations']['python'], name, 'exec'), namespace)
    return namespace


def test_binary_search_matches_bisect_with_duplicates_and_empty_inputs():
    ns = implementation('binary-search')
    rng = random.Random(13)
    for n in range(50):
        a = sorted(rng.randrange(-10, 11) for _ in range(n))
        for target in range(-12, 13):
            assert ns['lower_bound'](a, target) == bisect.bisect_left(a, target)
            assert ns['upper_bound'](a, target) == bisect.bisect_right(a, target)


def test_avl_preserves_order_height_and_balance_after_every_update():
    ns = implementation('avl-tree')
    rng = random.Random(42)
    root, expected = None, set()

    def check(node, lo=float('-inf'), hi=float('inf')):
        if node is None:
            return 0, []
        assert lo < node.key < hi
        lh, left = check(node.left, lo, node.key)
        rh, right = check(node.right, node.key, hi)
        assert abs(lh-rh) <= 1
        assert node.height == 1 + max(lh, rh)
        return node.height, left + [node.key] + right

    for _ in range(1000):
        key = rng.randrange(100)
        if rng.random() < .55:
            root = ns['insert'](root, key)
            expected.add(key)
        else:
            root = ns['erase'](root, key)
            expected.discard(key)
        assert check(root)[1] == sorted(expected)
    for key in sorted(expected):
        root = ns['erase'](root, key)
        check(root)
    assert root is None


def test_dijkstra_matches_floyd_warshall_on_small_nonnegative_graphs():
    ns = implementation('dijkstra')
    rng = random.Random(9)
    for n in range(1, 12):
        graph = [[] for _ in range(n)]
        oracle = [[float('inf')] * n for _ in range(n)]
        for u in range(n):
            oracle[u][u] = 0
            for v in range(n):
                if rng.random() < .25:
                    weight = rng.randrange(8)
                    graph[u].append((v, weight))
                    oracle[u][v] = min(oracle[u][v], weight)
        for k in range(n):
            for u in range(n):
                for v in range(n):
                    oracle[u][v] = min(oracle[u][v], oracle[u][k]+oracle[k][v])
        for source in range(n):
            distance, parent = ns['dijkstra'](graph, source)
            assert distance == oracle[source]
            for target in range(n):
                if target == source or distance[target] == float('inf'):
                    continue
                seen, cur = set(), target
                while cur != source:
                    assert cur not in seen
                    seen.add(cur)
                    predecessor = parent[cur]
                    assert predecessor is not None
                    assert any(v == cur and distance[predecessor]+w == distance[cur]
                               for v, w in graph[predecessor])
                    cur = predecessor
    with pytest.raises(ValueError):
        ns['dijkstra']([[(1, -1)], []], 0)


def test_knapsack_matches_exhaustive_subsets_and_reconstructs_once():
    ns = implementation('knapsack')
    rng = random.Random(99)
    for n in range(9):
        items = [(rng.randrange(1, 8), rng.randrange(15)) for _ in range(n)]
        for capacity in range(16):
            oracle = max(sum(items[i][1] for i in range(n) if mask >> i & 1)
                         for mask in range(1 << n)
                         if sum(items[i][0] for i in range(n) if mask >> i & 1) <= capacity)
            value, chosen = ns['knapsack'](items, capacity)
            assert value == oracle == ns['knapsack_value'](items, capacity)
            assert len(chosen) == len(set(chosen))
            assert sum(items[i][0] for i in chosen) <= capacity
            assert sum(items[i][1] for i in chosen) == value


@pytest.mark.parametrize('name', ['binary-search', 'avl-tree', 'dijkstra', 'knapsack'])
def test_javascript_examples_and_reference_problem_checks(name, tmp_path):
    if not shutil.which('node'):
        pytest.skip('node is unavailable')
    data = lesson(name)
    code = data['implementations']['javascript']
    # The AVL/Dijkstra exercises intentionally test component skills rather than
    # asking learners to paste the full reference solution.
    extras = {
        'avl-tree': 'function isBalanced(n){function h(n){if(!n)return 0;const a=h(n.left),b=h(n.right);return a<0||b<0||Math.abs(a-b)>1?-1:1+Math.max(a,b);}return h(n)>=0;}',
        'dijkstra': 'function relax(d,u,v,w){if(d[u]+w<d[v]){d[v]=d[u]+w;return true;}return false;}',
    }
    code += '\n' + extras.get(name, '') + '\n' + data['problems'][0]['tests']['javascript']
    path = tmp_path / 'example.js'
    path.write_text(code)
    subprocess.run(['node', str(path)], check=True, capture_output=True, text=True, timeout=10)
