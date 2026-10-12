"""Відкриті приклади 09 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(9)

PUBLIC = [('dockerfile_build_plan',
  ('FROM node:20 AS web\n'
   'COPY package.json .\n'
   'RUN npm ci\n'
   'COPY src/ src/\n'
   'RUN npm run build\n'
   'FROM python:3.12-slim\n'
   'COPY requirements.txt .\n'
   'COPY --from=web /dist /app\n'
   'COPY . .\n',
   ['src/App.js']),
  {'stages': [('web', 'node:20'), ('1', 'python:3.12-slim')],
   'errors': [],
   'unused': [],
   'rebuilt': [4, 5, 8, 9]}),
 ('dockerfile_build_plan',
  ('FROM golang:1.22 AS build\n'
   'COPY go.mod go.sum ./\n'
   'RUN go mod download\n'
   'COPY . .\n'
   'FROM build AS test\n'
   'RUN go test ./...\n'
   'FROM alpine:3.20\n'
   'COPY --from=build /out/app /app\n'
   'COPY --from=3 /x /y\n',
   ['go.sum']),
  {'stages': [('build', 'golang:1.22'), ('test', 'build'), ('2', 'alpine:3.20')],
   'errors': ['рядок 9: --from=3 посилається на етап, якого ще немає'],
   'unused': ['test'],
   'rebuilt': [2, 3, 4, 8, 9]})]


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
    for name in ('dockerfile_build_plan',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
