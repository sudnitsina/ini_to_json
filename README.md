[![Build Status](https://travis-ci.org/sudnitsina/ini_to_json.svg?branch=master)](https://travis-ci.org/sudnitsina/ini_to_json)
# ini_to_json
required python > 2.7
Script to convert from Ansible ini to JSON format
```
{
  "_meta": {
    "hostvars": {
      HOST_NAME: {
        VARIABLE_NAME: VARIABLE_VALUE
      }
    }
  },
   GROUP_NAME: {
     "hosts": [HOST_NAME],
     "vars": {VARIABLE_NAME: VARIABLE_VALUE},
     "children": [GROUP_NAME]
     }
 }
 ```
```
usage: ini_converter.py [-h] [-f FILE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to the file
  ```
