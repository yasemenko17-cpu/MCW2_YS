"""Відкриті приклади 06 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(6)

PUBLIC = [('workflow_issues',
  ({'on': {'push': {'branches': ['main']}},
    'jobs': {'test': {'steps': [{'uses': 'actions/checkout@v4'}, {'run': 'pytest'}]},
             'build': {'needs': ['test', 'lint'],
                       'steps': [{'uses': 'actions/checkout@main'},
                                 {'run': 'echo ${{ secrets.TOKEN }} | docker login'},
                                 {'run': 'echo "${{ github.event.head_commit.message }}"'}]}}},),
  ['test: немає permissions',
   'build: немає permissions',
   'build: needs посилається на невідому задачу lint',
   'build, крок 1: дію actions/checkout@main не закріплено',
   'build, крок 2: секрет напряму у run',
   'build, крок 3: вираз github.event у run']),
 ('workflow_issues',
  ({'on': ['pull_request_target'],
    'permissions': {'contents': 'read'},
    'jobs': {'check': {'steps': [{'uses': 'actions/checkout@v4',
                                  'with': {'ref': '${{ github.event.pull_request.head.sha }}'}},
                                 {'uses': './.github/actions/lint'},
                                 {'uses': 'docker://alpine'},
                                 {'uses': 'actions/cache'}]}}},),
  ['check, крок 1: pull_request_target з checkout коду з PR',
   'check, крок 4: дію actions/cache не закріплено'])]


def _check(fn, args, expected):
    if isinstance(expected, tuple) and expected and expected[0] == "ValueError":
        with pytest.raises(ValueError) as info:
            getattr(M, fn)(*copy.deepcopy(args))
        assert str(info.value) == expected[1]
    else:
        assert getattr(M, fn)(*copy.deepcopy(args)) == expected


@pytest.mark.parametrize("fn,args,expected", PUBLIC, ids=[f"p{i}" for i in range(len(PUBLIC))])
def test_public(fn, args, expected):
    _check(fn, args, expected)


def test_functions_exist():
    for name in ('workflow_issues',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
