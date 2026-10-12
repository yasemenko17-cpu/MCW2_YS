"""Відкриті приклади 03 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(3)

PUBLIC = [('non_idempotent_tasks',
  ([{'name': 'Install nginx', 'ansible.builtin.apt': {'name': 'nginx', 'state': 'present'}},
    {'name': 'Init db', 'ansible.builtin.command': '/opt/init.sh'},
    {'name': 'Init once',
     'ansible.builtin.command': {'cmd': '/opt/init.sh', 'creates': '/var/lib/db'}},
    {'name': 'Report', 'ansible.builtin.shell': 'uptime', 'changed_when': False},
    {'ansible.builtin.shell': 'date > /tmp/d'}],),
  ['задача 2 «Init db»: command без creates/removes і без changed_when',
   'задача 5 «без назви»: shell без creates/removes і без changed_when']),
 ('non_idempotent_tasks',
  ([{'name': 'Seed', 'command': 'seed.sh', 'args': {'creates': '/seeded'}},
    {'name': 'Cleanup', 'shell': 'rm -f /tmp/x', 'args': {'removes': '/tmp/x'}},
    {'name': 'Poke', 'raw': 'echo hi'},
    {'name': 'Poke2', 'raw': 'echo', 'changed_when': False},
    {'name': 'Run script', 'script': './s.sh'}],),
  ['задача 3 «Poke»: raw без creates/removes і без changed_when',
   'задача 5 «Run script»: script без creates/removes і без changed_when'])]


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
    for name in ('non_idempotent_tasks',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
