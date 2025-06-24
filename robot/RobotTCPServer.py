import asyncio
import logging
import re
from Config import Config

logger = logging.getLogger("RobotTCPServer.RobotTCPServer")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.get("debug_level", "INFO"))
)

class RobotTCPServer:
    def __init__(self, host="0.0.0.0", port=9001):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.running = False
        self.dispatcher = None  # CommandDispatcher присваивает себя сюда

        self.handlers = []

    async def start(self):
        server = await asyncio.start_server(self._on_connect, self.host, self.port)
        logger.info(f"TCP Server started on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

    async def _on_connect(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.running = True
        logger.info("Robot connected")
        try:
            await asyncio.gather(
                self._ping_loop(),
                self._listen_loop()
            )
        except Exception as e:
            logger.exception(f"Connection error: {e}")
        finally:
            self.running = False
            logger.info("Robot disconnected")

    async def _send_raw(self, command: str):
        if not self.writer:
            logger.warning("No connection available for sending")
            return
        self.writer.write((command + "\n").encode())
        await self.writer.drain()
        logger.debug(f"Command sent: {command}")

    async def _ping_loop(self):
        while self.running:
            await asyncio.sleep(5)
            if self.dispatcher:
                try:
                    await self.dispatcher.send("PING", expect_response=True, expected="ALIVE")
                except asyncio.TimeoutError:
                    logger.warning("Ping: timeout waiting for ALIVE")

    async def _listen_loop(self):
        while self.running:
            try:
                data = await self.reader.readline()
                if not data:
                    logger.info("Robot disconnected")
                    break
                decoded = data.decode().strip()
                logger.info(f"Received: {decoded}")

                if self.dispatcher and self.dispatcher.pending_response:
                    future, expected = self.dispatcher.pending_response
                    if not future.done():
                        future.set_result(decoded)
                        continue

                for pattern, handler in self.handlers:
                    logger.debug(f"{pattern} {decoded}")
                    match = pattern.search(decoded)
                    if match:
                            logger.info(f"Detected event from robot: {decoded}")
                            asyncio.create_task(handler(decoded))
                            break
                else:
                    logger.debug(f"Unknown message from robot: {decoded}")

            except Exception as e:
                logger.exception(f"Error in listen_loop: {e}")
                self.running = False
                break
    
    def register_handler(self, pattern: str | re.Pattern, callback):
        """
        pattern — строка или re.Pattern для поиска в сообщении от робота.
        callback — async функция, которая принимает (строку сообщения).
        """
        compiled = re.compile(pattern) if isinstance(pattern, str) else pattern
        self.handlers.append((compiled, callback))
        logger.info(f"Registered handler for: {pattern}")