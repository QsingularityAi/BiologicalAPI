from setuptools import setup, find_packages

setup(
    name="amplicon_analyzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'biopython>=1.79',
        'click>=8.0',
        'pandas>=1.3',
        'matplotlib>=3.4',
        'seaborn>=0.11',
        'pyyaml>=5.4',
        'tqdm>=4.65.0',
        'numpy>=1.21.0'
    ],
    entry_points={
        'console_scripts': [
            'analyze_amplicons=src.cli:main',
        ],
    },
    author="Anurag Trivedi",
    author_email="aanuragtrivedi007@gmail.com",
    description="Tool for detecting primer dimers and off-target amplification",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)