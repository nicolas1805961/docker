#!/usr/bin/env python3

import requests
import sys

# image = sys.argv[1]
# r = requests.post(
#     "http://localhost:5000/dewarp", files={"image": open(image, "rb")}
# ).json()
# print(r)


print(
    requests.post(
        "http://localhost:5000/dewarp", files={"image": open(sys.argv[1], "rb")}
    ).json()
)
