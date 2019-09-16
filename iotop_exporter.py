import argparse
import re
import time
from logger import logging
from psutil import Process, AccessDenied, process_iter
from prometheus_client import start_http_server, Gauge


def process_request(command):
    pidlist = []
    for proc in process_iter():
        if re.match(command, proc.name()):
            pidlist.append(proc.pid)

    for pid in pidlist:
        process = Process(pid)
        try:
            ios = process.io_counters()
            for iotype in ios._fields:
                IO_PROCESS.labels(io_type=iotype, pid=pid,
                                  cmd=process.name()).set(getattr(ios, iotype))
        except AccessDenied:
            logging.error("unable to access to PID %s stats" % pid)
    return IO_PROCESS


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(description='Launch an Iotop exporter')
    PARSER.add_argument('-p',
                        '--port',
                        type=int,
                        default=9099,
                        help='default listening port of exporter')
    PARSER.add_argument('-c',
                        '--command',
                        type=str,
                        help='command to monitor')
    ARGS = PARSER.parse_args()
    # Start up the server to expose the metrics.
    start_http_server(ARGS.port)
    # Generate some requests.
    IO_PROCESS = Gauge('io_process', 'Process IO',
                       ['io_type', 'pid', 'cmd'])
    while True:
        process_request(ARGS.command)
        time.sleep(5)
