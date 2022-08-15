import json
import pprint

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import models
from pyexpat import model


def model_name(model):
    return "%s.%s" % (model._meta.app_label, model._meta.object_name)


class Command(BaseCommand):
    """
    ...
    """

    help = "Checks constraints in the database and reports violations on stdout"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--json-filename",
            action="append",
            type=str,
            dest="json_file",
            help="A JSON source file to migrate",
        )
        parser.add_argument(
            "-s",
            "--source-app",
            action="append",
            type=str,
            dest="source",
            help="Which app is source for migration",
        )
        parser.add_argument(
            "-t",
            "--target-app",
            action="append",
            type=str,
            dest="target",
            help="Which app is target for migration",
        )
        parser.add_argument(
            "-m",
            "--target-model",
            action="append",
            type=str,
            dest="target_model",
            help="Which model is target for migration",
        )
        parser.add_argument(
            "-i",
            "--ignore-fields",
            action="append",
            type=str,
            dest="ignore_fields",
            help="Which fields to ignore for migration",
        )
        parser.add_argument(
            "-r",
            "--remap-field-values",
            action="append",
            type=str,
            dest="remapped_field_values",
            help="Replace a field with a custom value",
        )
        parser.add_argument(
            "-e",
            "--exclude-duplicates",
            action="append",
            type=str,
            dest="exclude_duplicates",
            help="Indicates we skip any existing records with the same data",
        )

    def handle(self, *args, **options):
        def is_float(element: str) -> bool:
            try:
                return float(element)
                return True
            except ValueError:
                return False

        def get_model(app_name, target_model):
            for modelclass in apps.get_models():
                if (
                    modelclass._meta.app_label == app_name
                    and modelclass._meta.model_name == target_model
                ):
                    return modelclass

        source_file = (
            options.get("json_file", None) and options.get("json_file", None)[0]
        )
        source_app = options.get("source", None) and options.get("source", None)[0]
        target_app = options.get("target", None) and options.get("target", None)[0]
        target_model = (
            options.get("target_model", None) and options.get("target_model", None)[0]
        )
        if not source_file and not source_app and not target_app:
            raise Exception(
                "Missing json file, target and source app. Cannot continue."
            )

        # optional options ;-)
        ignore_fields = options.get("ignore_fields", "") and [
            s.strip() for s in options.get("ignore_fields", None)[0].split(",")
        ]
        exclude_duplicates = (
            options.get("exclude_duplicates", None)
            and options.get("exclude_duplicates", None)[0]
        )
        remapped = options.get("remapped_field_values", "") and [
            s.strip() for s in options.get("remapped_field_values", None)[0].split(",")
        ]
        remapped_field_values = {}
        if remapped:
            for field_name, value in [v.split("=") for v in remapped]:
                if value.isnumeric():
                    remapped_field_values[field_name] = int(value)
                elif is_float(value):
                    remapped_field_values[field_name] = float(value)
                else:
                    remapped_field_values[field_name] = value

        result = []
        with open(source_file, encoding="utf8") as f:
            data = json.load(f)
            for section in data:
                app_name, model_name = section.get("model").split(".")
                if not source_app == app_name:
                    continue

                model = get_model(target_app, model_name)
                if not model:
                    continue

                if target_model and model._meta.model_name != target_model:
                    continue

                target_fields = {}
                source_fields = section.get("fields")
                for target_field in model._meta.fields:
                    if target_field.name in source_fields:
                        if target_field.name in remapped_field_values:
                            target_fields[target_field.name] = remapped_field_values[
                                target_field.name
                            ]

                        elif not target_field.name in ignore_fields:
                            target_fields[target_field.name] = source_fields[
                                target_field.name
                            ]

                if exclude_duplicates:
                    filter_values = {}
                    for target_field in target_fields:
                        if not target_field in remapped_field_values:
                            filter_values[target_field] = target_fields[target_field]

                    if model.objects.filter(**filter_values).count():
                        continue

                result.append(
                    {
                        "model": "%s.%s" % (target_app, model_name),
                        "fields": target_fields,
                    }
                )

        print(json.dumps(result))
