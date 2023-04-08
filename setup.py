import os
import setuptools


CODE_ROOT = os.path.dirname(os.path.abspath(__file__))
PACKAGE_ROOT = os.path.join(CODE_ROOT, 'easyvalidate')
VERSION_FILE = os.path.join(PACKAGE_ROOT, 'version.py')


def run_setup():
    setuptools.setup(
        name="easyvalidate",
        version=get_package_version(),
        author="Mitchell Matsumori-Kelly",
        description="Validation utilities",
        long_description=_readme(),
        long_description_content_type="text/markdown",
        python_requires=">=3.8",
        url="https://github.com/mtmk-ee/easyvalidate",
        install_requires=[],
        packages=setuptools.find_packages(),
    )

def _readme() -> str:
    with open('README.md') as f:
        return f.read()


def get_package_version() -> str:
    """Get version string for the package.

    Executes `version.py` and grabs `__version__`.
    """
    globals = {}
    try:
        with open(VERSION_FILE, 'r') as f:
            exec(f.read(), globals)
    except FileNotFoundError as e:
        raise FileNotFoundError('Version file could not be located') from e
    except OSError as e:
        raise OSError('Failed to read the the version file') from e
    except Exception:
        raise

    try:
        return globals['__version__']
    except KeyError:
        raise KeyError('Version string cannot be found in version file')


run_setup()
