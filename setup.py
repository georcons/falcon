from setuptools import setup, find_packages

setup(
    name = 'falcon',
    version = "1.1.0",
    author = 'Nikolay Georgiev',
    description = 'A heavily customizable Python package serving as a wrapper and a pipeline for parsing mathematical problems to LLMs.',
    packages = find_packages(),
    install_requires = ["openai>=1.58.1", "together>=1.4.0", "datasets>=3.1.0"]
)
