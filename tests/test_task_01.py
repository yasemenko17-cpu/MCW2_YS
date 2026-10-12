"""Відкриті приклади 01 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(1)

PUBLIC = [('dockerfile_issues',
  ('FROM python:latest\n'
   'RUN apt-get update && apt-get install -y curl\n'
   'ADD app.tar.gz /app/\n'
   'ADD config.ini /etc/\n'
   'RUN pip install flask\n'
   'CMD ["python"]\n',),
  ['рядок 1: образ python:latest без фіксованого тега',
   'рядок 2: apt-get install без --no-install-recommends',
   'рядок 4: ADD замість COPY для config.ini',
   'рядок 5: pip install без --no-cache-dir',
   'рядок 1: останній етап працює від root']),
 ('dockerfile_issues',
  ('FROM golang:1.22 AS build\n'
   'RUN go build -o /out/app .\n'
   '\n'
   'FROM alpine\n'
   'RUN apt-get install \\\n'
   '    --no-install-recommends curl\n'
   'USER 1000\n',),
  ['рядок 4: образ alpine без фіксованого тега'])]


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
    for name in ('dockerfile_issues',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
