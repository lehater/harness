#!/usr/bin/env python3
"""Distribution lifetime consistency and reproducible repository usage inventory."""
from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'spec/distribution/consumer-api-lifecycle-v0.yaml'
INVENTORY = 'spec/distribution/consumer-api-usage-v0.json'
DESIGN = 'docs/design/harness-consumer-api-lifecycle-v0.md'


def facade_paths(layout: dict) -> set[str]:
    compatibility = layout['compatibility']
    return set(compatibility['cli_facades']) | {
        identity.replace('.', '/') + '.py'
        for identity in compatibility['module_facades']
    }


def validate(contract: dict, layout: dict, root: Path = ROOT) -> None:
    assert contract['kind'] == 'harness-consumer-api-lifecycle'
    assert contract['states'] == ['SUPPORTED', 'DEPRECATED', 'EOL', 'REMOVED']
    assert contract['transitions'] == [
        {'from': a, 'to': b, 'requires': 'explicit-distribution-decision'}
        for a, b in zip(contract['states'], contract['states'][1:])
    ]
    assert set(contract['state_obligations']) == set(contract['states'])
    assert all(contract['state_obligations'].values())
    for api in ('v0', 'v1'):
        assert contract['apis'][api]['state'] == 'SUPPORTED', 'current source supports both APIs'
        assert contract['apis'][api]['decision'] == DESIGN
    compat = layout['compatibility']
    expected = {(kind, identity) for kind in ('import_aliases', 'cli_facades', 'module_facades')
                for identity in compat[kind]}
    records = contract['compatibility_inventory']
    assert len(records) == len(expected)
    assert {(r['registry'], r['identity']) for r in records} == expected
    for row in records:
        kind, identity = row['registry'], row['identity']
        # Physical mappings/targets belong exclusively to repository-layout.
        assert set(row) == {'registry', 'identity', 'role', 'consumer_apis', 'disposition', 'blocker'}
        if kind == 'import_aliases':
            assert row['disposition'] == 'REVIEW_CORE_REEXPORTS_SEPARATELY'
            assert row['consumer_apis'] == ['v0', 'v1']
            assert (root / compat[kind][identity]['bridge']).is_file()
        else:
            assert row['role'] == 'v0-facade'
            assert row['consumer_apis'] == ['v0']
            assert row['disposition'] == 'DELETE_AFTER_V0_EOL'
            path = identity if kind == 'cli_facades' else identity.replace('.', '/') + '.py'
            assert (root / path).is_file(), path
        assert row['blocker']
    special = {r['identity']: r for r in contract['special_surfaces']}
    assert len(special) == len(contract['special_surfaces']) == 6
    expected_special = {
        'harness/__init__.py#execution-bridge': 'RETAIN_EXECUTION_BRIDGE_PENDING_SEPARATE_DECISION',
        'harness/__init__.py#core-exports': 'REVIEW_CORE_REEXPORTS_SEPARATELY',
        'src/harness/__init__.py#core-exports': 'REVIEW_CORE_REEXPORTS_SEPARATELY',
        'scenario_suite.py': 'RETAIN_CONSUMER_TOOLING',
        'scenario_drivers.py': 'RETAIN_CONSUMER_TOOLING',
        'adapters/copilot_behavioral_eval_agent.py': 'RETAIN_PROVIDER_TOOLING_PENDING_SEPARATE_DECISION',
    }
    assert set(special) == set(expected_special)
    for identity, disposition in expected_special.items():
        row = special[identity]
        assert row['disposition'] == disposition
        assert (root / identity.split('#')[0]).is_file()
        assert row['canonical_target'] and row['blocker'] and row['consumer_apis']
        assert row['role'] != 'v0-facade'
    assert not any(r.get('identity', '').startswith('src/') for r in records)


