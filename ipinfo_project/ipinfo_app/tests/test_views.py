from django.test import TestCase, Client
from django.urls import reverse
import json

class IpInfoViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_submit_ips_page(self):
        response = self.client.get(reverse('submit_ips'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter IPs")

    def test_valid_ip_submission(self):
        response = self.client.post(
            reverse('submit_ips'),
            json.dumps({'ips': '8.8.8.8,8.8.4.4'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No valid IPs provided.")

    def test_invalid_ip_submission(self):
        response = self.client.post(
            reverse('submit_ips'),
            json.dumps({'ips': 'invalid_ip'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No valid IPs provided.")

    def test_empty_ip_submission(self):
        response = self.client.post(
            reverse('submit_ips'),
            json.dumps({'ips': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No valid IPs provided.")

    def test_mixed_ip_submission(self):
        response = self.client.post(
            reverse('submit_ips'),
            json.dumps({'ips': '8.8.8.8,invalid_ip'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No valid IPs provided.")

    def test_large_number_of_ips_submission(self):
        large_ip_list = ','.join(['8.8.8.8'] * 1000)
        response = self.client.post(
            reverse('submit_ips'),
            json.dumps({'ips': large_ip_list}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No valid IPs provided.")