#!/usr/bin/python
import argparse
import json
import re
import shlex


def serializer(data):
    """ Convert ini format inventory into dict."""
    if not isinstance(data, str):
        raise ValueError("Invalid data")

    _json = {"_meta": {"hostvars": {}}}
    _parser = re.compile(
        r"""^\[
                        ([^:\]\s]+)             # group name
                        (?::(\w+))?             # optional : and tag name
                    \]
                    \s*                         # ignore trailing whitespace
                    (?:\#.*)?                   # and/or a comment till the
                    $                           # end of the line
                """,
        re.X,
    )

    section = "hosts"
    groupname = "ungrouped"
    for row in data.splitlines():
        row = row.strip()
        if row == "" or row.startswith(";") or row.startswith("#"):
            continue
        m = _parser.match(row)
        if m:
            (groupname, section) = m.groups()
            section = section or "hosts"
            if groupname not in _json:
                _json[groupname] = {}
        else:
            a = shlex.split(row, comments=True)
            if section == "children":
                _json[groupname].setdefault(section, []).append(a[0])
            elif section == "vars":
                _json[groupname].setdefault(section, {})
                (var, val) = _variable_handler(a[0])
                _json[groupname][section][var] = val
            elif section == "hosts":
                if groupname not in _json:
                    _json[groupname] = {}
                host = a[0]
                _json[groupname].setdefault(section, []).append(host)
                if row.find(" ") != -1:
                    _json["_meta"]["hostvars"].setdefault(host, {})
                    for i in range(1, len(a)):
                        (var, val) = _variable_handler(a[i])
                        _json["_meta"]["hostvars"][host][var] = val
            else:
                raise ValueError("Section {} has unknown type".format(section))
    return _json


def _variable_handler(string):
    var, val = string.split("=")
    try:
        val = eval(val)
    except SyntaxError:
        pass
    except NameError:
        pass
    return var, val


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", help="Path to the file")
    args = parser.parse_args()

    with open(args.file) as ini:
        f = ini.read()

    print(json.dumps(serializer(f), sort_keys=True, indent=2))
