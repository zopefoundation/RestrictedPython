"""Every ast node has an explicit `visit_<node>` method.

"Explicit is better than implicit." (PEP 20)

RestrictedPython rejects every ast node without a `visit_<node>` method in
`RestrictingNodeTransformer.generic_visit`. That is the safety net for ast
nodes introduced by new Python versions. It is not the place where a decision
about a known language feature is recorded: each known node gets a
`visit_<node>` method which either allows it (with the necessary guards) or
denies it and explains why in its docstring.
"""
import ast
import sys

import pytest

from RestrictedPython import compile_restricted_exec
from RestrictedPython.transformer import RestrictingNodeTransformer


# Base classes which are never instantiated by the parser.
ABSTRACT_NODES = {
    'AST',
    'boolop',
    'cmpop',
    'excepthandler',
    'expr',
    'expr_context',
    'mod',
    'operator',
    'pattern',
    'slice',
    'stmt',
    'type_ignore',
    'type_param',
    'unaryop',
}

# Deprecated classes which the parser of the supported Python versions does
# not produce any more. They only exist for backwards compatibility.
DEPRECATED_NODES = {
    'AugLoad',
    'AugStore',
    'Bytes',
    'Ellipsis',
    'ExtSlice',
    'Index',
    'NameConstant',
    'Num',
    'Param',
    'Str',
    'Suite',
}


def concrete_ast_nodes():
    """Return the names of all ast nodes of the running Python version."""
    return sorted(
        name for name in dir(ast)
        if not name.startswith('_')
        and isinstance(getattr(ast, name), type)
        and issubclass(getattr(ast, name), ast.AST)
        and name not in ABSTRACT_NODES | DEPRECATED_NODES
    )


def test_explicit_deny__1():
    """Every ast node of the running Python has a `visit_<node>` method.

    If this test fails after adding a new Python version, read the section
    "Preparations for a new Python version" in the contributing documentation
    and add a `visit_<node>` method for each listed node.
    """
    missing = [
        name for name in concrete_ast_nodes()
        if not hasattr(RestrictingNodeTransformer, f'visit_{name}')
    ]
    assert missing == []


def assert_denied(source, node_name, lineno):
    """Assert `source` is denied by an explicit `visit_<node_name>`.

    An explicit `visit_<node>` method does not emit the warning about an
    unknown node which `generic_visit` emits.
    """
    result = compile_restricted_exec(source)
    assert result.errors == (
        f'Line {lineno}: {node_name} statements are not allowed.',)
    assert result.warnings == []
    assert result.code is None


MATCH_EXAMPLE = """\
match command:
    case 'go':
        pass
"""


def test_explicit_deny__Match__1():
    """It denies the `match` statement."""
    assert_denied(MATCH_EXAMPLE, 'Match', 1)


def test_explicit_deny__AnnAssign__1():
    """It denies annotated assignments."""
    assert_denied('x: int = 1', 'AnnAssign', 1)


def test_explicit_deny__AnnAssign__2():
    """It denies annotated assignments without a value."""
    assert_denied('x: int', 'AnnAssign', 1)


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='The `type` statement is new in Python 3.12.')
def test_explicit_deny__TypeAlias__1():
    """It denies the `type` statement."""
    assert_denied('type Alias = int', 'TypeAlias', 1)


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='Type parameter lists are new in Python 3.12.')
def test_explicit_deny__TypeVar__1():
    """It denies type variables in type parameter lists."""
    assert_denied('def func[T](arg):\n    return arg\n', 'TypeVar', 1)


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='Type parameter lists are new in Python 3.12.')
def test_explicit_deny__ParamSpec__1():
    """It denies parameter specifications in type parameter lists."""
    assert_denied('class Box[**P]:\n    pass\n', 'ParamSpec', 1)


@pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='Type parameter lists are new in Python 3.12.')
def test_explicit_deny__TypeVarTuple__1():
    """It denies type variable tuples in type parameter lists."""
    assert_denied('def func[*Ts]():\n    pass\n', 'TypeVarTuple', 1)


def test_explicit_deny__TypeIgnore__1():
    """It denies `# type: ignore` comments of a pre-parsed ast.

    The parser only creates `TypeIgnore` nodes if it is asked to keep type
    comments, which RestrictedPython never does. A pre-parsed ast passed in
    by the caller can contain them, though.
    """
    tree = ast.parse('x = 1  # type: ignore\n', type_comments=True)
    result = compile_restricted_exec(tree)
    assert result.errors == ('Line 1: TypeIgnore statements are not allowed.',)
    assert result.warnings == []
    assert result.code is None


# Contains each pattern node at least once.
ALL_PATTERNS_EXAMPLE = """\
match subject:
    case 1:
        pass
    case None:
        pass
    case [first, *rest]:
        pass
    case {'key': value}:
        pass
    case Point(x=0):
        pass
    case 1 | 2:
        pass
"""


def find_node(tree, node_name):
    """Return the first node of type `node_name` in `tree`."""
    node_type = getattr(ast, node_name)
    return next(node for node in ast.walk(tree) if isinstance(node, node_type))


