"""Assignment expression (``NamedExpr``) tests."""


from ast import NodeTransformer
from ast import parse
from unittest import TestCase

from RestrictedPython import compile_restricted
from RestrictedPython import safe_globals


class TestNamedExpr(TestCase):
    def test_works(self):
        code, gs = compile_str("if x:= x + 1: True\n")
        gs["x"] = 0
        exec(code, gs)
        self.assertEqual(gs["x"], 1)

    def test_no_private_target(self):
        with self.assertRaises(SyntaxError):
            compile_str("if _x_:= 1: True\n")

    def test_simple_only(self):
        # we test here that only a simple variable is allowed
        # as assignemt expression target
        # Currently (Python 3.8, 3.9), this is enforced by the
        # Python concrete syntax; therefore, some (``ast``) trickery is
        # necessary to produce a test for it.
        class TransformNamedExprTarget(NodeTransformer):
            def visit_NamedExpr(self, node):
                # this is brutal but sufficient for the test
                node.target = None
                return node

        mod = parse("if x:= x + 1: True\n")
        mod = TransformNamedExprTarget().visit(mod)
        with self.assertRaisesRegex(
                SyntaxError,
                "Assignment expressions are only allowed for simple target"):
            code, gs = compile_str(mod)


def compile_str(s, name="<unknown>"):
    """code and globals for *s*.

    *s* must be acceptable for ``compile_restricted`` (this is (especially) the
    case for an ``str`` or ``ast.Module``).

    *name* is a ``str`` used in error messages.
    """
    code = compile_restricted(s, name, 'exec')
    gs = safe_globals.copy()
    gs["__debug__"] = True  # assert active
    return code, gs
