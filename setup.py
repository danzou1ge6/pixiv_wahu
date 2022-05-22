from setuptools import setup


setup(
    name='pixiv_wahu',
    version='0.0.2',
    python_requires='>=3.10',
    package_dir={
        'wahu_backend': 'wahu_backend',
        'wahu_frontend': 'dist/wahu_frontend',
        'token_getter': 'dist_stuff/token_getter'
    },
    install_requires=[
        'click',
        'aiohttp',
        'fuzzywuzzy[accelerate_fuzzywuzzy]',
        'toml'
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
            'pixiv-wahu=wahu_backend:pixiv_wahu_run',
            'get-px-refreshtoken=token_getter:main'
        ]
    }
)
