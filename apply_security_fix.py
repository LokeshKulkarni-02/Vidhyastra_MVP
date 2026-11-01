#!/usr/bin/env python3
"""Safely patch Vidhyastra app.py security defaults.

Run this from the Vidhyastra project root:
    python apply_security_fix.py

The script creates a timestamped backup and only replaces the two known
configuration blocks. It does not modify the database or application routes.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

APP_PATH = Path(__file__).resolve().with_name("app.py")

OLD_CONFIG = '''app = Flask(__name__)
app.secret_key = os.environ.get(
    'VIDHYASTRA_SECRET',
    'dev-only-change-this-secret-before-deployment'
)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = (
    os.environ.get('VIDHYASTRA_HTTPS', '0') == '1'
)
'''

NEW_CONFIG = '''app = Flask(__name__)

# Set VIDHYASTRA_ENV=production on the production host. Production must have
# a strong secret supplied by the host's environment/configuration manager.
APP_ENV = os.environ.get('VIDHYASTRA_ENV', 'development').strip().lower()
IS_PRODUCTION = APP_ENV in {'production', 'prod'}
_configured_secret = os.environ.get('VIDHYASTRA_SECRET', '').strip()

if IS_PRODUCTION and not _configured_secret:
    raise RuntimeError(
        'VIDHYASTRA_SECRET is required when VIDHYASTRA_ENV=production. '
        'Generate a strong key and configure it in the hosting environment.'
    )

if _configured_secret and len(_configured_secret) < 32:
    raise RuntimeError(
        'VIDHYASTRA_SECRET must contain at least 32 characters. '
        'Generate a new key with secrets.token_urlsafe(48).'
    )

if not _configured_secret:
    # Convenient for local development only. This random key changes on each
    # restart, so local sessions will be invalidated after a restart.
    _configured_secret = secrets.token_urlsafe(48)
    app.logger.warning(
        'VIDHYASTRA_SECRET is not set; using a temporary development-only key.'
    )

app.secret_key = _configured_secret
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = (
    IS_PRODUCTION or os.environ.get('VIDHYASTRA_HTTPS', '0') == '1'
)
'''

OLD_RUN = '''if __name__ == '__main__':
    app.run(
        debug=os.environ.get('VIDHYASTRA_DEBUG', '1') == '1'
    )
'''

NEW_RUN = '''if __name__ == '__main__':
    debug_requested = os.environ.get('VIDHYASTRA_DEBUG', '0').strip().lower() in {
        '1', 'true', 'yes', 'on'
    }

    if IS_PRODUCTION and debug_requested:
        raise RuntimeError(
            'Flask debug mode is forbidden in production. Set Vidhyastra debug to 0.'
        )

    app.run(debug=debug_requested)
'''


def main() -> int:
    if not APP_PATH.is_file():
        print(f"ERROR: app.py not found next to {Path(__file__).name}.", file=sys.stderr)
        return 1

    source = APP_PATH.read_text(encoding='utf-8')

    if NEW_CONFIG in source and NEW_RUN in source:
        print('Security settings are already patched; no changes made.')
        return 0

    if source.count(OLD_CONFIG) != 1:
        print(
            'ERROR: expected to find the original Flask configuration block exactly once. '
            'No file was changed. Review app.py manually before proceeding.',
            file=sys.stderr,
        )
        return 2

    if source.count(OLD_RUN) != 1:
        print(
            'ERROR: expected to find the original app.run block exactly once. '
            'No file was changed. Review app.py manually before proceeding.',
            file=sys.stderr,
        )
        return 3

    updated = source.replace(OLD_CONFIG, NEW_CONFIG, 1).replace(OLD_RUN, NEW_RUN, 1)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = APP_PATH.with_name(f'app.py.backup_{timestamp}')
    backup_path.write_text(source, encoding='utf-8')
    APP_PATH.write_text(updated, encoding='utf-8')

    print('Security patch applied successfully.')
    print(f'Backup created: {backup_path.name}')
    print('Next run: python -m py_compile app.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
