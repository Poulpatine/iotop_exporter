import argparse
from logger import logging
import time
from psutil import Process, AccessDenied, process_iter
from prometheus_client import start_http_server, Gauge


def process_request(command):
    pidlist = []
    for proc in process_iter():
        if proc.name() == command:
            pidlist.append(proc.pid)

    for pid in pidlist:
        process = Process(pid)
        try:
            ios = process.io_counters()
            for iotype in ios._fields:
                io_process.labels(io_type=iotype, pid=pid,
                                  cmd=command).set(getattr(ios, iotype))
        except AccessDenied:
            logging.error("unable to access to PID %s stats" % pid)
    return io_process


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch an Iotop exporter')
    parser.add_argument('-p',
                        '--port',
                        type=int,
                        default=9099,
                        help='default listening port of exporter')
    parser.add_argument('-c',
                        '--command',
                        type=str,
                        help='command to monitor')
    args = parser.parse_args()
    # Start up the server to expose the metrics.
    start_http_server(args.port)
    # Generate some requests.
    io_process = Gauge('io_process', 'Process IO',
                       ['io_type', 'pid', 'cmd'])
    while True:
        process_request(args.command)
        time.sleep(5)
