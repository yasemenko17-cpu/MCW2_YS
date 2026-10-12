"""Відкриті приклади 10 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(10)

PUBLIC = [('pipeline_plan',
  ({'on': {'push': {'branches': ['main', 'release/*']}},
    'jobs': {'lint': {},
             'test': {'strategy': {'matrix': {'python': ['3.11', '3.12', '3.13'],
                                              'os': ['ubuntu', 'windows'],
                                              'exclude': [{'os': 'windows', 'python': '3.11'}]}}},
             'build': {'needs': ['lint', 'test']}}},
   'push',
   'main',
   {'lint': 2, 'test': 5, 'build': 4}),
  {'triggered': True,
   'waves': [['lint', 'test'], ['build']],
   'runs': {'lint': 1, 'test': 5, 'build': 1},
   'total_minutes': 31,
   'critical_minutes': 9}),
 ('pipeline_plan',
  ({'on': 'push', 'jobs': {'a': {}}}, 'pull_request', 'main', {}),
  {'triggered': False, 'waves': [], 'runs': {}, 'total_minutes': 0, 'critical_minutes': 0})]


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
    for name in ('pipeline_plan',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
