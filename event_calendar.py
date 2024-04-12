import pandas as pd
from datetime import datetime, timedelta


class EventCalendar:
    def __init__(self, rooms, start_datetime=None, num_days=1, time_interval='1T'):
        self.rooms = rooms
        if start_datetime is None:
            start_datetime = datetime.now()
        start_datetime = pd.to_datetime(start_datetime).floor('min')  # Normalize to the nearest minute
        end_datetime = start_datetime + timedelta(days=num_days)
        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq=time_interval)
        self.calendar = pd.DataFrame(index=date_range, columns=rooms)
        self.calendar = self.calendar.applymap(lambda x: [])

    """
    Add an event to the calendar.
    :param self: Instance of the event_calendar class.
    :param room: Room in which the event will be held.
    :param date: Date of the event.
    :param event_name: Name of the event.
    :param start_time: Start time of the event.
    :param end_time: End time of the event.
    """

    def add_event(self, room, start_datetime, event_name, duration_minutes):
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        event = {'event_name': event_name, 'start_time': start_datetime, 'end_time': end_datetime}
        # Check for overlap and add event if no overlap is found
        time_slots = pd.date_range(start=start_datetime, end=end_datetime - timedelta(minutes=1), freq='1T')
        for time_slot in time_slots:
            if not self.calendar.at[time_slot, room]:
                self.calendar.at[time_slot, room] = [event]
            else:
                raise ValueError("Event time overlap")
        """
        Add an event to the calendar.
        :param self: Instance of the event_calendar class.
        :param room: Room in which the event will be held.
        :param start_datetime: Start datetime of the event.
        :param event_name: Name of the event.
        :param duration_minutes: Duration of the event in hours.
        """

    def remove_event(self, room, date, event_name):
        """
        Remove an event from the calendar.

        :param self: Instance of the event_calendar class.
        :param room: Room from which to remove the event.
        :param date: Date of the event.
        :param event_name: Name of the event to remove.
        """
        events = self.calendar.at[date, room]
        filtered_events = [event for event in events if event['event_name'] != event_name]
        self.calendar.at[date, room] = filtered_events  # Ensure updates are correctly reflected

    def list_events_on_date(self, date):
        """
        List all events on a given date.
        :param self: Instance of the event_calendar class.
        :param date: Date for which to list events.
        """
        if not isinstance(date, pd.Timestamp):
            date = pd.Timestamp(date)
        return self.calendar.loc[date]
