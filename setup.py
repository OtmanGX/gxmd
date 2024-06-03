from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='gxmd',
    version='0.1.4a',
    packages=find_packages(),
    license='GPL v3.0',
    author='BENAYAD OTMANE',
    author_email='otmangx@gmail.com',
    python_requires=">=3.6",
    url='https://github.com/OtmanGX/gxmd',
    project_urls={
        "Source": "https://github.com/OtmanGX/gxmd",
    },
    description='Manga downloader',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    keywords="manga,downloader",
    classifiers=[
        'Environment :: Console',
        'Topic :: Manga :: Network :: FileTransfer',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'gxmd = gxmd.cli:main_cli',
        ],
    },
    install_requires=requirements,
    package_data={'gxmd': ['data/selectors.json']},
    include_package_data=True
)
