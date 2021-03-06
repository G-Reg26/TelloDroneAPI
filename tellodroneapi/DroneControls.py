import asyncio
from typing import Coroutine, Any

from tellodroneapi.Drone import Drone, DroneResponse


class DroneControl:
    """
    Handles controlling a drone and its actions such as general movement.
    """
    def __init__(self, drone: Drone, run_controls_async: bool = True):
        """
        DroneControl constructor
        :param drone: The drone these controls will be relayed to.
        :param run_controls_async: True if controls should return the awaited response from the
            drone device and False if commands should immediately resolve, returning None.
        """
        self.drone = drone
        self.run_controls_async = run_controls_async

        self.time_between_commands = 1
        """
        The amount of time in seconds to wait before commands. Sending commands too quickly leads
        to the drone ignoring them sometimes.
        """

    async def takeoff(self) -> DroneResponse:
        return await self._send_control("takeoff")

    async def land(self) -> DroneResponse:
        return await self._send_control("land")

    async def land_emergency(self) -> DroneResponse:
        """
        Stops all motors immediately.
        :return: DroneResponse
        """
        return await self._send_control("emergency")

    def _should_run_async(self, command: Coroutine) -> Coroutine[Any, Any, DroneResponse]:
        """
        Checks if run_controls_async is True and returns the command passed in if
        it is, otherwise returning an async-wrapped None value
        :param command: A Coroutine command that should be awaited if run_controls_async is True.
        :return: Coroutine[DroneResponse]
        """
        if self.run_controls_async:
            return command
        else:
            return async_none()

    async def _send_control(self, message: str) -> DroneResponse:
        """
        Sends a control command to the associated drone and returns an async future that is either
        the proper response from the drone, or None is should_run_async is false. If
        time_between_commands has been set, then this will not return until that time has passed.

        :param message: str A control command
        :return: The response from the drone, or None if run_controls_async is false.
        """
        command = self.drone.send_command_and_await(message)
        await asyncio.sleep(self.time_between_commands)
        return await self._should_run_async(command)


async def async_none():
    """
    Async wrapper around the None primitive. If run_controls_async is set to False,
    controls will return None immediately instead of the normal string response from
    the drone.
    :return: None
    """
    return None
