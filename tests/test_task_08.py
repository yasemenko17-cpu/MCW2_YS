"""Відкриті приклади 08 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(8)

PUBLIC = [('inventory_vars',
  ('[web]\n'
   'web1 http_port=8080\n'
   'web2\n'
   '\n'
   '[prod:children]\n'
   'web\n'
   '\n'
   '[web:vars]\n'
   'http_port=80\n'
   'env=web\n'
   '\n'
   '[prod:vars]\n'
   'env=prod\n',),
  {'web1': {'groups': ['prod', 'web'], 'vars': {'env': 'web', 'http_port': 8080}},
   'web2': {'groups': ['prod', 'web'], 'vars': {'env': 'web', 'http_port': 80}}}),
 ('inventory_vars',
  ('solo\n'
   '\n'
   '[a]\n'
   'h1\n'
   '\n'
   '[b]\n'
   'h1 x=5\n'
   '\n'
   '[ab:children]\n'
   'a\n'
   'b\n'
   '\n'
   '[ab:vars]\n'
   'x=1\n'
   'y=2\n'
   '\n'
   '[b:vars]\n'
   'y=3\n',),
  {'h1': {'groups': ['a', 'ab', 'b'], 'vars': {'x': 5, 'y': 3}},
   'solo': {'groups': ['ungrouped'], 'vars': {}}})]


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
    for name in ('inventory_vars',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
