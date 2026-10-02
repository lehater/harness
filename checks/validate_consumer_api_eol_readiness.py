#!/usr/bin/env python3
"""Fail-closed repository-local Consumer API v0 EOL evidence, not authorization."""
from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
import sys
from functools import cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from validators.validate_consumer_api_lifecycle import (  # noqa: E402
    CONTRACT as LIFECYCLE, INVENTORY, facade_paths, usage_inventory, validate as validate_lifecycle,
)

CONTRACT = 'spec/distribution/consumer-api-v0-eol-readiness-v0.yaml'
LAYOUT = 'spec/architecture/repository-layout-v0.yaml'


def repository_files(root: Path) -> list[str]:
    return sorted(set(subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
        cwd=root, text=True,
    ).splitlines()))


def execution_references(root: Path, layout: dict) -> dict[str, list[str]]:
    """Conservative bounded scan: imports, embedded imports, literal CLI/dynamic refs.

    Literal facade references require reviewed classification even if they are
    negative controls. Arbitrary computed Python execution is outside this oracle.
    """
    aliases = set(layout['compatibility']['module_facades']) | {'harness'}
    paths = facade_paths(layout)
    references = {}
    for relative in repository_files(root):
        path = root / relative
        if not path.is_file() or relative in paths or relative == 'harness/__init__.py':
            continue
        if path.suffix not in ('.py', '.sh', '.yml', '.yaml'):
            continue
        if relative.startswith(('docs/', 'spec/', 'skills/')):
            continue  # Declarative evidence is covered by the lifecycle usage inventory.
        hits = set()
        body = path.read_text()
        if path.suffix == '.py':
            tree = ast.parse(body)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    hits.update(a.name for a in node.names if a.name in aliases)
                elif isinstance(node, ast.ImportFrom) and node.level == 0:
                    if node.module in aliases:
                        hits.add(node.module)
                    hits.update(f'{node.module}.{a.name}' for a in node.names
                                if f'{node.module}.{a.name}' in aliases)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    # Exact filename arguments plus imports in subprocess -c probes.
                    if node.value in paths:
                        hits.add(node.value)
                    for alias in aliases:
                        if re.search(r'\b(?:from|import)\s+' + re.escape(alias) + r'(?=[\s;,]|$)', node.value):
                            hits.add(alias)
        else:
            for name in paths:
                if re.search(r'\bpython(?:3)?\s+' + re.escape(name) + r'\b', body):
                    hits.add(name)
        if hits:
            references[relative] = sorted(hits)
    return references



def assert_canonical_imports(body: str, legacy: set[str], relative: str) -> None:
    for node in ast.walk(ast.parse(body)):
        if isinstance(node, ast.Import):
            assert not any(a.name in legacy for a in node.names), relative
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            assert node.module not in legacy, relative
            assert not any(f'{node.module}.{a.name}' in legacy for a in node.names), relative


@cache
def repository_evidence(root: Path) -> tuple[dict, dict]:
    """Freeze expensive filesystem evidence once per invocation; mutations are metadata-only."""
    layout = yaml.safe_load((root / LAYOUT).read_text())
    lifecycle = yaml.safe_load((root / LIFECYCLE).read_text())
    legacy = set(layout['compatibility']['module_facades']) | {'harness'}
    for relative in repository_files(root):
        path = root / relative
        if (path.suffix == '.py' and path.is_file()
                and relative not in facade_paths(layout) and relative != 'harness/__init__.py'):
            assert_canonical_imports(path.read_text(), legacy, relative)
    # Current implicit behavior is evidence of future policy debt, never changed here.
    source = ast.parse((root / 'src/harness/application/consumer_pack.py').read_text())
    materialize = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'materialize_pack')
    assert dict(zip([a.arg for a in materialize.args.kwonlyargs],
                    materialize.args.kw_defaults))['consumer_api'].value == 'v0'
    defaults = [n for n in ast.walk(source) if isinstance(n, ast.Call)
                and any(isinstance(a, ast.Constant) and a.value == '--consumer-api' for a in n.args)]
    assert defaults and all(any(k.arg == 'default' and isinstance(k.value, ast.Constant)
                               and k.value.value == 'v0' for k in n.keywords) for n in defaults)
    return execution_references(root, layout), usage_inventory(lifecycle, layout)


