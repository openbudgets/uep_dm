# -*- coding: utf-8 -*-

from .context import uep_dm

import json
import unittest


class SendDMRequestToUEPServer(unittest.TestCase):
    """Basic test cases."""

    def test_send_csv_to_uep_server(self):
        CSV_FILE = "/home/wang/OP/DAM/Input_SN4KQV.csv"  # path to the CSV file
        result_dic = json.loads(uep_dm.send_request_to_UEP_server(CSV_FILE))
        assert 'rules' in result_dic.keys()
        assert 'task' in result_dic.keys()
        assert False


if __name__ == '__main__':
    unittest.main()
