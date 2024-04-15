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
    return EventCalendar(rooms=rooms, start_datetime=current_time, num_days=180, time_interval='1T')


def test_add_event_no_overlap(setup_calendar):
    now = get_current_time().replace(hour=20)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Planning Meeting', 2)
    assert len(calendar.calendar.at[now, 'Conference Room']) == 1


def test_add_event_with_overlap(setup_calendar):
    now = get_current_time().replace(hour=20)
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
    future_datetime = get_current_time() + timedelta(days=20)
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


def test_edit_event_basic(setup_calendar):
    now = get_current_time().replace(hour=10)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Strategy Meeting', 60)
    calendar.edit_event(now, 'Conference Room', 'Strategy Meeting',
                        new_event_name='Revised Strategy Meeting', new_duration_minutes=120)
    # Verify the changes were applied
    events = calendar.list_events_on_date(now)
    assert len(events['Conference Room']) == 1
    assert events['Conference Room'][0]['event_name'] == 'Revised Strategy Meeting'
    assert (events['Conference Room'][0]['end_time'] - events['Conference Room'][0][
        'start_time']).total_seconds() == 7200


def test_edit_event_conflict(setup_calendar):
    now = get_current_time().replace(hour=12)
    calendar = setup_calendar
    calendar.add_event('Meeting Room 1', now, 'Budget Meeting', 60)
    calendar.add_event('Meeting Room 1', now + timedelta(hours=1), 'HR Meeting', 60)
    # Attempt to extend the 'Budget Meeting' into the 'HR Meeting' time
    with pytest.raises(ValueError):
        calendar.edit_event(now, 'Meeting Room 1', 'Budget Meeting', new_duration_minutes=120)


def test_edit_nonexistent_event(setup_calendar):
    now = get_current_time().replace(hour=14)
    calendar = setup_calendar
    # Attempt to edit an event that doesn't exist
    with pytest.raises(ValueError):
        calendar.edit_event(now, 'Meeting Room 2', 'Nonexistent Meeting',
                            new_event_name='Still Nonexistent', new_duration_minutes=30)


def test_edit_event_change_room_and_time(setup_calendar):
    now = get_current_time().replace(hour=16)
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Planning Session', 60)
    new_time = now + timedelta(hours=2)
    calendar.edit_event(now, 'Conference Room', 'Planning Session',
                        new_room='Meeting Room 1', new_start_datetime=new_time)
    # Ensure the event is now at the new time and room
    assert len(calendar.calendar.at[now, 'Conference Room']) == 0
    assert len(calendar.calendar.at[new_time, 'Meeting Room 1']) == 1
    assert calendar.calendar.at[new_time, 'Meeting Room 1'][0]['event_name'] == 'Planning Session'


def test_copy_event_basic(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Initial Meeting', 60)
    new_time = now + timedelta(days=1)
    # Correctly specify new_time as the new_start_datetime and explicitly name the parameter
    calendar.copy_event(now, 'Conference Room', 'Initial Meeting', new_start_datetime=new_time)

    # Verify original event exists
    assert len(calendar.list_events_on_date(now)['Conference Room']) == 1
    # Verify new event is copied correctly
    assert len(calendar.list_events_on_date(new_time)['Conference Room']) == 1


def test_copy_event_room_change(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Room Change Meeting', 60)
    new_room = "Meeting Room 1"
    calendar.copy_event(now, 'Conference Room', 'Room Change Meeting', new_room=new_room, new_start_datetime=now)

    # Verify event is in the new room
    assert len(calendar.list_events_on_date(now)[new_room]) == 1
    # Verify original room is unaffected
    assert len(calendar.list_events_on_date(now)['Conference Room']) == 1


def test_copy_event_conflict(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Conflict Meeting', 60)
    calendar.add_event('Conference Room', now + timedelta(hours=1), 'Non-Overlapping Meeting', 60)

    # Attempt to copy the 'Conflict Meeting' to a time that overlaps with 'Non-Overlapping Meeting'
    with pytest.raises(ValueError):
        calendar.copy_event(now, 'Conference Room', 'Conflict Meeting',
                            new_start_datetime=now + timedelta(minutes=30))

    # Check that the original event is still in place and no new event was added at the conflict time
    assert len(calendar.list_events_on_date(now)['Conference Room']) == 1
    new_time = now + timedelta(minutes=30)
    assert len(calendar.list_events_on_date(new_time)['Conference Room']) == 0


def test_copy_event_invalid_date(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Future Meeting', 60)
    invalid_time = now + timedelta(days=365)  # Beyond the current calendar range
    with pytest.raises(ValueError):
        calendar.copy_event(now, 'Conference Room', 'Future Meeting', invalid_time)


def test_copy_multiple_events(setup_calendar):
    now = get_current_time()
    calendar = setup_calendar
    calendar.add_event('Conference Room', now, 'Multi-Copy Meeting', 60)
    copy_times = [now + timedelta(days=i) for i in range(1, 5)]  # Next four days
    for copy_time in copy_times:
        calendar.copy_event(now, 'Conference Room', 'Multi-Copy Meeting', copy_time)

    # Check each day to ensure the event was copied
    for copy_time in copy_times:
        assert len(calendar.list_events_on_date(copy_time)['Conference Room']) == 1
