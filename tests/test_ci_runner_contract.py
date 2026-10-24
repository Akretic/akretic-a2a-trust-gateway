from pathlib import Path

import yaml


def test_public_ci_preserves_tests_and_fork_coverage_without_write_credentials():
    workflow = yaml.safe_load(Path('.github/workflows/ci.yml').read_text())
    # PyYAML's YAML 1.1 loader interprets the unquoted Actions key `on` as True.
    triggers = workflow.get('on', workflow.get(True))
    assert set(triggers) == {'push', 'pull_request'}
    assert workflow['permissions'] == {'contents': 'read'}
    assert set(workflow['jobs']) == {'test'}
    job = workflow['jobs']['test']
    assert 'if' not in job
    assert job['runs-on'] == {
        'group': 'akretic-public-ci',
        'labels': ['self-hosted', 'Linux', 'X64', 'akretic-public-ci'],
    }
    assert job['timeout-minutes'] == 20
    assert job['steps'][0]['with']['persist-credentials'] is False
    assert job['steps'][1]['with']['python-version'] == '3.11'
    assert [step['run'] for step in job['steps'] if 'run' in step] == [
        'pip install -r requirements.txt',
        'pytest -q',
    ]