def validate(contract: dict, lifecycle: dict, layout: dict, root: Path = ROOT) -> None:
    validate_lifecycle(lifecycle, layout, root)
    assert contract['version'] == 1 and contract['kind'] == 'harness-consumer-api-eol-readiness'
    assert contract['lifecycle_contract'] == LIFECYCLE
    assert contract['transition'] == {'from_api': 'v0', 'to_state': 'EOL'}
    assert not {'states', 'transitions', 'state_obligations', 'apis'} & set(contract)
    gates = contract['gates']
    assert len(gates) == 10 and {g['id'] for g in gates} == {f'G{i}' for i in range(1, 11)}
    by_id = {g['id']: g for g in gates}
    for i in range(1, 9):
        assert by_id[f'G{i}']['status'] == 'PASS'
    for gate in gates:
        assert gate['evidence'] and gate['requirement']
        assert all((root / p).is_file() for p in gate['evidence'])
    assert lifecycle['apis']['v0']['state'] == 'DEPRECATED'
    assert lifecycle['apis']['v1']['state'] == 'SUPPORTED'
    assert lifecycle['onboarding']['recommended_consumer_api'] == 'v1'
    assert by_id['G9']['status'] == 'NOT_ESTABLISHED'
    assessment = contract['external_consumer_assessment']
    assert assessment['status'] == by_id['G9']['status']
    assert assessment['evidence'] and assessment['limitations']
    for evidence in assessment['evidence']:
        assert set(evidence) == {'path', 'scope'}
        assert (root / evidence['path']).is_file() and evidence['scope']
    assert assessment['independent_consumer_evidence'] == []
    assert assessment['search_absence_proves_absence'] is False
    assert by_id['G10']['status'] == 'NOT_MET'
    assert contract['eol_decision'] == {'status': 'NOT_MET', 'decision': None}
    assert contract['overall'] == 'NOT_READY'
    assert contract['eol_blockers'] == ['G9', 'G10']
    assert contract['deletion_authorized'] is False

    # Direct imports are never exempted merely because they occur in a validator.
    references, actual = repository_evidence(root)
    expected = contract['first_party_execution']['compatibility_subjects']
    assert len(expected) == len({r['path'] for r in expected})
    classified = {r['path']: r for r in expected}
    assert set(references) == set(classified), ('unclassified execution references', references)
    for path, hits in references.items():
        assert classified[path]['references'] == hits, (path, hits)
        assert classified[path]['reason'] and classified[path]['required_action_at_eol']
        assert classified[path]['classification'] in ('compatibility-probe', 'v0-dispatch', 'reference-only')
        assert (classified[path]['classification'] == 'v0-dispatch') == (path == 'distribution/harnessw.py')
        assert not path.startswith('src/harness/'), path
    assert contract['first_party_execution']['canonical_runtime_legacy_dependencies'] == 0
    assert contract['first_party_execution']['active_non_compatibility_dependencies'] == 0
    assert actual == json.loads((root / INVENTORY).read_text()), 'lifecycle usage inventory stale'
    for key, row in actual['surfaces'].items():
        if key.startswith(('cli_facades:', 'module_facades:')):
            assert not row['users'].get('canonical_runtime'), key

    obligations = contract['obligations']
    assert len(obligations) == len({r['id'] for r in obligations})
    categories = {
        'distribution-definitions', 'wrapper-v0-dispatch', 'implicit-v0-defaults',
        'compatibility-registry', 'root-facades', 'dotted-adapter-facades',
        'compatibility-validation', 'v0-docs-examples', 'core-exports',
        'execution-bridge', 'provider-agent-exception', 'scenario-tooling',
    }
    assert {r['category'] for r in obligations} == categories
    classified_facades = []
    for row in obligations:
        assert row['owner'] and row['reason'] and row['at_eol'] and row['at_removed']
        assert row['at_eol'] != row['at_removed']
        assert row['blocks_transition'] in ('EOL', 'REMOVED', 'SEPARATE', 'NEITHER')
        assert row['delete_at_eol'] is False
        assert row['paths'] and all((root / p.split('#')[0]).is_file() for p in row['paths'])
        if row['category'] in ('root-facades', 'dotted-adapter-facades'):
            assert row['blocks_transition'] == 'REMOVED'
            classified_facades.extend(row['paths'])
        if row['category'] in ('core-exports', 'execution-bridge', 'provider-agent-exception'):
            assert row['blocks_transition'] == 'SEPARATE'
        if row['category'] == 'implicit-v0-defaults':
            assert row['paths'] == ['src/harness/application/consumer_pack.py#implicit-defaults']
            assert row['blocks_transition'] == 'EOL'
        if row['category'] == 'scenario-tooling':
            assert row['blocks_transition'] == 'NEITHER'
            assert set(row['paths']) == {'scenario_suite.py', 'scenario_drivers.py'}
        assert not any(p.startswith('src/harness/') for p in row['paths']) or row['category'] in (
            'core-exports', 'implicit-v0-defaults')
    assert len(classified_facades) == len(set(classified_facades))
    assert set(classified_facades) == facade_paths(layout)
    core = next(r for r in obligations if r['category'] == 'core-exports')
    assert set(core['paths']) == {'harness/__init__.py#core-exports', 'src/harness/__init__.py#core-exports'}


