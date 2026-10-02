#!/usr/bin/env python3
"""Distribution lifetime consistency and reproducible repository usage inventory."""
from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
import tempfile
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'spec/distribution/consumer-api-lifecycle-v0.yaml'
INVENTORY = 'spec/distribution/consumer-api-usage-v0.json'
DESIGN = 'docs/design/harness-consumer-api-lifecycle-v0.md'
DEPRECATION = 'docs/design/harness-consumer-api-v0-deprecation.md'


def facade_paths(layout: dict) -> set[str]:
    compatibility = layout['compatibility']
    return set(compatibility['cli_facades']) | {
        identity.replace('.', '/') + '.py'
        for identity in compatibility['module_facades']
    }


def validate_onboarding(contract: dict, root: Path) -> None:
    onboarding = contract['onboarding']
    assert onboarding['recommended_consumer_api'] == 'v1'
    required = {
        'README.md',
        'docs/design/agent-skill-surfaces-and-consumer-distribution-v0.md',
        'docs/design/harness-consumer-wrapper-v0.md',
        'docs/design/harness-consumer-pack-v1.md',
        'spec/distribution/target-agents-fragment-v1.md',
    }
    surfaces = onboarding['owned_surfaces']
    assert required <= set(surfaces) and len(surfaces) == len(set(surfaces))
    assert not set(surfaces) & set(onboarding['compatibility_surfaces'])
    assert onboarding['binding_example'] == 'spec/distribution/consumer-binding-example-v1.json'
    binding = json.loads((root / onboarding['binding_example']).read_text())
    assert binding['version'] == 1 and binding['kind'] == 'harness-consumer-binding'
    assert binding['consumer_api'] == 'v1'
    assert binding['source']['repository'] == 'https://github.com/lehater/harness.git'
    assert re.fullmatch(r'[0-9a-f]{40}', binding['source']['revision'])
    assert binding['source']['revision'] != '0' * 40
    for relative in surfaces:
        body = (root / relative).read_text()
        assert 'v1' in body, relative
        assert 'python .harness/harnessw.py sync' in body, relative
        assert 'python -m harness.application.skill_router' in body, relative
        # Bounded executable guidance; physical/history/compatibility prose is allowed.
        blocks = re.findall(r'```[^\n]*\n(.*?)```', body, re.S)
        blocks += re.findall(r'(?<!`)`([^`\n]+)`(?!`)', body)
        for block in blocks:
            assert not re.search(r'consumer_api[\"\']?\s*:\s*[\"\']?v0\b', block), relative
            assert not re.search(r'\bpython(?:3)?\s+(?:\S*/)?(?:skill_router|consumer_pack|harness)\.py\b', block), relative
            assert not re.search(r'\bpython(?:3)?\s+-m\s+(?:skill_router|consumer_pack)\b', block), relative
            for line in block.splitlines():
                if re.search(r'python(?:3)?\s+-m\s+harness.application.consumer_pack\s+(?:materialize|validate-definition|validate-pack)\b', line):
                    assert '--consumer-api v1' in line, relative


