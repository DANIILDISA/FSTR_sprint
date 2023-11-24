import unittest
from app import app

"""
В тестах все и так понятно, поэтому комментариев в коде нет.
"""


class TestYourAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_submit_data(self):
        data = {
            "beauty_title": "Beautiful Title",
            "title": "Title",
            "other_titles": "Other Titles",
            "connect": "Connection Info",
            "add_time": "2023-11-21",
            "user": {
                "email": "user@email.tld",
                "fam": "Пупкин",
                "name": "Василий",
                "otc": "Иванович",
                "phone": "79031234567"
            },
            "coords": {
                "latitude": "45.3842",
                "longitude": "7.1525",
                "height": "1200"
            },
            "level": {
                "winter": "Winter Info",
                "summer": "Summer Info",
                "autumn": "Autumn Info",
                "spring": "Spring Info"
            },
            "images": [
                {"title": "Седловина"},
                {"title": "Подъем"}
            ]
        }
        response = self.app.post('/submitData', json=data)
        self.assertEqual(response.status_code, 200)

    def test_get_record_by_id(self):
        response = self.app.get('/submitData/1')
        self.assertEqual(response.status_code, 200)

    def test_edit_record_by_id(self):
        data = {
            "beauty_title": "Updated Beautiful Title",
            "title": "Updated Title",
            "other_titles": "Updated Other Titles",
            "connect": "Updated Connection Info",
            "add_time": "2023-11-22",
            "level": {
                "winter": "Updated Winter Info",
                "summer": "Updated Summer Info",
                "autumn": "Updated Autumn Info",
                "spring": "Updated Spring Info"
            }
        }
        response = self.app.patch('/submitData/1', json=data)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
