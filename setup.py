from setuptools import setup


setup(
    name='pixiv_wahu',
    version='0.2.5',
    python_requires='>=3.10',
    package_dir={
        'wahu_backend': 'wahu_backend',
        'wahu_frontend': 'dist/wahu_frontend',
        'wahu_cli': 'wahu_cli',
        'wahu_guilauncher': 'wahu_guilauncher'
    },
    install_requires=[
        'click',
        'aiohttp',
        'fuzzywuzzy[accelerate_fuzzywuzzy]',
        'toml',
        'prettytable'
    ],
    extras_require={
        'accelerate_fuzzywuzzy': ['python-levenshtein']
    },
    package_data={
        'wahu_frontend': ['*', 'assets/*'],
    },
    entry_points={
        'console_scripts': [
            'pixiv-wahu=wahu_backend:run',
            'wahu-gui=wahu_guilauncher:main'
        ]
    }
)
