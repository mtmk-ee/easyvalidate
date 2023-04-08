

class DecorationError(Exception):
    """The decorator was applied to an invalid target.
    """


class ValidationError(Exception):
    """A validation condition was not met.
    """


# =======================================================
class ExpressionError(ValidationError):
    """There was a problem evaluating an expression.
    """


# =======================================================
class AccessError(ValidationError):
    """
    """

class PrivateAccessError(AccessError):
    """
    """

class ProtectedAccessError(AccessError):
    """
    """
