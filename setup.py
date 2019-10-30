"""
Setup module.
"""
from setuptools import setup

from markdownreveal import __version__

setup(
    name='markdownreveal',
    version=__version__,
    description='Create presentations with simple Markdown notation',
    long_description="""This tool allows you to create and visualize
        presentations with simple Markdown notation. It is based on
        reveal.js and is able to generate the required HTML and refresh
        your browser view for easier and faster presentation creation.""",
    url='https://github.com/markdownreveal/markdownreveal',
    author='Miguel Sánchez de León Peque',
    author_email='peque@neosit.es',
    license='BSD License',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords='markdown reveal reveal.js presentation',
    entry_points={
        'console_scripts': [
            'mdr = markdownreveal.commands:cli',
            'markdownreveal = markdownreveal.commands:cli',
        ]
    },
    packages=['markdownreveal'],
    package_data={'markdownreveal': ['config.template.yaml']},
    install_requires=[
        'PyYAML>=5.1',
        'requests',
        'pypandoc',
        'livereload',
        'watchdog',
        'click',
        'click_default_group',
    ],
    extras_require={
        'dev': [],
        'test': ['tox'],
        'docs': ['sphinx', 'numpydoc', 'sphinx_rtd_theme'],
    },
)
