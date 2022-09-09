from autovent import autovent
from utils import f2c
import arrow, json


def test_stale_data(requests_mock):

    mock_data = json.loads(open("tests/mock_data/parked.json").read())

    # Stale data
    pacific_yesterday = arrow.utcnow().shift(days=-1).to("US/Pacific")
    mock_data["drive_state"]["timestamp"] = pacific_yesterday.replace(hour=0).timestamp() * 1000  # midnight
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) is None, "Should leave the car sleeping at night"

    mock_data["drive_state"]["timestamp"] = pacific_yesterday.replace(hour=12).timestamp() * 1000  # noon
    requests_mock.get("https://api.tessie.com/dummy_vin/status", text='{"status": "asleep"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/wake", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) is None, "Should wake up the car during the day"


def test_autovent(requests_mock):

    mock_data = json.loads(open("tests/mock_data/parked.json").read())
    mock_data["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000

    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) == 0, "Initial load should do nothing"

    # Conditions
    mock_data["drive_state"]["speed"] = 10
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, None) is None, "Should not vent if the car is moving"
    mock_data["drive_state"]["speed"] = None

    # Let's make it hot
    requests_mock.post("https://api.twilio.com/2010-04-01/Accounts/ACXXX/Messages.json", text='{"sid": "SMXXX"}')
    mock_data["climate_state"]["inside_temp"] = f2c(95)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/status", text='{"status": "awake"}')
    requests_mock.get("https://api.tessie.com/dummy_vin/command/vent_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == -1, "Windows should roll down"

    # Windows should be left alone
    mock_data["vehicle_state"]["rd_window"] = 1
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == 0, "Windows should stay down"

    # Let's cool it down
    mock_data["climate_state"]["inside_temp"] = f2c(85)
    requests_mock.get("https://api.tessie.com/dummy_vin/state", text=json.dumps(mock_data))
    requests_mock.get("https://api.tessie.com/dummy_vin/command/close_windows", text='{"result": true }')
    assert autovent("dummy_vin", "dummy_tessie_token", 90, "+18005551212") == 1, "Windows should roll back up"
