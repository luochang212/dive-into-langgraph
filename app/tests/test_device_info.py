import datetime
import unittest
from unittest.mock import patch

from utils import device_info

REAL_DATETIME = datetime.datetime


class DeviceInfoTests(unittest.TestCase):
    def test_current_time_is_computed_on_each_call(self):
        with patch("utils.device_info.datetime.datetime") as fake_datetime:
            fake_datetime.now.side_effect = [
                REAL_DATETIME(2026, 1, 1, 0, 0, 0),
                REAL_DATETIME(2026, 1, 1, 0, 0, 1),
            ]

            self.assertEqual(device_info.get_info("当前时间 (now)"), "2026-01-01 00:00:00")
            self.assertEqual(device_info.get_info("当前时间 (now)"), "2026-01-01 00:00:01")


if __name__ == "__main__":
    unittest.main()