def main() -> int:
    contract = yaml.safe_load((ROOT / CONTRACT).read_text())
    lifecycle = yaml.safe_load((ROOT / LIFECYCLE).read_text())
    layout = yaml.safe_load((ROOT / LAYOUT).read_text())
    validate(contract, lifecycle, layout)
    mutations = []
    for identity, status in (('G1', 'NOT_MET'), ('G9', 'PASS'), ('G10', 'PASS')):
        bad = copy.deepcopy(contract)
        next(g for g in bad['gates'] if g['id'] == identity)['status'] = status
        mutations.append(bad)
    for key, value in (('overall', 'READY'), ('deletion_authorized', True), ('eol_blockers', [])):
        bad = copy.deepcopy(contract); bad[key] = value; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['gates'].pop(); mutations.append(bad)
    bad = copy.deepcopy(contract); bad['external_consumer_assessment']['search_absence_proves_absence'] = True; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['obligations'].pop(); mutations.append(bad)
    for category in ('root-facades', 'core-exports', 'execution-bridge', 'provider-agent-exception', 'scenario-tooling'):
        bad = copy.deepcopy(contract)
        next(r for r in bad['obligations'] if r['category'] == category)['blocks_transition'] = 'EOL'
        mutations.append(bad)
    bad = copy.deepcopy(contract); bad['first_party_execution']['compatibility_subjects'].pop(); mutations.append(bad)
    for category in ('root-facades', 'dotted-adapter-facades'):
        bad = copy.deepcopy(contract)
        row = next(r for r in bad['obligations'] if r['category'] == category)
        bad['obligations'].remove(row)
        mutations.append(bad)
    bad = copy.deepcopy(contract)
    bad['obligations'][0]['paths'] = ['src/harness/application/skill_router.py']
    mutations.append(bad)
    bad = copy.deepcopy(contract)
    bad['obligations'][0]['at_removed'] = bad['obligations'][0]['at_eol']
    mutations.append(bad)
    bad = copy.deepcopy(contract)
    bad['first_party_execution']['compatibility_subjects'][0]['classification'] = 'ordinary-runtime'
    mutations.append(bad)
    legacy = set(layout['compatibility']['module_facades']) | {'harness'}
    assert_canonical_imports('from harness.project_model.core import CoreError', legacy, 'ordinary.py')
    for statement in ('import consumer_pack', 'from harness import CoreError',
                      'from adapters import canonical_graph', 'from skill_router import route_operation'):
        try:
            assert_canonical_imports(statement, legacy, 'ordinary.py')
        except AssertionError:
            continue
        raise AssertionError('ordinary first-party legacy import accepted')
    for bad in mutations:
        try:
            validate(bad, lifecycle, layout)
        except AssertionError:
            continue
        raise AssertionError('unsafe readiness mutation accepted')
    print('Consumer v0 EOL readiness PASS: G1-G8 PASS; G9 NOT_ESTABLISHED; '
          'G10 NOT_MET; overall NOT_READY; runtime/non-compatibility dependencies 0')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
