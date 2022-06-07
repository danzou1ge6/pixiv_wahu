from setuptools import setup


setup(
    name='pixiv_wahu',
    version='0.2.4',
    python_requires='>=3.10',
    package_dir={
        'wahu_backend': 'wahu_backend',
        'wahu_frontend': 'dist/wahu_frontend',
        'wahu_cli': 'wahu_cli',
        'token_getter': 'token_getter'
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
        'token_getter': ['*.html']
    },
    entry_points={
        'console_scripts': [
            'pixiv-wahu=wahu_backend:run',
            'get-px-refreshtoken=token_getter:main'
        ]
    }
)
