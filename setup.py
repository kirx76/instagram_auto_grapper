from setuptools import find_packages
from setuptools import setup

setup(
    name='instagram_auto_grapper',
    description="Simple web app for test CI",
    author='kirx76',
    url='',
    packages=find_packages('src'),
    package_dir={
        '': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'web_server = app:main']},
)
