from setuptools import setup, find_packages

setup(
    name="focusguard",
    version="1.0.0",
    description="Cross-Platform Website and Application Blocking Desktop Software",
    author="FocusGuard Team",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "focusguard": [
            "resources/block_page/*",
            "resources/icons/*",
        ]
    },
    install_requires=[
        "PySide6>=6.5.0",
        "psutil>=5.9.0",
    ],
    entry_points={
        "console_scripts": [
            "focusguard=focusguard.main:main",
        ],
    },
    python_requires=">=3.8",
)