# Nodes which only exist inside of an already denied `Match` node. They are
# never reached from source code but have an explicit `visit_<node>` method
# nevertheless.
PATTERN_NODES = [
    'MatchAs',
    'MatchClass',
    'MatchMapping',
    'MatchOr',
    'MatchSequence',
    'MatchSingleton',
    'MatchStar',
    'MatchValue',
    'match_case',
]


@pytest.mark.parametrize('node_name', PATTERN_NODES)
def test_explicit_deny__patterns__1(node_name):
    """It denies the nodes of the `match` statement one by one."""
    node = find_node(ast.parse(ALL_PATTERNS_EXAMPLE), node_name)
    transformer = RestrictingNodeTransformer()
    transformer.visit(node)
    # `match_case` has no position.
    lineno = getattr(node, 'lineno', None)
    assert transformer.errors == [
        f'Line {lineno}: {node_name} statements are not allowed.']
    assert transformer.warnings == []


def test_explicit_deny__FunctionType__1():
    """It denies function type signatures.

    They are only created by `ast.parse(mode='func_type')`.
    """
    tree = ast.parse('(int, str) -> bool', mode='func_type')
    transformer = RestrictingNodeTransformer()
    transformer.visit(tree)
    assert transformer.errors == [
        'Line None: FunctionType statements are not allowed.']
    assert transformer.warnings == []


# The following tests document the reasons given in the docstrings of the
# `visit_<node>` methods: they allow a denied node and show which guard or
# check it bypasses. If one of them fails for a new Python version, the
# corresponding docstring needs a review.


class AllowPatternMatching(RestrictingNodeTransformer):
    """Transformer which allows the `match` statement for the tests."""


for _node_name in ['Match', *PATTERN_NODES]:
    setattr(
        AllowPatternMatching,
        f'visit_{_node_name}',
        RestrictingNodeTransformer.node_contents_visit)


def recording_globals(calls):
    """Return globals with guards recording their calls into `calls`.

    The tests show that the guards are bypassed, so they are never called.
    """
    def _getattr_(ob, name):  # pragma: no cover
        calls.append(('_getattr_', name))
        return getattr(ob, name)

    def _getitem_(ob, key):  # pragma: no cover
        calls.append(('_getitem_', key))
        return ob[key]

    def _getiter_(ob):  # pragma: no cover
        calls.append(('_getiter_',))
        return iter(ob)

    return {
        '__builtins__': {},
        '_getattr_': _getattr_,
        '_getitem_': _getitem_,
        '_getiter_': _getiter_,
    }


def run_allowed(source, **kw):
    """Run `source` with pattern matching allowed.

    Return the globals and the recorded guard calls.
    """
    result = compile_restricted_exec(source, policy=AllowPatternMatching)
    assert result.errors == ()
    calls = []
    glb = recording_globals(calls)
    glb.update(kw)
    exec(result.code, glb)
    return glb, calls


class Point:
    __match_args__ = ('x',)
    x = 'secret'


def test_explicit_deny__MatchClass__reason__1():
    """A class pattern reads attributes without calling `_getattr_`."""
    glb, calls = run_allowed(
        'match point:\n'
        '    case Point(x=value):\n'
        '        result = value\n',
        point=Point(), Point=Point)
    assert glb['result'] == 'secret'
    assert calls == []


def test_explicit_deny__MatchClass__reason__2():
    """Positional class patterns use `__match_args__` without `_getattr_`."""
    glb, calls = run_allowed(
        'match point:\n'
        '    case Point(value):\n'
        '        result = value\n',
        point=Point(), Point=Point)
    assert glb['result'] == 'secret'
    assert calls == []


def test_explicit_deny__MatchSequence__reason__1():
    """A sequence pattern iterates without calling `_getiter_`."""
    glb, calls = run_allowed(
        'match seq:\n'
        '    case [first, *rest]:\n'
        '        result = (first, rest)\n',
        seq=[1, 2, 3])
    assert glb['result'] == (1, [2, 3])
    assert calls == []


def test_explicit_deny__MatchMapping__reason__1():
    """A mapping pattern reads items without calling `_getitem_`."""
    glb, calls = run_allowed(
        'match mapping:\n'
        "    case {'key': value, **rest}:\n"
        '        result = (value, rest)\n',
        mapping={'key': 1, 'other': 2})
    assert glb['result'] == (1, {'other': 2})
    assert calls == []


@pytest.mark.parametrize('pattern', [
    '_secret',
    '[*_secret]',
    '{**_secret}',
    'x as _secret',
])
def test_explicit_deny__MatchAs__reason__1(pattern):
    """Names bound by patterns escape the check for a leading `_`."""
    result = compile_restricted_exec(
        f'match subject:\n    case {pattern}:\n        pass\n',
        policy=AllowPatternMatching)
    assert result.errors == ()
    assert result.code is not None


def test_explicit_deny__MatchValue__reason__1():
    """A guarded attribute lookup is not a valid value pattern."""
    with pytest.raises(ValueError) as err:
        compile_restricted_exec(
            'match subject:\n    case obj.attr:\n        pass\n',
            policy=AllowPatternMatching)
    assert 'patterns may only match literals and attribute lookups' in str(
        err.value)