def validate(contract: dict, layout: dict, root: Path = ROOT) -> None:
    assert contract['kind'] == 'harness-consumer-api-lifecycle'
    assert contract['states'] == ['SUPPORTED', 'DEPRECATED', 'EOL', 'REMOVED']
    assert contract['transitions'] == [
        {'from': a, 'to': b, 'requires': 'explicit-distribution-decision'}
        for a, b in zip(contract['states'], contract['states'][1:])
    ]
    assert set(contract['state_obligations']) == set(contract['states'])
    assert all(contract['state_obligations'].values())
    assert contract['state_obligations']['DEPRECATED'] == [
        'latest-source-still-works', 'no-new-consumers', 'migrate-to-v1',
        'support-compatibility-defects-until-eol',
    ]
    for api in ('v0', 'v1'):
        assert contract['apis'][api]['state'] == ('DEPRECATED' if api == 'v0' else 'SUPPORTED')
        assert contract['apis'][api]['decision'] == (DEPRECATION if api == 'v0' else DESIGN)
    decision = (root / DEPRECATION).read_text()
    assert 'Status: accepted distribution decision.' in decision
    assert 'Consumer API v0 transitions from SUPPORTED to DEPRECATED.' in decision
    validate_onboarding(contract, root)
    compat = layout['compatibility']
    expected = {(kind, identity) for kind in ('import_aliases', 'cli_facades', 'module_facades')
                for identity in compat[kind]}
    records = contract['compatibility_inventory']
    assert len(records) == len(expected)
    assert {(r['registry'], r['identity']) for r in records} == expected
    for row in records:
        kind, identity = row['registry'], row['identity']
        # Physical mappings/targets belong exclusively to repository-layout.
        assert set(row) == {'registry', 'identity', 'role', 'physically_present_in', 'public_consumer_apis', 'disposition', 'blocker'}
        if kind == 'import_aliases':
            assert row['disposition'] == 'REVIEW_CORE_REEXPORTS_SEPARATELY'
            assert row['physically_present_in'] == ['v0', 'v1']
            assert row['public_consumer_apis'] == ['v0']
            assert (root / compat[kind][identity]['bridge']).is_file()
        else:
            assert row['role'] == 'v0-facade'
            assert row['physically_present_in'] == row['public_consumer_apis'] == ['v0']
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
        assert row['canonical_target'] and row['blocker'] and row['physically_present_in']
        assert row['physically_present_in'] == (['v0'] if row['role'] == 'provider-agent-tooling' else ['v0', 'v1'])
        expected_public = ([] if row['role'] == 'source-tree-execution-bridge' else
                           ['v0'] if 'core-exports' in identity or row['role'] == 'provider-agent-tooling' else
                           ['v0', 'v1'])
        assert row['public_consumer_apis'] == expected_public
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
        if relative in (CONTRACT, INVENTORY, DESIGN, 'checks/validate_consumer_api_lifecycle.py'):
            continue
        file = ROOT / relative
        if not file.is_file() or file.suffix not in ('.py', '.md', '.yaml', '.yml', '.json', '.sh'):
            continue
        body = file.read_text(errors='replace')
        if relative.startswith(('checks/', 'tests/')) and all(
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
                    'validators_tests' if relative.startswith(('checks/', 'tests/', 'spec/')) else
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
    for state in ('SUPPORTED', 'EOL', 'REMOVED'):
        bad = copy.deepcopy(contract); bad['apis']['v0']['state'] = state; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['apis']['v1']['state'] = 'DEPRECATED'; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['apis']['v0']['decision'] = DESIGN; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['onboarding']['recommended_consumer_api'] = 'v0'; mutations.append(bad)
    bad = copy.deepcopy(contract); bad['onboarding']['owned_surfaces'].pop(); mutations.append(bad)
    bad = copy.deepcopy(contract); bad['compatibility_inventory'][0]['public_consumer_apis'] = ['v0', 'v1']; mutations.append(bad)
    for index in (0, 1, 2):
        bad = copy.deepcopy(contract); bad['special_surfaces'][index]['public_consumer_apis'] = ['v0', 'v1']; mutations.append(bad)
    for index in range(len(contract['special_surfaces'])):
        bad = copy.deepcopy(contract); bad['special_surfaces'][index]['disposition'] = 'DELETE_AFTER_V0_EOL'; mutations.append(bad)
    for bad in mutations:
        try:
            validate(bad, layout)
        except AssertionError:
            continue
        raise AssertionError('invalid lifecycle mutation accepted')
    # New guidance in an owned surface and new explicitly registered surfaces
    # must be rejected. Keep historical/v0 compatibility prose outside this rule.
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        paths = contract['onboarding']['owned_surfaces'] + [contract['onboarding']['binding_example']]
        for relative in paths:
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        validate_onboarding(contract, root)
        readme = root / 'README.md'
        original = readme.read_text()
        for guidance in ('consumer_api: v0', 'python skill_router.py operation',
                         'python consumer_pack.py sync', 'python harness.py validate',
                         'python -m harness.application.consumer_pack materialize SOURCE PACK --revision SHA'):
            readme.write_text(original + '\n```sh\n' + guidance + '\n```\n')
            try:
                validate_onboarding(contract, root)
            except AssertionError:
                pass
            else:
                raise AssertionError('deprecated onboarding guidance accepted')
        readme.write_text(original)
        extended = copy.deepcopy(contract)
        extended['onboarding']['owned_surfaces'].append('new-consumer.md')
        (root / 'new-consumer.md').write_text(original + '\n```yaml\nconsumer_api: v0\n```\n')
        try:
            validate_onboarding(extended, root)
        except AssertionError:
            pass
        else:
            raise AssertionError('new owned surface recommends v0')
        binding_path = root / contract['onboarding']['binding_example']
        binding = json.loads(binding_path.read_text())
        binding['consumer_api'] = 'v0'
        binding_path.write_text(json.dumps(binding))
        try:
            validate_onboarding(contract, root)
        except AssertionError:
            pass
        else:
            raise AssertionError('v0 canonical binding accepted')
    print(f'Consumer API lifecycle/inventory PASS: {len(facade_paths(layout))} v0-only facades')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
