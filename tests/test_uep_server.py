# -*- coding: utf-8 -*-

from .context import uep_dm

import json
import unittest


class SendDMRequestToUEPServer(unittest.TestCase):
    """Basic test cases."""

    def test_send_csv_to_uep_server_rulemining(self):
        #test file location, use your own
        CSV_FILE = "../Data/esif.csv"
        result_dic = json.loads(uep_dm.send_request_to_UEP_server(CSV_FILE,"simple"))
        assert 'rules' in result_dic.keys()
        assert 'task' in result_dic.keys()
        assert False

    def test_send_csv_to_uep_server_outlier(self):
        #test file location, use your own
        CSV_FILE = "../Data/esif.csv"
        result_dic = json.loads(uep_dm.send_request_to_UEP_server(CSV_FILE,"outlier"))
        assert 'outlier' in result_dic.keys()
        assert 'task' in result_dic.keys()
        assert False

if __name__ == '__main__':
    unittest.main()
