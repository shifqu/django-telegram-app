"""Script to be invoked to run the test suite.

It sets up the Django environment, creates the test database and runs the tests.
"""

import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def parse_args(argv=None):
    """Parse command-line arguments for the test runner."""
    parser = argparse.ArgumentParser(description="Run the django-telegram-app test suite.")

    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=1,
        help=(
            "Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output (default: 1)."
        ),
    )
    parser.add_argument(
        "-q",
        "--buffer",
        action="store_true",
        help=("Buffer stdout/stderr during tests. Only show output for failing/erroring tests."),
    )
    parser.add_argument(
        "test_labels",
        nargs="*",
        default=["tests"],
        help="Specific test labels to run (default: 'tests').",
    )

    return parser.parse_args(argv)


def main(argv=None):
    """Run the test suite."""
    args = parse_args(argv)
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.testapps.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=args.verbosity, buffer=args.buffer)
    failures = test_runner.run_tests(args.test_labels)
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
