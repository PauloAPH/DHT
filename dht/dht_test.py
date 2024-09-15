import unittest

import node as ND
import sys

from protos import dht_pb2
from protos import dht_pb2_grpc
from unittest.mock import MagicMock, mock_open, patch, call

class TestFiles(unittest.TestCase):

    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data="This is a test.")
    @patch('os.path.join', return_value='/fake_path/file.txt')
    def test_save_file(self, mock_join, mock_open_func, mock_makedirs):
        node_id = 1
        file_id = 2
        data = "This is a test."

        # Call the function
        ND.save_file(node_id, file_id, data)

        mock_makedirs.assert_called_once_with("DHT_NODE_1", exist_ok=True)

        mock_open_func.assert_called_once_with('/fake_path/file.txt', 'w')

        mock_open_func().write.assert_called_once_with(data)

    @patch('builtins.open', new_callable=mock_open, read_data="This is a test.")
    @patch('os.path.join')
    def test_open_dht_file(self, mock_join, mock_open_func):
        node_id = 1
        file_id = 2

        mock_join.return_value = 'DHT_NODE_1/2.txt'

        result = ND.open_dht_file(node_id, file_id)
        mock_open_func.assert_called_once_with('DHT_NODE_1/2.txt', 'r')
        self.assertEqual(result, "This is a test.")

class TestNode(unittest.TestCase):

    def test_init(self):
        node = ND.Node('localhost:', '50000', 1)
        self.assertEqual(node.ip, 'localhost:')
        self.assertEqual(node.port, '50000')
        self.assertEqual(node.id, 1)
        self.assertEqual(node.params_map['n_id'], 1)

    def test_update_next_params(self):
        node = ND.Node('localhost:', '50000', 1)
        node.update_next_params('127.0.0.2', '50001', 2)
        self.assertEqual(node.params_map['n_ip'], '127.0.0.2')
        self.assertEqual(node.params_map['n_port'], '50001')
        self.assertEqual(node.params_map['n_id'], 2)

    @patch('builtins.print')
    def test_print_stat(self, mocked_print):
        node = ND.Node('localhost:', '50000', 1)
        node.update_next_params('localhost:', '50001', 2)
        node.print_stat()

        mocked_print.assert_has_calls([
            call("NODE: 1"),
            call("Next node id: 2 address: localhost:50001"),
            call("Previous node id: 1 address: ")
        ])
   
        
if __name__ == '__main__':
    unittest.main()
