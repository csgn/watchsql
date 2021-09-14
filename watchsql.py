import os
import sys
import hashlib
import argparse
import time


def hash(filename: str):
    h = hashlib.sha256()
    b = bytearray(128*1024)
    mv = memoryview(b)

    with open(filename, 'rb', buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])

    return h.hexdigest()


def exec(database: str, filename: str) -> None:
    os.system(f"psql {database} -c '\i {filename}'")


def mon(database: str, filename: str, reload: int) -> None:
    previous_hash = hash(filename)

    while True:
        current_hash = hash(filename)

        if previous_hash != current_hash:
            exec(database, filename)
            print("PROGRAM WAS CHANGED")
            previous_hash = current_hash

        time.sleep(reload)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", type=str)
    parser.add_argument("-f", "--file", type=str)
    parser.add_argument("-r", "--reload", type=int)
    args = parser.parse_args()


    mon(args.database, args.file, args.reload)

