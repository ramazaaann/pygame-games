"""Measures the running server: tick rate, jitter, message size, bandwidth, input latency.

Usage:  python3 server.py            (terminal 1)
        python3 benchmark.py [host]  (terminal 2)
"""
import select
import socket
import statistics
import sys
import time

from protocol import PORT, decode, encode

DURATION = 15  # max seconds of race to sample (a race ends earlier if both cars crash)


def connect(host, name):
    s = socket.create_connection((host, PORT), timeout=10)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.sendall(encode({"t": "join", "name": name}))
    return s


class Reader:
    def __init__(self, sock):
        self.sock, self.buf = sock, b""

    def messages(self):
        data = self.sock.recv(65536)
        if not data:
            raise ConnectionError("server closed the connection")
        self.buf += data
        out = []
        while b"\n" in self.buf:
            line, self.buf = self.buf.split(b"\n", 1)
            if line:
                out.append((time.perf_counter(), len(line) + 1, decode(line)))
        return out


def main():
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    a, b = connect(host, "bench-A"), connect(host, "bench-B")
    ra, rb = Reader(a), Reader(b)
    time.sleep(0.3)
    a.sendall(encode({"t": "ready"}))
    b.sendall(encode({"t": "ready"}))

    stamps, sizes, latencies = [], [], []
    started, sent_at, last_x = None, None, None
    toggle = False
    finished = False
    while not finished:
        readable, _, _ = select.select([a, b], [], [], 2)
        if not readable:
            break
        if b in readable:
            rb.messages()  # keep the second client's socket drained
        if a not in readable:
            continue
        for t, size, msg in ra.messages():
            if msg.get("t") == "over":
                finished = True
            if msg.get("t") != "state":
                continue
            if started is None:
                started = t
            stamps.append(t)
            sizes.append(size)
            me = next(p for p in msg["p"] if p["s"] == 0)
            if sent_at is not None and last_x is not None and me["x"] != last_x:
                latencies.append((t - sent_at) * 1000)
                sent_at = None
            last_x = me["x"]
            # every ~1 s press a key and time how long until the car moves
            if sent_at is None and len(stamps) % 30 == 0:
                toggle = not toggle
                a.sendall(encode({"t": "input", "l": toggle, "r": not toggle, "turbo": False}))
                sent_at = time.perf_counter()
        if started is not None and time.perf_counter() - started > DURATION:
            break

    gaps = [(y - x) * 1000 for x, y in zip(stamps, stamps[1:])]
    gaps_sorted = sorted(gaps)
    elapsed = stamps[-1] - stamps[0]
    print(f"samples:            {len(stamps)} snapshots in {elapsed:.1f}s")
    print(f"tick rate:          {len(stamps) / elapsed:.2f} Hz")
    print(f"tick interval:      mean {statistics.mean(gaps):.1f} ms, "
          f"p95 {gaps_sorted[int(len(gaps) * .95)]:.1f} ms, max {max(gaps):.1f} ms")
    print(f"snapshot size:      mean {statistics.mean(sizes):.0f} B, max {max(sizes)} B")
    print(f"bandwidth/client:   {sum(sizes) / elapsed / 1024:.1f} KB/s")
    if latencies:
        lat = sorted(latencies)
        print(f"input -> car moves: median {statistics.median(lat):.1f} ms, "
              f"p95 {lat[int(len(lat) * .95)]:.1f} ms ({len(lat)} samples)")


if __name__ == "__main__":
    main()
