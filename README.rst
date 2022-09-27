=====
oprfs
=====

Easy-to-deploy oblivious pseudo-random function (OPRF) service that allows other parties (typically participants in some secure multi-party computation protocol) to maintain a persistent mask which they cannot decrypt but which they can safely apply (via requests to the service) to private data values of their choice.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/oprfs.svg
   :target: https://badge.fury.io/py/oprfs
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/oprfs/badge/?version=latest
   :target: https://oprfs.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/nthparty/oprfs/workflows/lint-test-cover-docs/badge.svg
   :target: https://github.com/nthparty/oprfs/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/nthparty/oprfs/badge.svg?branch=main
   :target: https://coveralls.io/github/nthparty/oprfs?branch=main

Purpose
-------
This library makes it possible to deploy a service that allows other parties to request an encrypted mask (which they cannot decrypt themselves but the service can decrypt) for an oblivious `pseudo-random function <https://en.wikipedia.org/wiki/Pseudorandom_function_family>`__ (OPRF) protocol. Those other parties can then ask the service to apply the mask to their own private, encrypted data values (which the service cannot decrypt). Thanks to the underlying `oblivious <https://pypi.org/project/oblivious>`__ library, method implementations rely on cryptographic primitives found within the `libsodium <https://github.com/jedisct1/libsodium>`__ library.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/oprfs>`__::

    python -m pip install oprfs

The library can be imported in the usual ways::

    import oprfs
    from oprfs import *

Deployment Example: HTTP Server and Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Below is in illustration of how an instance of the OPRF service might be deployed using `Flask <https://flask.palletsprojects.com>`__::

    import oprfs
    import flask
    app = flask.Flask(__name__)

    # Normally, a persistent key should be retrieved from secure storage.
    # Here, a new key is created each time so older masks cannot be reused
    # once the service is restarted.
    key = oprfs.key()

    @app.route('/', methods=['POST'])
    def endpoint():
        # Call the handler with the key and request, then return the response.
        return flask.jsonify(oprfs.handler(key, flask.request.get_json()))

    app.run()

.. |point| replace:: ``point``
.. _point: https://oblivious.readthedocs.io/en/6.0.0/_source/oblivious.ristretto.html#oblivious.ristretto.point

Once an instance of the above service is running, a client might interact with it as illustrated in the example below. Note the use of the distinct `oprf <https://pypi.org/project/oprf>`__ library to represent a data instance (which is itself a wrapper for an `Ed25519 <https://ed25519.cr.yp.to>`__ group element as represented by an instance of the |point|_ class in the `oblivious <https://pypi.org/project/oblivious>`__ library)::

    import json
    import requests
    import oprf

    # Request an encrypted mask.
    response = requests.post('http://localhost:5000', json={})
    mask_encrypted = json.loads(response.text)['mask'][0]

    # Mask some data.
    data = oprf.data.hash('abc').to_base64()
    response = requests.post(
        'http://localhost:5000',
        json={'mask': [mask_encrypted], 'data': [data]}
    )
    data_masked = oprf.data.from_base64(json.loads(response.text)['data'][0])

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__::

    python -m pip install .[docs,lint]

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__::

    python -m pip install .[docs]
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details)::

    python -m pip install .[test]
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__::

    python src/oprfs/oprfs.py -v

Style conventions are enforced using `Pylint <https://pylint.pycqa.org>`__::

    python -m pip install .[lint]
    python -m pylint src/oprfs

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/nthparty/oprfs>`__ for this library.

Versioning
^^^^^^^^^^
The version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/oprfs>`__ by a package maintainer. First, install the dependencies required for packaging and publishing::

    python -m pip install .[publish]

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions. Create and push a tag for this version (replacing ``?.?.?`` with the version number)::

    git tag ?.?.?
    git push origin ?.?.?

Remove any old build/distribution files. Then, package the source into a distribution archive::

    rm -rf build dist src/*.egg-info
    python -m build --sdist --wheel .

Finally, upload the package distribution archive to `PyPI <https://pypi.org>`__::

    python -m twine upload dist/*
