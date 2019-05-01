import unittest
import subprocess


class TestConversion(unittest.TestCase):
    def test_wrong_title(self):
        test_data = """[atlanta:section]
                       host1 123="45632" 567=890 #Comment
                       host2 a="b" """
        self.assertRaises(ValueError, serializer, test_data)

    def test_wrong_data(self):
        test_data = 123
        self.assertRaises(ValueError, serializer, test_data)

    def test_ungrouped(self):
        test_data = "123"
        my_json = serializer(test_data)
        exp_result = {"_meta": {"hostvars": {}}, "ungrouped": {"hosts": ["123"]}}

        self.assertDictEqual(my_json, exp_result)

        test_data = """123\n321"""
        exp_result = {"_meta": {"hostvars": {}}, "ungrouped": {"hosts": ["123", "321"]}}

        my_json = serializer(test_data)
        self.assertDictEqual(my_json, exp_result)

        exp_result = {
            "_meta": {"hostvars": {"testhost": {"self_destruct_countdown": True}}},
            "ungrouped": {"hosts": ["testhost"]},
        }

        test_data = "testhost self_destruct_countdown=True"

        my_json = serializer(test_data)
        self.assertDictEqual(my_json, exp_result)

    def test_variables(self):
        #  '=' symbol is not allowed
        test_data = "host1 a=1=2"
        self.assertRaises(ValueError, serializer, test_data)

        # witespaces are not allowed in variable
        self.assertRaises(ValueError, serializer, "host1 a=1 2")
        self.assertRaises(ValueError, serializer, "host1 a=b c")

        # witespaces around '=' are not allowed
        self.assertRaises(ValueError, serializer, "host1 a= b")
        self.assertRaises(ValueError, serializer, "host1 a =b")
        self.assertRaises(ValueError, serializer, "host1 a = b")

    def test_data_types(self):
        # strings
        my_json = serializer("host1 a='abc'")
        exp_result = {
            "_meta": {"hostvars": {"host1": {"a": "abc"}}},
            "ungrouped": {"hosts": ["host1"]},
        }
        self.assertDictEqual(my_json, exp_result)

        # numbers
        my_json = serializer("host1 a=1")
        exp_result = {
            "_meta": {"hostvars": {"host1": {"a": 1}}},
            "ungrouped": {"hosts": ["host1"]},
        }
        self.assertDictEqual(my_json, exp_result)

        # Arrays
        my_json = serializer("host1 a=[1,2,3]")
        exp_result = {
            "_meta": {"hostvars": {"host1": {"a": [1, 2, 3]}}},
            "ungrouped": {"hosts": ["host1"]},
        }
        self.assertDictEqual(my_json, exp_result)

        # Booleans
        my_json = serializer("host1 a=True")
        exp_result = {
            "_meta": {"hostvars": {"host1": {"a": True}}},
            "ungrouped": {"hosts": ["host1"]},
        }
        self.assertDictEqual(my_json, exp_result)

        # null
        my_json = serializer("host1 a=None")
        exp_result = {
            "_meta": {"hostvars": {"host1": {"a": None}}},
            "ungrouped": {"hosts": ["host1"]},
        }
        self.assertDictEqual(my_json, exp_result)

    def test_not_supported_data_types(self):
        # Objects in host vars
        test_data = "host1 a={'port': 8080}"
        self.assertRaises(ValueError, serializer, test_data)

        # Objects in group vars
        test_data = """[web:vars]
                    a={'port': 8080}"""
        self.assertRaises(ValueError, serializer, test_data)

    def test_convert(self):
        test_data = """
                    [atlanta]
                    host1 123="45632" 567=890 #Comment
                    host2 a="b"

                        # ddddd
                    [raleigh]
                    host4 ansible_ssh_port=2233
                    host3

                    [southeast:children]
                    atlanta
                    raleigh

                    [southeast:vars]
                    some_server="foo.southeast.example.com" # comment
                    halon_system_timeout=30
                    self_destruct_countdown=60
                    escape_pods=2

                    [usa:children]
                    southeast
                    northeast
                    """
        exp_result = {
            "_meta": {
                "hostvars": {
                    "host1": {"123": 45632, "567": 890},
                    "host2": {"a": "b"},
                    "host4": {"ansible_ssh_port": 2233},
                }
            },
            "atlanta": {"hosts": ["host1", "host2"]},
            "raleigh": {"hosts": ["host4", "host3"]},
            "southeast": {
                "children": ["atlanta", "raleigh"],
                "vars": {
                    "escape_pods": 2,
                    "halon_system_timeout": 30,
                    "self_destruct_countdown": 60,
                    "some_server": "foo.southeast.example.com",
                },
            },
            "usa": {"children": ["southeast", "northeast"]},
        }
        my_json = serializer(test_data)
        self.assertDictEqual(my_json, exp_result)

        test_data = """
                      # other example config
                      host1 # this is 'ungrouped'
                      # both hosts have same IP but diff ports, also 'ungrouped'
                      host2 ansible_host=127.0.0.1 ansible_port=44
                      host3 ansible_host=127.0.0.1 ansible_port=45
                      [g1]
                      host4
                      [g2]
                      host4
                    """
        exp_result = {
            "_meta": {
                "hostvars": {
                    "host1": {},
                    "host2": {"ansible_host": "127.0.0.1", "ansible_port": 44},
                    "host3": {"ansible_host": "127.0.0.1", "ansible_port": 45},
                }
            },
            "g1": {"hosts": ["host4"]},
            "g2": {"hosts": ["host4"]},
            "ungrouped": {"hosts": ["host1", "host2", "host3"]},
        }
        my_json = serializer(test_data)
        self.assertDictEqual(my_json, exp_result)


class TestCLI(unittest.TestCase):
    def test_json(self):
        cmd = ["python", "ini_converter.py", "-f", "tests/test_data.ini"]
        result = subprocess.check_output(cmd)
        exp_result = {
            "_meta": {
                "hostvars": {
                    "host1": {},
                    "host2": {"ansible_host": "127.0.0.1", "ansible_port": 44},
                    "host3": {"ansible_host": "127.0.0.1", "ansible_port": 45},
                }
            },
            "g1": {"hosts": ["host4"]},
            "g2": {"hosts": ["host4"]},
            "ungrouped": {"hosts": ["host1", "host2", "host3"]},
        }
        import ast
        result = result.decode("utf-8")
        result = ast.literal_eval(result)
        self.assertDictEqual(exp_result, result)

    def test_yaml(self):
        cmd = ["python", "ini_converter.py", "-f", "tests/test_data.ini", "--yaml"]
        result = subprocess.check_output(cmd).decode("utf-8")
        exp_result = """_meta:
  hostvars:
    host1: {}
    host2:
      ansible_host: 127.0.0.1
      ansible_port: 44
    host3:
      ansible_host: 127.0.0.1
      ansible_port: 45
g1:
  hosts:
  - host4
g2:
  hosts:
  - host4
ungrouped:
  hosts:
  - host1
  - host2
  - host3

"""
        self.assertEqual(result, exp_result)


if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path

        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from ini_converter import serializer
    else:
        from ini_converter import serializer
    unittest.main()
