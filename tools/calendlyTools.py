# from utils import CALENDLY_TOKEN,BASE_CALENDLY_URL
import os
import pytz
import requests
from datetime import datetime
from dotenv import load_dotenv
from dateutil.parser import parse
from langchain.tools import StructuredTool


load_dotenv()

CALENDLY_TOKEN = os.getenv("calendlyKey")

BASE_CALENDLY_URL = "https://api.calendly.com"

appointmentType = {
    "followUp":"6f940d3f-d067-42a0-a393-f6855a4566ef",
    "general":"55ceb7b5-24a7-469b-ab21-2859116e8744",
    "physical":"94b0fdd4-aabe-4234-a04a-21d496b1edca",
    "specialist":"84b801db-92e1-4ea3-bd38-585c432c31df"
}

# Func to convert utc Timezones into ist (used while fetching available slots)
def utc_to_ist(utc_time_str):
    utc = pytz.utc
    ist = pytz.timezone("Asia/Kolkata")

    dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    dt_utc = dt.astimezone(utc)
    dt_ist = dt_utc.astimezone(ist)

    return dt_ist.strftime("%Y-%m-%d %H:%M:%S")
 
# Func to convert ist Timezone into utc (used while booking)
def ist_to_utc(ist_time_str: str):
    """
    Automatically parse any user-entered IST time and convert to UTC.
    """
    ist = pytz.timezone("Asia/Kolkata")

    # Parse ANY format → returns a naive or aware datetime
    dt = parse(ist_time_str)

    # If parser already detected timezone, convert directly
    if dt.tzinfo:
        dt_utc = dt.astimezone(pytz.utc)
    else:
        # Assume user meant IST → localize
        dt_ist = ist.localize(dt)
        dt_utc = dt_ist.astimezone(pytz.utc)

    return dt_utc.isoformat().replace("+00:00", "Z")

def get_current_user():
    """
    Fetch the authenticated Calendly user's URI and organization.
    Returns a dict with user_uri and org_uri.
    """
    headers = {"Authorization": f"Bearer {CALENDLY_TOKEN}"}
    url = f"{BASE_CALENDLY_URL}/users/me"
    res = requests.get(url, headers=headers).json()

    user_uri = res["resource"]["uri"]
    org_uri = res["resource"]["current_organization"]

    return {"user_uri": user_uri, "org_uri": org_uri}

# Fetch event types
def get_event_types():
    """
    Fetch Calendly event types for the current authenticated user.
    """
    user = get_current_user()
    headers = {"Authorization": f"Bearer {CALENDLY_TOKEN}"}

    url = f"{BASE_CALENDLY_URL}/event_types"
    params = {"user": user["user_uri"]}

    res = requests.get(url, headers=headers, params=params).json()

    events = []
    for e in res.get("collection", []):
        events.append({
            "uuid": e["uri"].split("/")[-1],
            "name": e.get("name"),
            "duration": e.get("duration"),
            "description": e.get("description", "")
        })

    return events

event_types_tool = StructuredTool.from_function(
    name="fetch_event_types",
    func=get_event_types,
    description=(
        "Fetch the clinic's appointment types from Calendly. "
        "Use this when user asks: what appointment types are available, "
        "or wants to book something but hasn't chosen a type yet."
    )
)


# Fetch Available Slots
def get_available_slots(event_type: str, start_time: str, end_time: str):
    """
    Fetch available slots for a given event type.
    Requires user context.
    """
    user = get_current_user()
    headers = {"Authorization": f"Bearer {CALENDLY_TOKEN}"}
    try:
        event_type_uuid = appointmentType[event_type]
    except KeyError:
        return "Please give proper eventType"

    event_type_uri = f"{BASE_CALENDLY_URL}/event_types/{event_type_uuid}"

    url = f"{BASE_CALENDLY_URL}/event_type_available_times"
    params = {
        "user": user["user_uri"],
        "event_type": event_type_uri,
        "start_time": ist_to_utc(start_time),
        "end_time": ist_to_utc(end_time)
    }

    res = requests.get(url, headers=headers, params=params).json()
    slots = []
    for s in res.get("collection", []):
        slots.append({
            "start": utc_to_ist(s["start_time"]),
        })

    return slots

availability_tool = StructuredTool.from_function(
    name="fetch_availability",
    func=get_available_slots,
    description=(
        "Fetch available booking slots for a given appointment type. "
        "appointmentType accepted Values - [followUp,general,physical,specialist]"
        "Provide start_time, and end_time in YYYY-MM-DD HH:MM AM/PM format."
    )
)

# Create a booking
def create_booking(event_type: str, start_time: str, name: str, email: str):
    """
    Create a Calendly booking.
    Requires user context.
    """
    user = get_current_user()
    headers = {
        "Authorization": f"Bearer {CALENDLY_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        event_type_uuid = appointmentType[event_type]
    except KeyError:
        return "Please give proper eventType"

    url = f"{BASE_CALENDLY_URL}/invitees"

    payload = {
        "event_type": f"{BASE_CALENDLY_URL}/event_types/{event_type_uuid}",
        "start_time": ist_to_utc(start_time),
        "invitee": {
            "email": email, 
            "name": name,
            "timezone":"Asia/Kolkata"
        },
    }

    res = requests.post(url, json=payload, headers=headers).json()
    print('The result is -- ',res)
    if res.get("resource", {}).get('status','') == 'active':
        return "Scheduled Successfully, A mail must have been sent to the given email"
    elif res.get('details',[])[0].get('code') == 'already_filled':
        return "The slot is booked already"
    else:
        return "There was a issue while scheduling, try again later"

booking_tool = StructuredTool.from_function(
    name="create_appointment",
    func=create_booking,
    description=(
        "Schedule an appointment using Calendly. "
        "Provide appointmentType, start_time, patient name & email. "
        "appointmentType accepted Values - [followUp,general,physical,specialist]"
        "Use this ONLY after confirming user-selected slot."
        "Provide start_time in YYYY-MM-DD HH:MM AM/PM format."
    )
)

# print(create_booking("general","2025-11-28 11:00 AM","Shar","shartee07@gmail.com"))
# print(get_available_slots("general",'2025-11-28 10:00 AM','2025-11-29 10:00 AM'))