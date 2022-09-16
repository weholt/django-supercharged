#!/usr/bin/env python
import os
import time

import djclick as click
from django.conf import settings
from django.core.management import call_command


@click.command()
def backup_sqlite3_media():
    import tarfile

    backup_folder = os.path.join(os.getcwd(), "backups")
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    print("\nDumping all data to json ...")
    json_dumpdata = os.path.join(os.getcwd(), "db_dump_%s.json" % int(time.time()))
    output = open(json_dumpdata, "w")
    call_command("dumpdata", format="json", indent=3, stdout=output)
    output.close()
    print("done")

    print("\nBacking up db.sqlite3 ...")
    tar = tarfile.open(
        os.path.join(backup_folder, "backup_%s.tar" % int(time.time())), "w"
    )
    tar.add(os.path.join(os.getcwd(), "db.sqlite3"), arcname="db.sqlite3")
    print("done.")

    print("\nBacking up dumpdata.json ...")
    tar.add(json_dumpdata, arcname="dumpdata.json")
    print("done")

    print("\nBacking up media folder ....")
    for image in os.listdir(settings.MEDIA_ROOT):
        tar.add(
            os.path.join(settings.MEDIA_ROOT, image),
            arcname="media%s%s" % (os.sep, image),
        )
    tar.close()
    print("done")

    os.remove(json_dumpdata)
