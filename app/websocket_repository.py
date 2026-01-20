import logging
from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, status
from pydantic import ValidationError
import aiohttp
from typing import TYPE_CHECKING
import json
import asyncio
import traceback

from app.db import get_db




logger = logging.getLogger("WebSocket Repository")


class WebSocketRepository:

    _connections: dict[str, "WebSocketRepository"] = {}
    _lock = asyncio.Lock()

    FOR_TO = {
        CommandCommunicationEnum.JOIN_CHAT: JoinChat,
        CommandCommunicationEnum.SEND_MENSAGE: SendMensage,
        CommandCommunicationEnum.PING: Ping,
    }

    def __init__(
        self,
        websocket: WebSocket,
        redis: get_db,
      
    ):
        self.__instance = websocket
        self._db = redis
        self._player_id = None
        self.process_await = False


    async def connect(self):
        await self.__instance.accept()

    async def send(self, data: EventCommunicationAbstract):
        try:
            await self.__instance.send_bytes(data.get_message_to_client())
        except (WebSocketDisconnect, RuntimeError) as e:
            logger.warning(f"Websocket is closed and cannot send data type: {type(e)}")
        except Exception as e:
            logger.error("Error to send data", extra={"error": str(e)})
            raise e

    async def remove_connection(self):
        if self._player_id:
            async with WebSocketRepository._lock:
                WebSocketRepository._connections.pop(self._player_id, None)

    async def server_disconnect(self, code: int = status.WS_1000_NORMAL_CLOSURE):
        try:
            await self.__instance.close(code)
        except RuntimeError:
            logger.error("Error:", exec_info=True)
            logger.error("Websocket is closed and cannot disconnect")

    async def consume_command(self):
        while True:
            try:
                instance: "CommandCommunicationAbstract" = await self.__queue.get()
                self.process_await = True
                await instance.execute_action(self)
                self.__queue.task_done()
            except asyncio.CancelledError:
                break
            finally:
                self.process_await = False

    async def wait_command(self):
        async for data in self.__instance.iter_bytes():
            communication = self.unravel_payload(data)
            await self.__queue.put(communication)

    def unravel_payload(self, data: bytes):
        try:
            return self.FOR_TO[data[0]](**json.loads(data[1:]))
        except (KeyError, ValidationError) as e:
            logger.error("Error to unravel payload", extra={"error": str(e)})
            raise WebSocketException(status.WS_1007_INVALID_FRAME_PAYLOAD_DATA) from e

    @staticmethod
    def get_connection(player_id: str) -> "WebSocketRepository | None":
        return WebSocketRepository._connections.get(player_id)
