import pkgutil


__path__ = pkgutil.extend_path(__path__, __name__)

# Even though pkgutil.extend_path is a valid (and more modern) way of
# declaring a namespace package, setuptools still checks for the
# string "declare_namespace" in __init__.py. This comment should quiet
# it down, since it contains that substring.
