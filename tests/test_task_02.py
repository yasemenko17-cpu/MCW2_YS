"""Відкриті приклади 02 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(2)

PUBLIC = [('compose_issues',
  ({'services': {'web': {'image': 'nginx:1.27',
                         'ports': ['8080:80'],
                         'depends_on': {'db': {'condition': 'service_healthy'}},
                         'volumes': ['static:/usr/share/nginx/html', './conf:/etc/nginx:ro']},
                 'db': {'image': 'postgres:16', 'volumes': ['pgdata:/var/lib/postgresql/data']},
                 'admin': {'image': 'adminer',
                           'ports': ['8080:8080'],
                           'depends_on': ['db', 'cache']}},
    'volumes': {'pgdata': {}}},),
  ['web: том static не оголошено',
   'web: залежність db чекає service_healthy, але у db немає healthcheck',
   'admin: залежність cache не знайдено',
   'admin: порт хоста 8080 уже зайнято сервісом web']),
 ('compose_issues',
  ({'services': {'app': {'ports': ['8000:8000'], 'volumes': ['./src:/app']}}},),
  [])]


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
    for name in ('compose_issues',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
