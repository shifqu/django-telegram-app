"""Script to be invoked to run the test suite.

It sets up the Django environment, creates the test database and runs the tests.
"""

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    """Run the test suite."""
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
