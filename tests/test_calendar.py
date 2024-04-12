import pytest
import pandas as pd
from datetime import datetime, timedelta
from event_calendar import EventCalendar


def get_current_time():
    """ Utility function to fetch the current time, rounded down to the nearest hour for consistency """
    return datetime.now().replace(minute=0, second=0, microsecond=0)


@pytest.fixture
def setup_calendar():
    rooms = ["Conference Room", "Meeting Room 1", "Meeting Room 2"]
    current_time = get_current_time()  # Ensure this returns time rounded to the nearest minute.
    return EventCalendar(rooms=rooms, start_datetime=current_time, num_days=1, time_interval='1T')


def test_add_event_no_overlap(setup_calendar):
    now = get_current_time().replace(hour=10)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Planning Meeting', 2)
    assert len(calendar.calendar.at[now, 'Conference Room']) == 1


def test_add_event_with_overlap(setup_calendar):
    now = get_current_time().replace(hour=11)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Morning Brief', 1)
    overlap_time = now + pd.Timedelta(hours=0.5)
    print(calendar.calendar.loc[now:overlap_time, 'Conference Room'])  # Print slot from now to overlap_time
    try:
        calendar.add_event('Conference Room', overlap_time, 'Extended Brief', 1)
    except ValueError:
        pass
    print(calendar.calendar.loc[now:overlap_time, 'Conference Room'])  # Print slot from now to overlap_time


def test_event_on_future_date(setup_calendar):
    future_datetime = get_current_time() + timedelta(days=10)
    future_datetime = future_datetime.replace(hour=14)
    calendar = setup_calendar
    calendar.add_event('Meeting Room 1', future_datetime, 'Future Conference', 3)
    assert len(calendar.calendar.at[future_datetime, 'Meeting Room 1']) == 1


def test_add_events_with_times(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Morning Meeting', 2)
    next_event_start = now + timedelta(hours=3)
    calendar.add_event('Conference Room', next_event_start, 'Afternoon Meeting', 2)
    assert len(calendar.calendar.at[now, 'Conference Room']) == 1
    assert len(calendar.calendar.at[next_event_start, 'Conference Room']) == 1
