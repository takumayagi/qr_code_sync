#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2025 Takuma Yagi <takuma.yagi@aist.go.jp>
#
# Distributed under terms of the MIT license.

import os
import sys
import time
import datetime
import gnureadline

import numpy as np
import cv2
import zbarlight
from PIL import Image

def main():
    """
    Recognize QR code and obtain the data
    """
    video_path = sys.argv[1]

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 100)

    while True:

        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (1280, 720))
        codes = zbarlight.scan_codes(['qrcode'], Image.fromarray(frame))

        if codes is None or len(codes) == 0:
            pass
        else:
            data_str = codes[0].decode("utf-8")
            delta_str = "{:.4f}".format(float(data_str.split(",")[0]))
            cv2.putText(frame, delta_str, (400, 600), cv2.FONT_HERSHEY_SIMPLEX, 4.0, (0, 0, 255), 6, cv2.LINE_4)
        cv2.imshow("screen", frame)
        key = cv2.waitKey(200)
        if key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
