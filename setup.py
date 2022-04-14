from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The lines below can be parsed by `docs/conf.py`.
name = "oprfs"
version = "0.1.0"

setup(
    name=name,
    version=version,
    packages=[name,],
    install_requires=["bcl>=0.1.1", "oprf>=1.0.0"],
    license="MIT",
    url="https://github.com/nthparty/oprfs",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Oblivious pseudo-random function (OPRF) service for obtaining "+\
                "a persistent mask and applying that mask to private data.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
