"""Check the installation dependencies and report the version numbers of each.

This is meant to be used as an error diagnostic tool.
"""
__author__ = "Martin Blais <blais@furius.ca>"

import sys
import types


def list_dependencies(file=sys.stderr):
    """Check the dependencies and produce a listing on the given file.

    Args:
      file: A file object to write the output to.
    """
    print("Dependencies:")
    for package, version, sufficient in check_dependencies():
        print("   {:16}: {} {}".format(
            package,
            version or 'NOT INSTALLED',
            "(INSUFFICIENT)" if version and not sufficient else ""),
              file=file)


def check_dependencies():
    """Check the runtime dependencies and report their version numbers.

    Returns:
      A list of pairs of (package-name, version-number, sufficient) whereby if a
      package has not been installed, its 'version-number' will be set to None.
      Otherwise, it will be a string with the version number in it. 'sufficient'
      will be True if the version if sufficient for this installation of
      Beancount.
    """
    return [
        # Check for a complete installation of Python itself.
        check_python(),
        check_cdecimal(),

        # Modules we really do need installed.
        check_import('dateutil'),
        check_import('bottle'),
        check_import('ply', module_name='ply.yacc', min_version='3.4'),
        check_import('lxml', module_name='lxml.etree', min_version='3'),

        # Test are only required because of google-api-python-client.
        check_import('apiclient'),
        check_import('oauth2client'),
        ]


def check_python():
    """Check that Python 3.3 or above is installed.

    Returns:
      A triple of (package-name, version-number, sufficient) as per
      check_dependencies().
    """
    return ('python3',
            '.'.join(map(str, sys.version_info[:3])),
            sys.version_info[:2] >= (3, 3))


def is_fast_decimal(decimal_module):
    "Return true if a fast C decimal implementattion is installed."
    return isinstance(decimal_module.Decimal().sqrt, types.BuiltinFunctionType)


def check_cdecimal():
    """Check that Python 3.3 or above is installed.

    Returns:
      A triple of (package-name, version-number, sufficient) as per
      check_dependencies().
    """
    # Note: this code mirrors and should be kept in-sync with that at the top of
    # beancount.core.number.

    # Try the built-in installation.
    import decimal
    if is_fast_decimal(decimal):
        return ('cdecimal', '{} (built-in)'.format(decimal.__version__), True)

    # Try an explicitly installed version.
    try:
        import cdecimal
        if is_fast_decimal(cdecimal):
            return ('cdecimal', getattr(cdecimal, '__version__', 'OKAY'), True)
    except ImportError:
        pass

    # Not found.
    return ('cdecimal', None, False)


def check_import(package_name, min_version=None, module_name=None):
    """Check that a particular module name is installed.

    Args:
      package_name: A string, the name of the package and module to be
        imported to verify this works. This should have a __version__
        attribute on it.
      min_version: If not None, a string, the minimum version number
        we require.
      module_name: The name of the module to import if it differs from the
        package name.
    Returns:
      A triple of (package-name, version-number, sufficient) as per
      check_dependencies().
    """
    if module_name is None:
        module_name = package_name
    try:
        __import__(module_name)
        module = sys.modules[module_name]
        version = module.__version__
        assert isinstance(version, str)
        is_sufficient = version >= min_version if min_version else True
    except ImportError:
        version, is_sufficient = None, False
    return (package_name, version, is_sufficient)
