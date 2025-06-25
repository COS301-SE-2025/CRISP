"""Django's command-line utility for admin tasks"""
import os
import sys


def main():
    """Run administrative tasks."""
<<<<<<<< HEAD:crisp_threat_intel/manage.py
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp_threat_intel.settings')
========
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crisp.settings')
>>>>>>>> 9b1b65c42fb53c6d10298d1f08a45c5b03bf43a5:manage.py
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()