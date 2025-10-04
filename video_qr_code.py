#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2025 Takuma Yagi <takuma.yagi@aist.go.jp>
#
# Distributed under terms of the MIT license.

import os
import time
import datetime
import argparse

import numpy as np
import cv2
import qrcode

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', type=int, default=1)
    parser.add_argument('--task', type=int, default=1)
    parser.add_argument('--take', type=int, default=1)
    parser.add_argument('--delay', type=int, default=1)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if not args.debug:
        cv2.namedWindow('screen', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    current = datetime.datetime.now()

    width, height = 1920, 1080
    base_img = np.ones((height, width), dtype=np.uint8) * 255
    print_str = "{}/{}".format(current.month, current.day)
    cv2.putText(base_img, print_str, (20, 870), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 0, 0), 8, cv2.LINE_4)
    print_str = "Participant {} Task {} Take {}".format(args.pid, args.task, args.take)
    cv2.putText(base_img, print_str, (20, 1020), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 0, 0), 8, cv2.LINE_4)

    img = base_img.copy()
    print_str = "Press key to start"
    cv2.putText(img, print_str, (420, 500), cv2.FONT_HERSHEY_SIMPLEX, 3.5, (0, 0, 0), 8, cv2.LINE_4)

    cv2.imshow("screen", img)
    key = cv2.waitKey(0)

    start_time = datetime.datetime.now()

    while True:
        img = base_img.copy()
        current = datetime.datetime.now()
        delta = current - start_time

        # Data configuration
        # csv format
        # delta (seconds)
        # local date
        # participant id
        # task
        # take
        elapsed = delta.seconds + delta.microseconds * 10e-7
        date_str = ",".join([
            str(current.year),
            str(current.month),
            str(current.day),
            str(current.hour),
            str(current.minute),
            str(current.second)
        ])
        data_str = ",".join(["{:.6f}".format(elapsed), date_str, str(args.pid), str(args.task), str(args.take)])

        # Generate QR code
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=20,
            border=0
        )
        qr.add_data(data_str)
        qr_img = np.array(qr.make_image(), dtype=np.uint8) * 255
        h, w = qr_img.shape

        # Display necessary info
        img[height//2-h//2-180:height//2-h//2+h-180, width//2-w//2:width//2-w//2+w] = qr_img
        print_str = "{:03.3f}".format(elapsed)
        cv2.putText(img, print_str, (650, 870), cv2.FONT_HERSHEY_SIMPLEX, 7.0, (0, 0, 0), 10, cv2.LINE_4)
        cv2.imshow("screen", img)
        key = cv2.waitKey(args.delay)
        if key & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()



if __name__ == "__main__":
    main()
