from collective.transmute.utils import performance
from unittest.mock import MagicMock


class TestReportTime:
    def test_logs_start_and_end_messages(self):
        consoles = MagicMock()
        with performance.report_time("Test step", consoles):
            pass
        assert consoles.print_log.call_count == 2
        start_msg = consoles.print_log.call_args_list[0].args[0]
        end_msg = consoles.print_log.call_args_list[1].args[0]
        assert "Test step started at" in start_msg
        assert "Test step ended at" in end_msg
        assert "Test step took" in end_msg
        assert "seconds" in end_msg

    def test_yields_control(self):
        consoles = MagicMock()
        executed = False
        with performance.report_time("work", consoles):
            executed = True
        assert executed is True

    def test_propagates_exceptions(self):
        consoles = MagicMock()
        try:
            with performance.report_time("failing", consoles):
                raise ValueError("boom")
        except ValueError:
            pass
        # Start message is logged even if the body raises
        assert consoles.print_log.call_count >= 1
