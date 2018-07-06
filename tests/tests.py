import unittest


class TestConversion(unittest.TestCase):
    def test_convert(self):
        test_data = '''
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
                    
                    '''
        result = {'_meta': {'hostvars': {'host1': {'123': '45632', '567': '890'},
                                         'host2': {'a': 'b'},
                                         'host4': {'ansible_ssh_port': '2233'}}},
                  'atlanta': {'hosts': ['host1', 'host2']},
                  'raleigh': {'hosts': ['host4', 'host3']},
                  'southeast': {'children': ['atlanta', 'raleigh'],
                                'vars': {'escape_pods': '2',
                                         'halon_system_timeout': '30',
                                         'self_destruct_countdown': '60',
                                         'some_server': 'foo.southeast.example.com'}},
                  'usa': {'children': ['southeast', 'northeast']}}
        my_json = serializer(test_data)
        self.assertDictEqual(my_json, result)

    def test_wrong_title(self):
        test_data = '''
                    [atlanta]
                    host1 123="45632" 567=890 #Comment
                    host2 a="b"

                        # ddddd
                    [raleigh]
                    host4 ansible_ssh_port=2233
                    host3

                    [southeast:c]
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

                    '''
        self.assertRaises(ValueError, serializer, test_data)

    def test_wrong_data(self):
        test_data = 123
        self.assertRaises(ValueError, serializer, test_data)
        test_data = '123'
        self.assertRaises(ValueError, serializer, test_data)
        test_data = '''
        123
        321
        '''
        self.assertRaises(ValueError, serializer, test_data)


if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from ini_converter import serializer
    else:
        from ini_converter import serializer
    unittest.main()