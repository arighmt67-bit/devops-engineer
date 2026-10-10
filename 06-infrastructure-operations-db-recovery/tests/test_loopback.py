"""Address regression: the unchanged app may listen only on IPv6 localhost."""
import json
import subprocess
import unittest
from unittest.mock import patch
import guest_test as guest
import lab


class LoopbackTests(unittest.TestCase):
    def test_http_clients_use_hostname_for_ipv4_or_ipv6_localhost(self):
        # TEST FIXTURE ONLY: inspect request addressing, not a live HTTP response.
        class Response:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return b'{"status":"success"}'

        def open_request(request, **kwargs):
            self.assertEqual(request.host, 'localhost:5050')
            return Response()

        with patch.object(guest.urllib.request, 'urlopen', side_effect=open_request):
            self.assertEqual(guest.http()[0], 200)

        calls = []
        def call(args, timeout=900):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, 'TEST FIXTURE ONLY', '')
        with patch.object(lab, 'vm_list', return_value={'state': 'Running'}), \
             patch.object(lab, 'call', side_effect=call), patch('builtins.print'):
            lab.status()
        urls = [arg for args in calls for arg in args if arg.startswith('http://')]
        self.assertEqual(urls, ['http://localhost:5050/'])
