"""Відкриті приклади 07 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(7)

PUBLIC = [('error_budget',
  ('99.9', [(100000, 40), (100000, 80), (100000, 30)]),
  {'total': 300000,
   'errors': 150,
   'allowed_errors': 300,
   'budget_left': 150,
   'burn_rate': '0.50',
   'worst_day': 2,
   'status': 'норма'}),
 ('error_budget',
  ('99.5', [(2000, 8), (1000, 9)]),
  {'total': 3000,
   'errors': 17,
   'allowed_errors': 15,
   'budget_left': -2,
   'burn_rate': '1.13',
   'worst_day': 2,
   'status': 'вичерпано'})]


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
    for name in ('error_budget',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
