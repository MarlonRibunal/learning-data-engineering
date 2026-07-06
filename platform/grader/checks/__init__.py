"""Importing this package registers all built-in check types.

New check kinds are added by creating a module here and importing it below.
"""

from . import file_check, sql_check  # noqa: F401  (import for side effects)
