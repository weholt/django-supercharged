#!/usr/bin/env python
import os
from pathlib import Path

import djclick as click
from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter

from supercharged.utils import camelcase2snakecase, configure_django_environ


@click.command()
@click.argument("app_name")
def startbigapp(app_name):

    configure_django_environ(os.getcwd())
    from django.apps import apps

    existing_app = [app for app in apps.get_app_configs() if app.name == app_name]
    if existing_app:
        raise SystemError("There is allready an app called %s" % app_name)

    root_path = Path(os.path.split(__file__)[0])
    recipe_folder = root_path / "cookiecutter_recipes" / "bigapp"

    if not os.path.exists(recipe_folder):
        raise SystemError(
            "Folder for cookiecutter-recipes not found at %s" % recipe_folder
        )
    try:
        extra_context = {
            "app_name": app_name,
            "snake_case_app_name": camelcase2snakecase(app_name),
        }
        cookiecutter(
            str(recipe_folder), None, no_input=True, extra_context=extra_context
        )
    except OutputDirExistsException:
        print("There is allready an app with that name")
