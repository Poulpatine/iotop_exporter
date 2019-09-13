import time
import psutil
from prometheus_client import start_http_server, Gauge


def process_request():
    command = 'java'
    pidlist = []
    for proc in psutil.process_iter():
        if proc.name() == command:
            pidlist.append(proc.pid)

    for pid in pidlist:
        process = psutil.Process(pid)
        ios = process.io_counters()
        for iotype in ios._fields:
            io_process.labels(io_type=iotype, pid=pid,
                              cmd=command).set(getattr(ios, iotype))
    return io_process


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    io_process = Gauge('io_process', 'Process IO',
                       ['io_type', 'pid', 'cmd'])
    while True:
        process_request()
        time.sleep(5)
