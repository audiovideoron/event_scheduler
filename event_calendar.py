import pandas as pd
from datetime import datetime, timedelta
import logging


class EventCalendar:
    """
    A class representing an event calendar.

    Parameters
    ----------
    rooms: list[str]
        List of room names in the calendar.
    start_datetime: str or datetime.datetime, optional
        The start datetime of the calendar. If not specified, the current datetime will be used.
    num_days: int, optional
        The number of days the calendar should span. Default is 730 (two years).
    time_interval: str, optional
        The time interval for each slot in the calendar. Default is '1T' (1 minute).

    Methods
    -------
    add_event(room: str, start_datetime: str or datetime.datetime, event_name: str, duration_minutes: int)
        Add an event to the calendar.
    remove_event(room: str, date: str or datetime.datetime, event_name: str)
        Remove an event from the calendar.
    list_events_on_date(date: str or datetime.datetime) -> pd.DataFrame
        List all events on a given date.
    edit_event(original_datetime: str or datetime.datetime, original_room: str, original_event_name: str,
               new_room: str = None, new_start_datetime: str or datetime.datetime = None,
               new_event_name: str = None, new_duration_minutes: int = None)
        Edit an event in the calendar.
    copy_event(original_datetime: str or datetime.datetime, original_room: str, event_name: str,
               new_room: str = None, new_start_datetime: str or datetime.datetime = None)
        Copy an event to a new date and/or room.

    Attributes
    ----------
    calendar: pd.DataFrame
        The event calendar dataframe.

    Raises
    ------
    ValueError
        If there is an event time overlap, an event is not found, or an invalid start datetime is specified.

    Examples
    --------
    Create an event calendar and add an event:
        >>> calendar = EventCalendar(['Room 1', 'Room 2'])
        >>> calendar.add_event('Room 1', '2022-01-01 10:00', 'Meeting', 60)

    Remove an event from the calendar:
        >>> calendar.remove_event('Room 1', '2022-01-01', 'Meeting')

    List all events on a specific date:
        >>> calendar.list_events_on_date('2022-01-01')

    Edit an event in the calendar:
        >>> calendar.edit_event('2022-01-01 10:00', 'Room 1', 'Meeting',
                                new_start_datetime='2022-01-01 11:00', new_duration_minutes=30)

    Copy an event to a new date and/or room:
        >>> calendar.copy_event('2022-01-01 10:00', 'Room 1', 'Meeting',
                                new_start_datetime='2022-01-02 13:00', new_room='Room 2')
    """

    def __init__(self, rooms, start_datetime=None, num_days=730, time_interval='1T'):  # Set to 730 days for two years
        """
        :param rooms: A list of room names. :param start_datetime: A datetime object representing the start date and
        time of the calendar. If not provided, it defaults to the current date and time. :param num_days: An integer
        representing the number of days for which the calendar should be initialized. The default value is 730,
        which corresponds to a two-year period. :param time_interval: A string representing the time interval for the
        calendar. The default value is '1T', which indicates 1-minute intervals.

        This method initializes the calendar with the given parameters. It creates a calendar dataframe with the
        specified number of days and time interval, indexed by a date range. Each room in the calendar is initially
        assigned an empty list.

        Example usage:
            rooms = ['Room 1', 'Room 2', 'Room 3']
            start_datetime = datetime(2022, 1, 1, 8, 0, 0)
            num_days = 365
            time_interval = '30T'
            calendar = Calendar(rooms, start_datetime, num_days, time_interval)

            """
        self.rooms = rooms
        if start_datetime is None:
            start_datetime = datetime.now()
        start_datetime = pd.to_datetime(start_datetime).floor('min')  # Normalize to the nearest minute
        end_datetime = start_datetime + timedelta(days=num_days)
        date_range = pd.date_range(start=start_datetime, end=end_datetime, freq=time_interval)
        self.calendar = pd.DataFrame(index=date_range, columns=rooms)
        self.calendar = self.calendar.applymap(lambda x: [])
        print(f"Calendar initialized from {start_datetime} to {end_datetime}")

    # Configure logging at the beginning of your script or application initialization
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    def find_event(self, event_datetime, room, event_name):
        """
        Searches for a specific event in the calendar.

        :param event_datetime: The datetime of the event to search for.
        :param room: The room where the event is scheduled.
        :param event_name: The name of the event to search for.
        :return: A tuple containing the event and its index if found, otherwise None and -1.
        """
        events = self.calendar.at[event_datetime, room]
        for index, event in enumerate(events):
            if event['event_name'] == event_name:
                return event, index
        return None, -1  # Return None and an invalid index if the event is not found

    def check_overlap(self, room, start_datetime, end_datetime):
        """
        Check if there is any event overlap in the given room within the specified time range.
        The method raises an exception if an overlap is found.

        :param room: The room to check for event overlap.
        :param start_datetime: The start datetime of the time range to check.
        :param end_datetime: The end datetime of the time range to check.

        :raises ValueError: If a time slot conflict is detected.
        """

        time_slots = pd.date_range(start=start_datetime, end=end_datetime, freq='1T')

        for time_slot in time_slots:
            events = self.calendar.at[time_slot, room]

            if events:
                raise ValueError("Time slot conflict: another event exists in the same room at the same time.")

    def add_event(self, room, start_datetime, event_name, duration_minutes):
        """
        :param room: The room where the event will take place.
        :param start_datetime: The starting datetime of the event.
        :param event_name: The name of the event.
        :param duration_minutes: The duration of the event in minutes.
        :return: None

        This method adds an event to the calendar. It first checks for any overlap with existing events in the
        specified room. If there is an overlap, it raises a ValueError. If there is no overlap, it adds the event to
        all its time slots.

        Example Usage: ``` calendar.add_event(room='Room 1', start_datetime=datetime(2021, 10, 1, 10, 0),
        event_name='Meeting', duration_minutes=60) ```
        """
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

    def remove_event(self, room, date, event_name):
        """
        Remove an event with the specified event_name from the calendar on the given date and room.

        :param room: The room for which to remove the event.
        :param date: The date on which the event occurs.
        :param event_name: The name of the event to remove.
        :return: None
        """
        events = self.calendar.at[date, room]
        filtered_events = [event for event in events if event['event_name'] != event_name]
        if not filtered_events:
            self.calendar.at[date, room] = []
        else:
            self.calendar.at[date, room] = filtered_events

    def list_events_on_date(self, date):
        """
        :param date: The date for which to list events.
        :return: The events on the given date.

        """
        if not isinstance(date, pd.Timestamp):
            date = pd.Timestamp(date)
        return self.calendar.loc[date]

    def edit_event(self, original_datetime, original_room, original_event_name, new_room=None, new_start_datetime=None,
                   new_event_name=None, new_duration_minutes=None):
        """
        :param original_datetime: The original datetime of the event to be edited.
        :param original_room: The original room of the event to be edited.
        :param original_event_name: The original name of the event to be edited.
        :param new_room: The new room for the edited event. Default is None.
        :param new_start_datetime: The new start datetime for the edited event. Default is None.
        :param new_event_name: The new name for the edited event. Default is None.
        :param new_duration_minutes: The new duration in minutes for the edited event. Default is None.
        :return: None

        This method allows you to edit an event by providing the original event details and the new details for the
        event. If the original event is not found, a ValueError will be raised. The method removes the original event
        from the calendar, and then adds the edited event with the new details. If new room, new start datetime,
        new event name, or new duration are not provided, the method will use the original values.

        If the new event overlaps with another event in the new room, a ValueError will be raised.

        Example usage:

        edit_event(
            original_datetime=datetime(2022, 1, 1, 10, 0),
            original_room='Room 1',
            original_event_name='Meeting',
            new_start_datetime=datetime(2022, 1, 1, 10, 30),
            new_event_name='Updated Meeting',
            new_duration_minutes=60
        )
        """
        # Find the original event
        original_event, index = self.find_event(original_datetime, original_room, original_event_name)
        if original_event is None:
            raise ValueError("Original event not found.")

        # Remove the original event
        self.remove_event(original_room, original_datetime, original_event_name)

        # Set defaults for unspecified new event parameters
        if new_room is None:
            new_room = original_room
        if new_start_datetime is None:
            new_start_datetime = original_datetime
        if new_event_name is None:
            new_event_name = original_event_name
        if new_duration_minutes is None:
            original_duration = (original_event['end_time'] - original_event['start_time']).total_seconds() / 60
            new_duration_minutes = original_duration

        # Check for overlaps unless it's essentially the same event
        end_datetime = new_start_datetime + timedelta(minutes=new_duration_minutes)
        time_slots = pd.date_range(start=new_start_datetime, end=end_datetime - timedelta(minutes=1), freq='1T')
        for time_slot in time_slots:
            if any(e for e in self.calendar.at[time_slot, new_room] if e['event_name'] != original_event_name):
                raise ValueError("Event time overlap with another event.")

        # Add the event with new details
        new_event = {'event_name': new_event_name, 'start_time': new_start_datetime, 'end_time': end_datetime}
        for time_slot in time_slots:
            self.calendar.at[time_slot, new_room] = [new_event]

        print(f"Event '{original_event_name}' edited successfully.")

    def copy_event(self, original_datetime, original_room, event_name, new_room=None, new_start_datetime=None):
        """
        :param original_datetime: The original datetime of the event to be copied.
        :param original_room: The original room of the event to be copied.
        :param event_name: The name of the event to be copied.
        :param new_room: (optional) The new room where the event will be copied to.
        :param new_start_datetime: (optional) The new datetime when the event will start in the new room.
        :return: None

        This method copies an event from the original datetime and room to a new room and datetime. If new_room or
        new_start_datetime are not provided, they default to the original room and datetime. The method checks if the
        new_start_datetime is within the range of the calendar's index and raises a ValueError if it is not. It also
        checks if the new_start_datetime is outside the range of the calendar's index and raises a ValueError if it
        is. If the original event is not found, a ValueError is raised.

        If the new_room and new_start_datetime are both provided, the method calculates the duration of the original
        event and determines the new_end_datetime based on the new_start_datetime and duration. It checks for
        overlaps with existing events in the new room and raises a warning if a conflict is detected. If no conflicts
        are found, the method copies the event to the new time and room in the calendar.

        Example usage: calendar = Calendar() calendar.copy_event(original_datetime, original_room, event_name,
        new_room=optional_new_room, new_start_datetime=optional_new_datetime)
        """
        # Check if new_start_datetime is within the DataFrame index
        if new_start_datetime not in self.calendar.index:
            raise ValueError(f"Attempted to access a date outside of the calendar's range: {new_start_datetime}")

        # Date range validation
        if new_start_datetime is not None:
            if new_start_datetime < self.calendar.index[0] or new_start_datetime > self.calendar.index[-1]:
                raise ValueError(f"Attempted to access a date outside of the calendar's range: {new_start_datetime}")

        original_event, index = self.find_event(original_datetime, original_room, event_name)
        if original_event is None:
            raise ValueError("Original event not found.")

        if new_room is None:
            new_room = original_room
        if new_start_datetime is None:
            new_start_datetime = original_datetime

        original_duration = (original_event['end_time'] - original_event['start_time']).total_seconds() / 60
        new_end_datetime = new_start_datetime + timedelta(minutes=original_duration)
        logging.debug(
            f"Attempting to copy to {new_room} at {new_start_datetime} with duration {original_duration} minutes.")

        # Check for overlaps
        time_slots = pd.date_range(start=new_start_datetime, end=new_end_datetime - timedelta(minutes=1), freq='1T')
        for time_slot in time_slots:
            current_events = self.calendar.at[time_slot, new_room]
            if current_events:
                logging.warning(f"Conflict detected at {time_slot}, not proceeding with event copy.")
                return

        # If no conflicts, copy the event to new time and room
        new_event = {'event_name': event_name, 'start_time': new_start_datetime, 'end_time': new_end_datetime}
        for time_slot in time_slots:
            self.calendar.at[time_slot, new_room].append(new_event)
        logging.info(
            f"Event '{event_name}' copied successfully from {original_room} to {new_room} at {new_start_datetime}.")
