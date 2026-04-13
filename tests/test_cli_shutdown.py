"""
Tests for signal-driven CLI shutdown handling.
"""

import unittest
from unittest.mock import patch

from openevolve import cli


class _ExitCalled(Exception):
    """Raised by the test double for os._exit."""

    def __init__(self, code: int):
        super().__init__(code)
        self.code = code


class TestCliShutdown(unittest.TestCase):
    def test_main_uses_os_exit_after_signal_driven_shutdown(self):
        async def fake_main_async():
            return 143

        with patch("openevolve.cli.main_async", fake_main_async):
            with patch("openevolve.cli.logging.shutdown"):
                with patch("openevolve.cli.sys.stdout.flush"):
                    with patch("openevolve.cli.sys.stderr.flush"):
                        with patch(
                            "openevolve.cli.os._exit",
                            side_effect=lambda code: (_ for _ in ()).throw(_ExitCalled(code)),
                        ):
                            with self.assertRaises(_ExitCalled) as cm:
                                cli.main()

        self.assertEqual(cm.exception.code, 143)

    def test_main_returns_normally_without_signal(self):
        async def fake_main_async():
            return 0

        with patch("openevolve.cli.main_async", fake_main_async):
            with patch("openevolve.cli.os._exit") as mock_exit:
                self.assertEqual(cli.main(), 0)
                mock_exit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
