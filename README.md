# ini_to_json
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
