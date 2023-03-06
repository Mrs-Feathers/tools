"""
diary

in my terminal, `diary` is aliased to this script so I can easily create, edit,
and save a new diary entry (stored in my cloud provider as a markdown file)
"""
import os
import tempfile
import datetime
from sys import argv
from subprocess import call
from cabinet import cabinet

EDITOR = os.environ.get('EDITOR', 'vim')
PATH_DIARY = cabinet.get("path", "diary")
PATH_NOTES_LOCAL = cabinet.get('path', 'notes', 'local')
PATH_NOTES_CLOUD = cabinet.get('path', 'notes', 'cloud')
FILENAME = f"{PATH_DIARY}/{datetime.datetime.now().strftime('%Y %m %d %H.%M.%S')}.md"

with tempfile.NamedTemporaryFile(mode='w+', suffix=".tmp") as tf:

    if len(argv) == 1:
        tf.write('')
        tf.flush()
        call([EDITOR, tf.name])
        tf.seek(0)
        DATA = tf.read()
    else:
        print("Pulling...")
        os.system(f"rclone sync {PATH_NOTES_CLOUD} {PATH_NOTES_LOCAL}")
        print("Pulled.")
        DATA = ' '.join(argv[1:])

    if len(DATA) > 0:
        print("Saving...")
        cabinet.writeFile(
            FILENAME, "notes", DATA)
    else:
        print("No changes made.")
