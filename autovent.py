from Tessie import Tessie
import arrow
import click
from utils import c2f, send_sms
from loguru import logger


@click.command()
@click.option("--vin", required=True, help="Tesla VIN number to auto vent")
@click.option("--tessie_token", required=True, help="API access token for Tessie (see tessie.com)")
@click.option(
    "--vent_temp", default=70, help="The threshold for when to roll up/down the windows, degrees in farenheit"
)
@click.option("--notify_phone", help="Send a message to this phone number when the windows are moved")
def autovent(vin, tessie_token, vent_temp, notify_phone):
    """
    Automatically vent the windows to lower cabin temperature
    """

    tessie = Tessie(tessie_token, vin)
    state = tessie.get_vehicle_state()
    climate_state = state["climate_state"]
    vehicle_state = state["vehicle_state"]
    logger.trace(f"Climate state: {climate_state}")
    logger.trace(f"Vehicle state: {vehicle_state}")

    inside_temp = c2f(climate_state["inside_temp"])
    outside_temp = c2f(climate_state["outside_temp"])

    try:
        if tessie.localize_time(arrow.utcnow().shift(hours=-2)) > tessie.localize_time(
            arrow.get(state["drive_state"]["timestamp"])
        ):
            raise ValueError("API data is stale. Car not online?")
        tessie.check_state("drive_state", "speed", lambda v: v == 0, "Car is moving 🛞")
        tessie.check_state("vehicle_state", "is_user_present", lambda v: v == False, "Someone is in the car 🙆")
    except ValueError as e:
        logger.critical(str(e))
        return

    msg = f"Inside temperature is {inside_temp}° and outside temperature is {outside_temp}°."
    logger.info(msg)

    if vehicle_state["rd_window"] != 0:
        logger.info("Windows are down")
        if inside_temp < vent_temp:
            tessie.wake_up(vin)
            tessie.request("command/close_windows", vin)
            logger.success("Windows closed")
            if notify_phone:
                msg += " Windows rolled up. ✅"
                send_sms(notify_phone, msg)
        else:
            logger.info("Leaving windows as is")

    else:
        logger.info("Windows are up")
        if inside_temp > vent_temp and outside_temp < inside_temp:
            tessie.wake_up(vin)
            tessie.request("command/vent_windows", vin)
            logger.success("Windows vented")
            if notify_phone:
                msg += " Windows vented. ✅"
                send_sms(notify_phone, msg)
        else:
            logger.info("Leaving windows as is")


if __name__ == "__main__":
    autovent()
