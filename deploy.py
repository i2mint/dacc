"""Manual build-and-upload helper: ``python deploy.py`` builds and uploads to PyPI.

Importing this module does nothing (so test collection, e.g.
``pytest --doctest-modules``, can never trigger a build or an upload).
"""

import subprocess


def deploy():
    """Build sdist/wheel and upload them to PyPI with twine."""
    # TODO: Both of these are python. Change to use python objects directly.
    print("--------------------------- setup_output ---------------------------")
    subprocess.run("python setup.py sdist bdist_wheel".split(" "), check=True)

    print("--------------------------- upload_output ---------------------------")
    subprocess.run("python -m twine upload dist/*".split(" "), check=True)


if __name__ == "__main__":
    deploy()
