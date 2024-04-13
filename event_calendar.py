import pandas as pd
from datetime import datetime, timedelta


class EventCalendar:
    def __init__(self, rooms, start_datetime=None, num_days=180, time_interval='1T'):
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
        # Check for overlap for all time slots
        time_slots = pd.date_range(start=start_datetime, end=end_datetime - timedelta(minutes=1), freq='1T')

        for time_slot in time_slots:
            if self.calendar.at[time_slot, room]:
                raise ValueError("Event time overlap")

        # If there's no overlap, add the event to all its time slots
        for time_slot in time_slots:
            self.calendar.at[time_slot, room] = [event]

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
        :param room: Room from which to remove the event.
        :param date: Date of the event.
        :param event_name: Name of the event to remove.
        """
        events = self.calendar.at[date, room]
        filtered_events = [event for event in events if event['event_name'] != event_name]
        if not filtered_events:
            self.calendar.at[date, room] = []
        else:
            self.calendar.at[date, room] = filtered_events

    def list_events_on_date(self, date):
        """
        List all events on a given date.
        :param self: Instance of the event_calendar class.
        :param date: Date for which to list events.
        """
        if not isinstance(date, pd.Timestamp):
            date = pd.Timestamp(date)
        return self.calendar.loc[date]

    def edit_event(self, original_datetime, original_room, original_event_name, new_room=None, new_start_datetime=None,
                   new_event_name=None, new_duration_minutes=None):
        """
        Edit an existing event in the calendar.
        :param original_datetime: The original start datetime of the event.
        :param original_room: The room where the event was originally booked.
        :param original_event_name: The original name of the event.
        :param new_room: The new room to move the event to (optional).
        :param new_start_datetime: The new start datetime for the event (optional).
            :param new_event_name: The new name for the event (optional).
            :param new_duration_minutes: The new duration of the event in minutes (optional).
        """
        events = self.calendar.at[original_datetime, original_room]
        event = next((event for event in events if event['event_name'] == original_event_name), None)
        if not event:
            raise ValueError("Original event not found.")

        # Temporarily remove the original event
        self.remove_event(original_room, original_datetime, original_event_name)

        # Set defaults for unspecified new event parameters
        if new_room is None:
            new_room = original_room
        if new_start_datetime is None:
            new_start_datetime = original_datetime
        if new_event_name is None:
            new_event_name = original_event_name
        if new_duration_minutes is None:
            original_duration = (event['end_time'] - event['start_time']).total_seconds() / 60
            new_duration_minutes = original_duration

        # Check for overlaps unless it's essentially the same event
        end_datetime = new_start_datetime + timedelta(minutes=new_duration_minutes)
        time_slots = pd.date_range(start=new_start_datetime, end=end_datetime - timedelta(minutes=1), freq='1T')
        for time_slot in time_slots:
            current_events = self.calendar.at[time_slot, new_room]
            if any(e for e in current_events if e['event_name'] != original_event_name):
                raise ValueError("Event time overlap with another event.")

        # Add the event with new details
        new_event = {'event_name': new_event_name, 'start_time': new_start_datetime, 'end_time': end_datetime}
        for time_slot in time_slots:
            self.calendar.at[time_slot, new_room] = [new_event]

        print(f"Event '{original_event_name}' edited successfully.")

