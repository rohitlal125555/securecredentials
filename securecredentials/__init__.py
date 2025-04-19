from ._version import __version__
from .core import SecureCredentials

# noinspection PyProtectedMember
SecureCredentials._initialize()

__all__ = ["__version__"] + [attr for attr in dir(SecureCredentials) if not attr.startswith("_")]

def __getattr__(name):
    return getattr(SecureCredentials, name)

def __dir__():
    return __all__.copy()
