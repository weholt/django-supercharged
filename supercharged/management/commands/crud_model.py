import os
import pprint
import shutil
from pathlib import Path

import djclick as click

from supercharged.utils import (
    Field,
    camelcase2snakecase,
    configure_django_environ,
    create_content,
)


@click.argument("model_name")
@click.argument("app_name")
@click.option("--field", "-f", multiple=True)
@click.option("--stubbs", "-s")
@click.option("--base_html", "-b")
@click.command()
def crud_model(app_name, model_name, field=None, stubbs=None, base_html=None):
    """
    Will create a model, including views, templates and urlpatterns, for a given app.
    """
    snake_case_model_name = camelcase2snakecase(model_name)
    fields = field and [Field(field) for field in field] or []

    date_hierarchy_field = next(
        (x.name for x in fields if x.date_field),
        None,
    )

    searchable_fields = [f.name for f in fields if f.searchable]
    filter_fields = [f.name for f in fields if f.filter_field]

    context = {
        "custom_id": "id" in fields,
        "app_name": app_name,
        "model_name": model_name,
        "snake_case_model_name": snake_case_model_name,
        "fields": fields,
        "date_hierarchy_field": date_hierarchy_field,
        "searchable_fields": searchable_fields,
        "filter_fields": filter_fields,
    }

    if not model_name.isalnum():
        raise SystemError("Model names can only be alphanumeric characters.")

    stubb_base = Path(os.path.split(__file__)[0]) / "stubbs"

    configure_django_environ(os.getcwd())
    from django.apps import apps

    existing_app = [app for app in apps.get_app_configs() if app.name == app_name]
    if not existing_app:
        raise SystemError("No app called %s" % app_name)

    app = existing_app[0]
    if model_name in [model.__name__ for model in app.get_models()]:
        raise SystemError(f"App {app_name} allready has a model called {model_name}.")

    models_folder = os.path.join(app.path, "models")
    if not os.path.exists(models_folder):
        raise SystemError(
            f"{app_name} does not have a models package. This is required."
        )

    model_file = os.path.join(models_folder, snake_case_model_name, ".py")
    if os.path.exists(model_file):
        raise SystemError(f"{app_name} allready has a model file for {model_name}.")

    views_folder = os.path.join(app.path, "views")
    if not os.path.exists(views_folder):
        raise SystemError(
            f"{app_name} does not have a views package. This is required."
        )

    view_file = os.path.join(views_folder, snake_case_model_name, ".py")
    if os.path.exists(view_file):
        raise SystemError(f"{app_name} allready has a view file for {model_name}.")

    urls_file = os.path.join(app.path, "urls.py")
    if not os.path.exists(urls_file):
        raise SystemError(f"{app_name} does not have a urls.py file. This is required.")

    admin_file = os.path.join(app.path, "admin.py")
    if not os.path.exists(admin_file):
        raise SystemError(
            f"{app_name} does not have a admin.py file. This is required."
        )

    stubbs_available = [f for f in os.listdir(stubb_base) if os.path.isdir(f)]
    if stubbs and stubbs not in stubbs_available:
        raise SystemError("Unknown stubb selected (%s)." % stubbs)

    stubbs_folder = os.path.join(stubb_base, stubbs or "default")

    if not os.path.exists(stubbs_folder):
        raise SystemError("Missing expected subbs-folder at %s" % stubbs_folder)

    model_stubb = open(os.path.join(stubbs_folder, "model.py")).read()
    create_content(
        model_stubb,
        os.path.join(models_folder, "%s.py" % snake_case_model_name),
        context,
    )

    view_stubb = open(os.path.join(stubbs_folder, "views.py")).read()
    create_content(
        view_stubb,
        os.path.join(views_folder, "%s.py" % snake_case_model_name),
        context,
    )

    url_stubb = open(os.path.join(stubbs_folder, "urls.py")).read()
    create_content(url_stubb, urls_file, context, append=True)

    admin_stubb = open(os.path.join(stubbs_folder, "admin.py")).read()
    create_content(admin_stubb, admin_file, context, append=True)

    api_folder = os.path.join(app.path, "api")
    if os.path.exists(api_folder):
        api_stubb = open(os.path.join(stubbs_folder, "api.py")).read()
        create_content(
            api_stubb,
            os.path.join(api_folder, "%s.py" % snake_case_model_name),
            context,
        )

    source_template_folder = os.path.join(stubbs_folder, "templates")
    target_template_folder = os.path.join(
        app.path, "templates", app_name, snake_case_model_name
    )

    if not os.path.exists(target_template_folder):
        os.makedirs(target_template_folder)

    base_html_filename = os.path.join(source_template_folder, base_html or "base.html")
    if not os.path.exists(base_html_filename):
        raise SystemError("Base html specified as '%s' does not exist." % base_html)

    if not os.path.exists(os.path.join(app.path, "templates", "base.html")):
        shutil.copy(
            base_html_filename,
            os.path.join(app.path, "templates", "base.html"),
        )

    for filename in [
        "create.html",
        "delete.html",
        "detail.html",
        "list.html",
        "update.html",
    ]:
        if not os.path.exists(os.path.join(target_template_folder, filename)):
            create_content(
                open(os.path.join(source_template_folder, filename)).read(),
                os.path.join(target_template_folder, filename),
                context,
            )

    print("-" * 80)
    print("BUILD CONTEXT:")
    pprint.pprint(context)
    print("\n")

    print("Reformatting and fixing code ....\n")
    os.chdir(app.path)
    os.system("black .")
    os.system("isort --atomic .")
