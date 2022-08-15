import os
import shutil
from pathlib import Path

import djclick as click

from supercharged.utils import configure_django_environ


@click.command()
def add_global_templates():

    configure_django_environ(os.getcwd())
    from django.apps import apps

    app_name = "global_templates"
    existing_app = [app for app in apps.get_app_configs() if app.name == app_name]
    if existing_app:
        raise SystemError("There is allready an app called %s" % app_name)

    from supercharged.themes import bootstrap

    base_html = os.path.join(
        os.path.split(bootstrap.__file__)[0], "templates", "base.html"
    )

    global_templates_path = os.path.join(os.getcwd(), app_name)
    os.makedirs(os.path.join(global_templates_path, "templates"))
    Path(os.path.join(global_templates_path, "__init__.py")).touch()
    shutil.copy(
        base_html, os.path.join(global_templates_path, "templates", "base.html")
    )
