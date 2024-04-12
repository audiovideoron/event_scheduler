import pandas as pd
from datetime import datetime


class EventCalendar:
    def __init__(self, rooms, start_datetime=None, num_days=30):
        self.rooms = rooms
        if start_datetime is None:
            start_datetime = datetime.now()
        else:
            start_datetime = pd.to_datetime(start_datetime)
        # Make sure the index includes times set to a consistent hour, e.g., midnight
        start_datetime = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        date_range = pd.date_range(start=start_datetime, periods=num_days, freq='D')
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

    def add_event(self, room, start_datetime, event_name, duration):
        """
        Add an event to the calendar.
        :param room: Room in which the event will be held.
        :param start_datetime: Start datetime of the event.
        :param event_name: Name of the event.
        :param duration: Duration of the event in hours.
        """
        end_datetime = pd.to_datetime(start_datetime) + pd.Timedelta(hours=duration)
        event = {'event_name': event_name, 'start_time': start_datetime, 'end_time': end_datetime}
        date_key = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)  # Key to access the DataFrame
        events = self.calendar.at[date_key, room]
        for existing_event in events:
            if not (existing_event['end_time'] <= start_datetime or existing_event['start_time'] >= end_datetime):
                raise ValueError("Event time overlap")
        events.append(event)
        self.calendar.at[date_key, room] = events

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
