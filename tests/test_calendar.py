import pytest
import pandas as pd
from datetime import datetime, timedelta
from event_calendar import EventCalendar


@pytest.fixture
def setup_calendar():
    rooms = ["Conference Room", "Meeting Room 1", "Meeting Room 2"]
    start_datetime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    calendar = EventCalendar(rooms=rooms, start_datetime=start_datetime, num_days=30)
    return calendar


def test_add_event_no_overlap(setup_calendar):
    now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Planning Meeting', 2)
    assert len(calendar.calendar.at[now, 'Conference Room']) == 1


def test_add_event_with_overlap(setup_calendar):
    now = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Morning Brief', 1)
    with pytest.raises(ValueError):
        overlap_time = now + pd.Timedelta(hours=0.5)
        calendar.add_event('Conference Room', overlap_time, 'Extended Brief', 1)


def test_event_on_future_date(setup_calendar):
    future_datetime = datetime.now() + timedelta(days=10)
    future_datetime = future_datetime.replace(hour=14, minute=0, second=0, microsecond=0)
    calendar = setup_calendar
    calendar.add_event('Meeting Room 1', future_datetime, 'Future Conference', 3)
    assert len(calendar.calendar.at[future_datetime, 'Meeting Room 1']) == 1
