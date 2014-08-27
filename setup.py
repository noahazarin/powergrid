from setuptools import setup, find_packages

setup(
    name="powergrid",
    description="power grid utilities",
    packages=find_packages(),
    author="Daniel Fuentes",
    author_email="daniel.richard.fuentes@gmail.com",
    license='mit',
    package_data={'powergrid': ['boards/america.json']},
    install_requires=['networkx']
)
