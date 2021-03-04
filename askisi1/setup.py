from setuptools import setup

setup(
    name="askisi1",
    version="0.1.0",
    packages=["askisi1"],
    entry_points={
        "console_scripts": [
            "askisi1 = askisi1.__main__:main"
        ]
    },
)