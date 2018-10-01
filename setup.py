#!/usr/bin/env python
import re
import os
from setuptools import setup, find_packages

try:
    # For pip >= 10.
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:
    # For pip <= 9.0.3.
    from pip.req import parse_requirements
    from pip.download import PipSession

install_reqs = parse_requirements('./requirements.txt', session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]


# Get version
# with open(os.path.join('lambda_grpc', 'consts.py'), 'rt') as consts_file:
#     version = re.search(r'__version__ = \'(.*?)\'', consts_file.read()).group(1)
version = '1.0.0'

PYTHON_STEM = os.path.join('src', 'python', 'lambda-grpc')

PACKAGES = list(find_packages(PYTHON_STEM))
PACKAGES_DIRECTORIES = {
    '': PYTHON_STEM,
}
setup(
    name='lambda-grpc',
    version=version,
    description='Enables running a gRPC server on AWS Lambda',
    author='Gal Bashan',
    author_email='galbashan1@gmail.com',
    url='https://github.com/galbash/lambda-grpc',
    packages=PACKAGES,
    package_dir=PACKAGES_DIRECTORIES,
    install_requires=reqs,
    license="MIT License",
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    keywords=['serverless', 'microservices', 'lambda', 'rpc'],
    classifiers=(
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    )
)
