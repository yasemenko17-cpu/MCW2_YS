"""Відкриті приклади 04 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(4)

PUBLIC = [('parse_exposition',
  ('# HELP http_requests_total Кількість запитів.\n'
   '# TYPE http_requests_total counter\n'
   'http_requests_total{method="GET",code="200"} 1027\n'
   'http_requests_total{method="POST",code="500"} 3 1712000000000\n'
   'up 1\n',),
  [('http_requests_total', {'method': 'GET', 'code': '200'}, 1027.0),
   ('http_requests_total', {'method': 'POST', 'code': '500'}, 3.0),
   ('up', {}, 1.0)]),
 ('parse_exposition',
  ('request_seconds_bucket{le="0.5",path="/a\\"b"} 24054\n'
   'request_seconds_bucket{le="+Inf",path="/a\\"b"} 144320\n'
   'memory_bytes 1.5e3\n',),
  [('request_seconds_bucket', {'le': '0.5', 'path': '/a"b'}, 24054.0),
   ('request_seconds_bucket', {'le': '+Inf', 'path': '/a"b'}, 144320.0),
   ('memory_bytes', {}, 1500.0)])]


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
    for name in ('parse_exposition',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
