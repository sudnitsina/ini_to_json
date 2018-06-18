#!/usr/bin/python
import argparse
import json
import re
import shlex


def serializer(data):
    if not isinstance(data, str):
        raise ValueError("Invalid data")
    _json = {"_meta": {"hostvars": {}}}
    _parser = re.compile(
                r'''^\[
                        ([^:\]\s]+)             # group name (see groupname below)
                        (?::(\w+))?             # optional : and tag name
                    \]
                    \s*                         # ignore trailing whitespace
                    (?:\#.*)?                   # and/or a comment till the
                    $                           # end of the line
                ''', re.X
    )

    state = ''
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
            if state not in ['hosts', 'children', 'vars']:
                title = ":".join(m.groups())
                raise ValueError("Section [%s] has unknown type: %s" % (title, state))
            if state == 'hosts':
                _json[groupname]["hosts"] = []
            if state == 'vars':
                _json[groupname]["vars"] = {}
            if state == 'children':
                _json[groupname]["children"] = []
        else:
            a = shlex.split(row, comments=True)
            if state == 'children':
                _json[groupname][state].append(a[0])
            elif state == 'vars':
                (var, val) = a[0].split("=")
                _json[groupname][state][var] = val
            elif state == 'hosts':
                host = a[0]
                _json[groupname][state].append(host)
                if row.find(" ") != -1:
                    _json["_meta"]["hostvars"][host] = {}
                    for i in range(1, len(a)):
                        (var, val) = a[i].split("=")
                        _json["_meta"]["hostvars"][host][var] = val
            elif state == '':
                raise ValueError("Invalid data")
    return _json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to the file")
    args = parser.parse_args()

    with open(args.file) as ini:
        f = ini.read()

    print(json.dumps(serializer(f), sort_keys=True, indent=2))
