#!/usr/bin/env python3
import sqlite3
import sys
import argparse
import tempfile
import subprocess
import os

DEFAULT_PODMAN_DB = '/var/lib/containers/storage/db.sql'

def main():
    ap = argparse.ArgumentParser(description='Open Podman container JSON in $EDITOR.')
    ap.add_argument('--podman-db',
        help=f'Specify an alternate location of Podman\'s container configuration. (default: {DEFAULT_PODMAN_DB})',
        default=DEFAULT_PODMAN_DB)
    ap.add_argument('container_id',
        help='Container name or ID. Will list the containers instead if not specified',
        nargs='?')
    args = ap.parse_args()

    conn = sqlite3.connect(args.podman_db)
    cur = conn.cursor()
    if args.container_id is None:
        print_containers(cur)
        return 0
    else:
        return edit_container_config(conn, cur, args.container_id)

def print_containers(cur: sqlite3.Cursor):
    cur.execute('select ID, Name from ContainerConfig')
    display_rows = [('ID', 'NAME')]
    display_rows.extend(cur.fetchall())

    # measure column width
    id_col_width = max(len(r[0]) for r in display_rows) + 3

    print("Available containers:")
    for c_id, c_name in display_rows:
        print(''.join((c_id.ljust(id_col_width), c_name)))

def edit_container_config(conn: sqlite3.Connection, cur: sqlite3.Cursor, name_or_id: str):
    for col_to_match in ('ID', 'Name'):
        cur.execute(f'select JSON from ContainerConfig where {col_to_match}=?', (name_or_id,))
        rs = cur.fetchall()
        if rs:
            break

    if not rs:
        print(f"No container has the name or ID '{name_or_id}'")
        return 1

    print(f'Editing configuration for container with {col_to_match}: {name_or_id}')
    old_data = rs[0][0]
    with tempfile.NamedTemporaryFile('+wb', suffix='.json') as f:
        f.write(old_data)
        editorargs = os.environ.get('EDITOR', 'nano').split()
        editorargs.append(f.name)
        subprocess.run(editorargs)
        # read back
        print('Saving configuration ...')
        f.seek(0)
        new_data = f.read()

    if new_data != old_data:
        cur.execute(f'update ContainerConfig set JSON=? where {col_to_match}=?', (new_data, name_or_id))
        conn.commit()
        conn.close()
        print("Done!")
    else:
        print("No changes detected.")

if __name__ == '__main__':
    sys.exit(main())
