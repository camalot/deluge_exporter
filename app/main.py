from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
import asyncio
import os
import signal
from concurrent.futures import ProcessPoolExecutor

from libs.colors import Colors
from metrics.exporter import MetricsExporter


def sighandler(signum: int, frame):
    match signum:
        case signal.SIGTERM:
            print(Colors.colorize(Colors.FGYELLOW, "<SIGTERM received>"))
        case signal.SIGINT:
            print(Colors.colorize(Colors.FGYELLOW, "<SIGINT received>"))
    exit(0)


def exporter():
    try:
        EXPORTER_ENABLED = os.environ.get("DE_CONFIG_METRICS_ENABLED", "false").lower() == "true"
        if EXPORTER_ENABLED:
            print("Metrics exporter enabled")
            exporter = MetricsExporter()
            print("Running exporter")
            exporter.run()
        else:
            print(Colors.colorize(Colors.FGYELLOW, "<Metrics exporter disabled>"))
    except KeyboardInterrupt:
        print(Colors.colorize(Colors.FGYELLOW, "<KeyboardInterrupt received>"))
        exit(0)

# if __name__ == '__main__':
#     print("STARTING")
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     try:
#         signal.signal(signal.SIGTERM, sighandler)
#         signal.signal(signal.SIGINT, sighandler)
#         # executor = ProcessPoolExecutor(2)
#         # loop.run_in_executor(executor, exporter)
#         # loop.run_forever()

#         asyncio.run(amain(loop=loop))
#     except KeyboardInterrupt:
#         pass
#     finally:
#         loop.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        signal.signal(signal.SIGTERM, sighandler)
        signal.signal(signal.SIGINT, sighandler)

        executor = ProcessPoolExecutor(2)
        loop.run_in_executor(executor, exporter)
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
