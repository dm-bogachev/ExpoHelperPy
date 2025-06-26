import asyncio
import logging
from Config import Config

logger = logging.getLogger("RobotTCPServer.CommandDispatcher")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

class CommandDispatcher:
    def __init__(self, tcp_server):
        self.tcp_server = tcp_server
        self.pending_response = None  # (Future, expected_response)
        self.lock = asyncio.Lock()
        self.tcp_server.dispatcher = self

    async def send(self, command: str, expect_response: bool = True, expected: str | None = None) -> str | None:
        async with self.lock:
            logger.debug(f"API command: {command}")
            future = None
            if expect_response:
                future = asyncio.get_event_loop().create_future()
                self.pending_response = (future, expected)
            await self.tcp_server._send_raw(command)
            if future:
                try:
                    result = await asyncio.wait_for(future, timeout=5.0)
                    if expected and result != expected:
                        logger.warning(f"Expected response '{expected}', got '{result}'")
                    return result
                finally:
                    self.pending_response = None
            return None
