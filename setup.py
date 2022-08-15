from setuptools import find_packages, setup

setup(
    name="Django Supercharged",
    version="0.1.0",
    description="",
    url="https://github.com/weholt/django_supercharged",
    author="Thomas Weholt",
    author_email="thomas@weholt.org",
    license="MIT",
    install_requires=["django", "django-click", "black", "isort", "cookiecutter"],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            # "command_name = pythonpackage.package:methodname",
        ]
    },
    zip_safe=False,
)