def usage_inventory(contract: dict, layout: dict) -> dict:
    """AST imports and bounded textual legacy paths/identities; never infer semantics."""
    surfaces = {}
    for row in contract['compatibility_inventory']:
        identity, kind = row['identity'], row['registry']
        mapping = layout['compatibility'][kind][identity]
        path = (mapping['bridge'] if kind == 'import_aliases' else
                identity if kind == 'cli_facades' else identity.replace('.', '/') + '.py')
        surfaces[f'{kind}:{identity}'] = (identity.removesuffix('.py'), path, mapping['target'])
    for row in contract['special_surfaces']:
        surfaces[row['identity']] = (row['identity'].split('#')[0].removesuffix('.py').replace('/', '.'),
                                      row['identity'].split('#')[0], row['canonical_target'])
    files = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'],
                                    cwd=ROOT, text=True).splitlines()
    result = {key: {'path': path, 'canonical_target': target, 'users': {}}
              for key, (_, path, target) in surfaces.items()}
    registry_driven_validators = []
    for relative in sorted(set(files)):
        if relative in (CONTRACT, INVENTORY, DESIGN, 'validators/validate_consumer_api_lifecycle.py'):
            continue
        file = ROOT / relative
        if not file.is_file() or file.suffix not in ('.py', '.md', '.yaml', '.yml', '.json', '.sh'):
            continue
        body = file.read_text(errors='replace')
        if relative.startswith('validators/') and all(
            name in body for name in ('cli_facades', 'module_facades')
        ):
            registry_driven_validators.append(relative)
        imports = set()
        if file.suffix == '.py':
            try:
                for node in ast.walk(ast.parse(body)):
                    if isinstance(node, ast.Import):
                        imports.update(a.name for a in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0:
                        imports.add(node.module)
                        imports.update(f'{node.module}.{a.name}' for a in node.names)
            except SyntaxError:
                pass
        category = ('canonical_runtime' if relative.startswith('src/harness/') else
                    'historical' if relative.startswith(('docs/audit/', 'docs/legacy/', 'docs/plans/', 'spec/assurance/evidence/')) else
                    'distribution_tooling' if relative.startswith(('spec/distribution/', 'spec/architecture/')) else
                    'validators_tests' if relative.startswith(('validators/', 'tests/', 'spec/')) else
                    'documentation_examples' if relative.startswith(('docs/', 'examples/', 'skills/')) else
                    'distribution_tooling')
        for key, (identity, path, _) in surfaces.items():
            # Runtime dependency claims use executable imports only. Other hits
            # are reference evidence, including string probes and declarative mappings.
            hit = identity in imports
            if category != 'canonical_runtime':
                hit = hit or (path in body and bool(re.search(r'(?<![\w./])' + re.escape(path) + r'(?![\w/])', body)))
                if '.' in identity and identity in body:
                    hit = hit or bool(re.search(r'(?<![\w.])' + re.escape(identity) + r'(?![\w.])', body))
            if hit and relative != path:
                result[key]['users'].setdefault(category, []).append(relative)
    return {'version': 1, 'method': 'AST absolute imports; bounded textual facade paths/dotted identities outside runtime',
            'registry_driven_validators': registry_driven_validators, 'surfaces': result}


def main() -> int:
    layout = yaml.safe_load((ROOT / 'spec/architecture/repository-layout-v0.yaml').read_text())
    contract = yaml.safe_load((ROOT / CONTRACT).read_text())
    validate(contract, layout)
    actual = usage_inventory(contract, layout)
    assert json.loads((ROOT / INVENTORY).read_text()) == actual, 'usage inventory stale'
    # Contract mutations prove rejection at the smallest surface.
    mutations = []
    bad = copy.deepcopy(contract); bad['compatibility_inventory'].pop(); mutations.append(bad)
    bad = copy.deepcopy(contract); bad['compatibility_inventory'][0]['identity'] = 'unknown'; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['apis']['v0']['state'] = 'EOL'; mutations.append(bad)
    for index in range(len(contract['special_surfaces'])):
        bad = copy.deepcopy(contract); bad['special_surfaces'][index]['disposition'] = 'DELETE_AFTER_V0_EOL'; mutations.append(bad)
    for bad in mutations:
        try:
            validate(bad, layout)
        except AssertionError:
            continue
        raise AssertionError('invalid lifecycle mutation accepted')
    print(f'Consumer API lifecycle/inventory PASS: {len(facade_paths(layout))} v0-only facades')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
