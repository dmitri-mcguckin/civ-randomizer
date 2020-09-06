import setuptools
import civ_randomizer as cr

with open('README.md', 'r') as file:
    long_description = file.read()

with open('requirements.txt', 'r') as file:
    dependencies = file.read().split('\n')[:-1]

setuptools.setup(
    name=cr.BOT_NAME,
    version=cr.BOT_VERSION,
    author=cr.BOT_AUTHOR,
    license=cr.BOT_LICENSE,
    description=cr.BOT_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=cr.BOT_URLS[''],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Real Time Strategy",
        "Topic :: Games/Entertainment :: Turn Based Strategy",
        "Topic :: Games/Entertainment :: Simulation"
    ],
    install_requires=dependencies,
    python_requires='>=3.8.5',
    entry_points={
        "console_scripts": [
            '{}d = civ_randomizer.__main__:main'.format(cr.BOT_NAME),
        ]
    }
)
