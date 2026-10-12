"""Відкриті приклади 05 (з картки). Повний набір перевірок — у викладача."""
import copy

import pytest
from conftest import load

M = load(5)

PUBLIC = [('plan_summary',
  ([{'address': 'docker_network.app', 'type': 'docker_network', 'actions': ['create']},
    {'address': 'docker_image.web', 'type': 'docker_image', 'actions': ['update']},
    {'address': 'docker_container.web',
     'type': 'docker_container',
     'actions': ['delete', 'create']},
    {'address': 'docker_volume.data', 'type': 'docker_volume', 'actions': ['delete']},
    {'address': 'local_file.cfg', 'type': 'local_file', 'actions': ['no-op']},
    {'address': 'data.local_file.x', 'type': 'local_file', 'actions': ['read']}],
   ('docker_volume',)),
  {'add': 2,
   'change': 1,
   'destroy': 2,
   'replace': ['docker_container.web'],
   'blocked': ['docker_volume.data'],
   'by_type': {'docker_container': {'add': 1, 'change': 0, 'destroy': 1},
               'docker_image': {'add': 0, 'change': 1, 'destroy': 0},
               'docker_network': {'add': 1, 'change': 0, 'destroy': 0},
               'docker_volume': {'add': 0, 'change': 0, 'destroy': 1}},
   'line': 'Plan: 2 to add, 1 to change, 2 to destroy.'}),
 ('plan_summary',
  ([{'address': 'a.x', 'type': 'a', 'actions': ['no-op']},
    {'address': 'b.y', 'type': 'b', 'actions': ['read']}],),
  {'add': 0,
   'change': 0,
   'destroy': 0,
   'replace': [],
   'blocked': [],
   'by_type': {},
   'line': 'No changes.'})]


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
    for name in ('plan_summary',):
        assert callable(getattr(M, name, None)), f"немає функції {name}"
