"""utils"""

import re

mysql_pattern = re.compile(
    r'^.*:\/\/(?P<user>.*):(?P<password>.*)@(?P<host>.*):(?P<port>.*)\/(?P<database>.*)\?(charset=)+(?P<charset>.*)$')


def transform_mysql_db_str(db_str: str) -> dict:
    """Transform a database string"""
    matcher = mysql_pattern.match(db_str)
    if matcher:
        return matcher.groupdict()
    return dict()
