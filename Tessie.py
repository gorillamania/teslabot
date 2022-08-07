import requests
from loguru import logger


class Tessie:

    tessie_token = state = vin = None

    def __init__(self, tessie_token, vin=None):
        self.tessie_token = tessie_token
        self.vin = vin

    def get_vehicles(self):
        return self.request("vehicles")

    def get_vehicle_state(self):
        if self.state:
            return self.state

        vehicle_states = self.get_vehicles()
        for state in vehicle_states["results"]:
            if self.vin == state["vin"]:
                self.state = state
                return state["last_state"]
        else:
            raise Exception(f"No matching VIN found #{vin}")

    def get_sleep_status(self):
        return self.request("status", self.vin)["status"]

    def wake_up(self):
        sleep_status = self.get_sleep_status(self.vin)
        logger.info(f"Sleep status is {sleep_status}")
        if sleep_status != "awake":
            logger.info("Sending wake up")
            self.request("wake", self.vin)
            logger.success("Awake")

    def request(self, path, vin=None):
        base_url = "https://api.tessie.com/"

        if vin:
            base_url = f"{base_url}/{vin}"

        url = f"{base_url}/{path}"
        logger.info(f"Requesting {url}")

        response = requests.get(url, headers={"Authorization": f"Bearer {self.tessie_token}"})
        response.raise_for_status()
        return response.json()
