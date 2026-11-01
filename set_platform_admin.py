#!/usr/bin/env python3
"""Create or reset a Vidhyastra platform-admin login safely.

Run from the project root after app.py has initialized the SQLite database:
    python set_platform_admin.py

The password is entered interactively and stored only as a Werkzeug password
hash. This script never prints the password or writes it to a file.
"""
from __future__ import annotations

from datetime import datetime
from getpass import getpass
from pathlib import Path
import re
import sqlite3
import sys

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / 'vidhyastra.db'


def main() -> int:
    if not DB_PATH.is_file():
        print('ERROR: vidhyastra.db was not found. Start the app once to initialize it.')
        return 1

    email = input('Platform admin email (this is the login username): ').strip().lower()
    if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        print('ERROR: enter a valid email address.')
        return 2

    password = getpass('New platform admin password (12+ characters): ')
    confirmation = getpass('Confirm new password: ')
    if password != confirmation:
        print('ERROR: passwords do not match.')
        return 3
    if len(password) < 12:
        print('ERROR: use a password with at least 12 characters.')
        return 4

    con = sqlite3.connect(DB_PATH)
    try:
        con.row_factory = sqlite3.Row
        con.execute('BEGIN IMMEDIATE')
        existing = con.execute(
            'SELECT id, role FROM users WHERE email=?', (email,)
        ).fetchone()

        password_hash = generate_password_hash(password)
        now = datetime.now().isoformat(timespec='seconds')

        if existing:
            if existing['role'] != 'platform_admin':
                con.rollback()
                print(
                    'ERROR: this email already belongs to a different account role. '
                    'No account was changed. Choose another email or resolve it manually.'
                )
                return 5
            con.execute(
                'UPDATE users SET password_hash=? WHERE id=?',
                (password_hash, existing['id']),
            )
            action = 'reset'
        else:
            con.execute(
                '''INSERT INTO users
                   (name, email, phone, password_hash, role, created_at)
                   VALUES (?, ?, ?, ?, 'platform_admin', ?)''',
                ('Vidhyastra Platform Admin', email, 'Not provided', password_hash, now),
            )
            action = 'created'

        con.commit()
        print(f'Platform administrator {action}: {email}')
        print('Login URL: /login')
        print('Role dashboard: /platform')
        print('The password was saved as a secure hash; it is not displayed.')
        return 0
    except sqlite3.Error as exc:
        con.rollback()
        print(f'Database error: {exc}', file=sys.stderr)
        return 6
    finally:
        con.close()


if __name__ == '__main__':
    raise SystemExit(main())
