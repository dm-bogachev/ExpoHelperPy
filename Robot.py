import logging
logger = logging.getLogger()

import time
from threading import Thread, Event
from Config import Config
from RobotConnection import RobotConnection

class Robot(Thread):
    
    def __init__(self):
        super().__init__()
        # Загружаем конфигурацию и используем её параметры
        Config.load()
        self.config = Config._config
        self.connection = RobotConnection()
        self._request_pending = False
        
        self.stop_event = Event()
        self.ping_interval = self.config['ping_interval']
        logger.info(f'Initialized robot TCP/IP handler class with host {self.config["host"]} and port {self.config["port"]}')

    def run(self):
        while not self.stop_event.is_set():
            if not self.connection.connected:
                try:
                    self.connection.connect()
                except ConnectionRefusedError as e:
                    logger.error(e)
            else:
                try:
                    while self._request_pending:
                        logger.warning('Another request already pending, waiting for ping')
                        time.sleep(0.1)  # Sleep for 100ms
                    if not self._request_pending:
                        self._request_pending = True
                        self.connection.send('PING')
                    response = self.connection.receive()
                    if response is None:
                        self.connection.connected = False
                    self._request_pending = False
                except Exception as e:
                    logger.error(f'Error during connection check: {e}')
                    self.connection.connected = False
                    self._request_pending = False
                finally:
                    self.stop_event.wait(self.ping_interval)
        logger.info('Robot thread stopped')

    def stop(self):
        self.stop_event.set()
        logger.info('Robot thread stopped')

    def __send_command(self, command, no_response=False):
        pending_attempts = 0
        while self._request_pending:
            logger.warning('PING request already pending, waiting...')
            if pending_attempts > 10:
                logger.error('Max attempts reached, aborting...')
                break
            pending_attempts += 1
            time.sleep(0.1)  
        try:
            self._request_pending = True
            self.connection.send(command)
            if no_response:
                self._request_pending = False
                return None
            response = self.connection.receive()
            self._request_pending = False
            return response
        except Exception as e:
            logger.error(f'Error sending command: {e}')
            self._request_pending = False
            return None

    # Примеры команд:
    # def send_pick(self, model, coordinates):
    #     if len(coordinates) == 2:
    #         x, y = coordinates
    #         return self.__send_command(f'PICK,{model},{2},{x},{y}')
    #     else:
    #         x, y, a = coordinates
    #         return self.__send_command(f'PICK,{model},{3},{x},{y},{a}')
    #
    # def send_measurement_request(self, measurement_result):
    #     result = 'OK' if measurement_result else 'NG'
    #     return self.__send_command(f'MEASUREMENT,{result}')

if __name__ == '__main__':
    import time
    logging.basicConfig()
    logger.setLevel(logging.DEBUG)
    robot_handler = Robot()
    robot_handler.start()
    while True:
        while not robot_handler.connection.connected:
            logger.info('Waiting for robot to connect...')
            time.sleep(1)
        logger.info('Robot connected')
        # Пример вызова команд (функции send_pick/send_measurement_request активировать при необходимости)
        # logger.info(robot_handler.send_pick(1, (2, 3)))
        # logger.info(robot_handler.send_measurement_request(True))
        time.sleep(5)
