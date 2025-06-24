
from RobotTCPServer import RobotTCPServer

class Robot(RobotTCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Дополнительная инициализация

    def register_commands(self):
        # Реализуйте регистрацию команд и хэндлеров
        self.register_handler(r'echo*', self.echo)
        # Добавьте свои команды

    async def echo(self, data):
        # Пример реализации обработчика команды
        return f"Echo: {data}"
    

from fastapi import FastAPI, Query
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio

from CommandDispatcher import CommandDispatcher


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем TCP сервер в фоне
    asyncio.create_task(robot.start())
    yield

app = FastAPI(
    title="Robot Service API",
    description="API для управления роботом",
    root_path="/api/robot",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

robot = Robot()         # Используем наш класс Robot
robot.register_commands() # Регистрируем команды и хэндлеры
dispatcher = CommandDispatcher(robot)

@app.post("/send")
async def send_command(
    command: str = Query(...),
    expect_response: bool = Query(default=True)
):
    result = await dispatcher.send(command, expect_response=expect_response)
    return {"status": "sent", "response": result}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8002)