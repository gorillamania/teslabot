import json

import arrow

from peakoff import peakoff

TEST_VIN = "5YJ3E1EA8KF326283"


def test_peakoff_conditions(requests_mock):
    mock_data = json.loads(open("tests/mock_data/parked.json").read())
    mock_data["results"][0]["last_state"]["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000

    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    assert (
        peakoff(TEST_VIN, "dummy_tessie_token", "16:00", "21:00", None) is None
    ), "Should do nothing while not plugged in"

    mock_data = json.loads(open("tests/mock_data/supercharging.json").read())
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    assert (
        peakoff(TEST_VIN, "dummy_tessie_token", "16:00", "21:00", None) is None
    ), "Should do nothing while supercharging"


def test_peakoff_toggling(requests_mock):
    mock_data = json.loads(open("tests/mock_data/supercharging.json").read())
    mock_data["results"][0]["last_state"]["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000
    mock_data["results"][0]["last_state"]["charge_state"]["charger_voltage"] = 100
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))

    assert peakoff(TEST_VIN, "dummy_tessie_token", "00:00", "00:00", None) == 0, "Should leave it alone outside of peak"

    requests_mock.get(f"https://api.tessie.com/{TEST_VIN}/command/stop_charging", text='{"result": true }')
    assert peakoff(TEST_VIN, "dummy_tessie_token", "00:00", "23:59", None) == -1, "Should stop charging during peak"

    mock_data["results"][0]["last_state"]["charge_state"]["charging_state"] = "Stopped"
    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    requests_mock.get(f"https://api.tessie.com/{TEST_VIN}/command/start_charging", text='{"result": true }')
    assert peakoff(TEST_VIN, "dummy_tessie_token", "00:00", "00:00", None) == 1, "Should resume charging off peak"


def test_low_battery(requests_mock):
    mock_data = json.loads(open("tests/mock_data/residential_charging.json").read())
    mock_data["results"][0]["last_state"]["drive_state"]["timestamp"] = arrow.utcnow().timestamp() * 1000

    requests_mock.get("https://api.tessie.com/vehicles", text=json.dumps(mock_data))
    assert (
        peakoff(TEST_VIN, "dummy_tessie_token", "00:00", "23:59", None) == 0
    ), "Should leave it charging because the battery is too low to optimize"
