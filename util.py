import gzip
import json
import sys

def read_json_lines(file, limit=sys.maxsize):
    with gzip.open(file, mode="rb") if file.endswith('.gz') else open(file, mode="rb") as f:
        counter=0
        for line in f:
            counter += 1
            if counter > limit: break
            yield json.loads(line.decode('utf-8'))
