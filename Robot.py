import logging
logger = logging.getLogger()

import time
from threading import Thread, Event
from Config import Config
from RobotConnection import RobotConnection

# Настройка логирования (если ещё не настроена в основном модуле)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

class Robot(Thread):
    
    def __init__(self):
        super().__init__()
        # Загружаем конфигурацию и используем её параметры
        logger.debug("Loading configuration.")
        Config.init()
        self.connection = RobotConnection()
        self._request_pending = False
        
        self.stop_event = Event()
        self.ping_interval = Config.get('ping_interval')
        logger.info(f'Initialized robot TCP/IP handler class with host {Config.get("host")} and port {Config.get("port")}')

    def run(self):
        logger.debug("Robot thread started.")
        while not self.stop_event.is_set():
            logger.debug("Entering main loop cycle.")
            if not self.connection.connected:
                logger.debug("Robot not connected, attempting connection.")
                try:
                    self.connection.connect()
                    logger.info("Connection attempt successful.")
                except ConnectionRefusedError as e:
                    logger.error(f'Connection error: {e}')
            else:
                logger.debug("Robot is connected; processing commands.")
                try:
                    while self._request_pending:
                        logger.warning('Another request already pending, waiting for ping')
                        time.sleep(0.1)  # Sleep for 100ms
                    if not self._request_pending:
                        self._request_pending = True
                        logger.debug("Sending PING command.")
                        self.connection.send('PING')
                    response = self.connection.receive()
                    logger.debug(f'Received response: {response}')
                    if response is None:
                        logger.warning("No response received; marking connection as disconnected.")
                        self.connection.connected = False
                    self._request_pending = False
                except Exception as e:
                    logger.error(f'Error during connection check: {e}')
                    self.connection.connected = False
                    self._request_pending = False
                finally:
                    logger.debug(f'Waiting for {self.ping_interval} seconds before next iteration.')
                    self.stop_event.wait(self.ping_interval)
        logger.info('Robot thread stopped.')

    def stop(self):
        self.stop_event.set()
        logger.info('Robot thread stop signal set.')

    def __send_command(self, command, no_response=False):
        logger.debug(f'Entering __send_command with command: {command} and no_response: {no_response}')
        pending_attempts = 0
        while self._request_pending:
            logger.warning('PING request already pending, waiting...')
            if pending_attempts > 10:
                logger.error('Max attempts reached, aborting command send...')
                break
            pending_attempts += 1
            time.sleep(0.1)
        try:
            self._request_pending = True
            logger.debug(f'Sending command: {command}')
            self.connection.send(command)
            if no_response:
                logger.debug("No response expected; returning immediately.")
                self._request_pending = False
                return None
            response = self.connection.receive()
            logger.debug(f'Command response: {response}')
            self._request_pending = False
            return response
        except Exception as e:
            logger.error(f'Error sending command: {e}')
            self._request_pending = False
            return None

    def send_start(self):
        logger.info("send_start command invoked.")
        return self.__send_command('START', no_response=True)
    
    def wait_response(self, timeout=60):
        logger.info("wait_response command invoked.")
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.connection.receive(no_request=True)
            if response:
                logger.debug(f'Received response in wait_response: {response}')
                return response
            time.sleep(0.1)
        logger.warning('Timeout waiting for response from robot.')
        return None

if __name__ == '__main__':
    import time
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    logger.debug("Main script started. Creating Robot instance.")
    robot_handler = Robot()
    robot_handler.start()
    try:
        while not robot_handler.connection.connected:
            logger.info('Waiting for robot to connect...')
            time.sleep(1)
        time.sleep(5)
        robot_handler.send_start()
        robot_handler.wait_response(timeout=1000)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Stopping robot handler.")
        robot_handler.stop()
        robot_handler.join()
    logger.debug("Main script ended.")
