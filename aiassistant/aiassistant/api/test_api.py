import unittest
import requests
import json

# Assuming the API runs on localhost and port 5000 as configured in api.py
BASE_URL = "http://localhost:5000"

class TestPiApi(unittest.TestCase):

    def test_get_volume(self):
        """Test retrieving the current volume."""
        response = requests.get(f"{BASE_URL}/volume")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("volume", data)
        self.assertIsInstance(data["volume"], int)
        self.assertTrue(0 <= data["volume"] <= 100, "Volume should be between 0 and 100")

    def test_set_volume_valid(self):
        """Test setting a valid volume level."""
        # Get initial volume to restore it later
        try:
            initial_response = requests.get(f"{BASE_URL}/volume")
            initial_volume = initial_response.json().get("volume") if initial_response.status_code == 200 else None
        except requests.RequestException:
            initial_volume = None # Default if API is not reachable or error

        test_volume = 50
        response = requests.post(f"{BASE_URL}/volume/{test_volume}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get("status"), "success")
        self.assertEqual(data.get("volume"), test_volume)

        # Verify the volume was actually set
        current_volume_response = requests.get(f"{BASE_URL}/volume")
        self.assertEqual(current_volume_response.status_code, 200)
        self.assertEqual(current_volume_response.json().get("volume"), test_volume)

        # Restore initial volume if it was successfully fetched
        if initial_volume is not None:
            requests.post(f"{BASE_URL}/volume/{initial_volume}")

    def test_set_volume_invalid_too_high(self):
        """Test setting volume too high (e.g., 101)."""
        response = requests.post(f"{BASE_URL}/volume/101")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Volume must be 0-100")

    def test_set_volume_invalid_too_low(self):
        """Test setting volume too low (e.g., -1)."""
        response = requests.post(f"{BASE_URL}/volume/-1")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Volume must be 0-100")

    def test_get_cpu_temp(self):
        """Test retrieving CPU temperature."""
        response = requests.get(f"{BASE_URL}/cpu_temp")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("cpu_temp_c", data)
        self.assertIsInstance(data["cpu_temp_c"], float)

    def test_tts_endpoint_valid_text(self):
        """Test the TTS endpoint with valid text."""
        test_text = "test"
        response = requests.get(f"{BASE_URL}/tts?text={test_text}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['content-type'], 'audio/wav')
        self.assertTrue(len(response.content) > 0)

    def test_tts_endpoint_empty_text(self):
        """Test the TTS endpoint with empty text."""
        response = requests.get(f"{BASE_URL}/tts?text=")
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data["detail"], "Text query parameter cannot be empty.")

    def test_tts_endpoint_no_text_param(self):
        """Test the TTS endpoint without the text parameter."""
        response = requests.get(f"{BASE_URL}/tts")
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertIn("detail", data)
        self.assertTrue(any(err.get("msg") == "Field required" and err.get("loc") == ["query", "text"] for err in data.get("detail", [])))


if __name__ == "__main__":
    unittest.main()
