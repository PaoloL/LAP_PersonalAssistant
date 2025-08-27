from typing import TypedDict


class CalendarResponse(TypedDict):
    event_name: str
    event_start_date: str
    event_end_date: str
    event_participants: []