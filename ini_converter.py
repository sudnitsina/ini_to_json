#!/usr/bin/python
import argparse
import json
import re
import shlex


def serializer(data):
    """ Convert ini format inventory into json
    """
    if not isinstance(data, str):
        raise ValueError("Invalid data")

    _json = {"_meta": {"hostvars": {}}}
    _parser = re.compile(
                r'''^\[
                        ([^:\]\s]+)             # group name
                        (?::(\w+))?             # optional : and tag name
                    \]
                    \s*                         # ignore trailing whitespace
                    (?:\#.*)?                   # and/or a comment till the
                    $                           # end of the line
                ''', re.X
    )

    state = None
    groupname = ''
    for row in data.split('\n'):
        row = row.strip()
        if row == '' or row.startswith(";") or row.startswith("#"):
            continue
        m = _parser.match(row)
        if m:
            (groupname, state) = m.groups()
            state = state or 'hosts'
            if groupname not in _json:
                _json[groupname] = {}
        else:
            a = shlex.split(row, comments=True)
            if state == 'children':
                _json[groupname].setdefault(state, []).append(a[0])
            elif state == 'vars':
                _json[groupname].setdefault(state, {})
                (var, val) = a[0].split("=")
                _json[groupname][state][var] = val
            elif state == 'hosts':
                host = a[0]
                _json[groupname].setdefault(state, []).append(host)
                if row.find(" ") != -1:
                    _json["_meta"]["hostvars"].setdefault(host, {})
                    for i in range(1, len(a)):
                        (var, val) = a[i].split("=")
                        _json["_meta"]["hostvars"][host][var] = val
            else:
                raise ValueError('invalid data')
    return _json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to the file")
    args = parser.parse_args()

    with open(args.file) as ini:
        f = ini.read()

    print(json.dumps(serializer(f), sort_keys=True, indent=2))
