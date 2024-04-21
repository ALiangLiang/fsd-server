import asyncio

from uvicorn.server import Server, Config

from training_server import training_server
from api_server import app


HOST = '0.0.0.0'


async def main():
    fsd_server = training_server
    api_server_config = Config(
        app,
        host=HOST,
        log_level="info",
        reload=True
    )
    api_server = Server(config=api_server_config)
    api_server_config.setup_event_loop()
    await asyncio.gather(
        fsd_server.serve(),
        api_server.serve()
    )

if __name__ == '__main__':
    asyncio.run(main())
