import os
import asyncio
import argparse

from uvicorn.server import Server, Config

from training_server import training_server
from api_server import app


HOST = '0.0.0.0'


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ssl-key', dest='key', default=None)
    parser.add_argument('--ssl-cert', dest='cert', default=None)
    args = parser.parse_args()

    fsd_server = training_server
    api_server_config = Config(
        app,
        host=HOST,
        log_level='info',
        reload=True,
        ssl_keyfile=args.key,
        ssl_certfile=args.cert,
    )
    api_server = Server(config=api_server_config)
    api_server_config.setup_event_loop()
    await asyncio.gather(
        fsd_server.serve(),
        api_server.serve()
    )

if __name__ == '__main__':
    asyncio.run(main())
