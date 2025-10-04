#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2025 Takuma Yagi <takuma.yagi@aist.go.jp>
#
# Distributed under terms of the MIT license.

import os
import os.path as osp
import sys
import time
import datetime
import gnureadline
import argparse
import glob

import numpy as np
import cv2
import zbarlight
from PIL import Image

def get_metadata(args, dir_name, video_path):

    if args.debug:
        print(video_path)

    cap = cv2.VideoCapture(video_path)

    nb_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        print("Invalid fps {}".format(video_path))
        return

    video_length = nb_frames / fps
    if video_length < args.min_length:
        print("Length too short: ({} sec), {}".format(video_length, video_path))
        return

    # XXX A fixed offset to read frames without errors using opencv
    cap.set(cv2.CAP_PROP_POS_FRAMES, args.offset)

    # You may perform spatial calibration to remove distortion
    if args.calib_path != "":
        data = np.load(args.calib_path)
        intrinsics = data["intrinsic_matrix"]
        dist_coeff = data["distCoeff"]
        image_size = (width, height)
        newMat, ROI = cv2.getOptimalNewCameraMatrix(intrinsics, dist_coeff, image_size, alpha=args.crop_alpha, centerPrincipalPoint=1)
        mapx, mapy = cv2.initUndistortRectifyMap(intrinsics, dist_coeff, None, newMat, image_size, m1type=cv2.CV_32FC1)

    found_cnt = 0
    found = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if args.calib_path != "":
            frame = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)
            frame = cv2.resize(frame, (width, height))
        codes = zbarlight.scan_codes(['qrcode'], Image.fromarray(frame))
        found_cnt += 1

        if found_cnt >= args.max_scan_length * fps:
            print("QR code not found: {}".format(video_path))
            break

        if args.debug:
            cv2.imshow("frame", cv2.resize(frame, (1280, int(1280 / width * height))))
            cv2.waitKey(1)

        if (codes is None or len(codes) == 0):
            continue

        found = True
        data_str = codes[0].decode("utf-8")
        break

    frame_pos = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

    cap.release()
    cv2.destroyAllWindows()

    rel_video_path = osp.join(dir_name, osp.basename(video_path))
    if not found:
        return
        # video_path,camera_id,nb_frames,fps,seconds,frame_pos,start_timestamp,year,month,day,hour,minute,second,participant_id,task,take
        # meta_str = ",".join([rel_video_path, dir_name, str(nb_frames), str(fps), str(nb_frames / fps), str(frame_pos)])
    else:
        meta_str = ",".join([rel_video_path, dir_name, str(nb_frames), str(fps), str(nb_frames / fps), str(frame_pos), data_str])
    return meta_str


def main():
    """
    Scan videos to obtain metadata
    Export summary as a csv file
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir', type=str)
    parser.add_argument('--date', type=str, default="01/01")
    parser.add_argument('--ext', type=str, default="MP4")
    parser.add_argument('--dir_name', type=str, default="")
    parser.add_argument('--video_name', type=str, default="")
    parser.add_argument('--calib_path', type=str, default="")
    parser.add_argument('--crop_alpha', type=float, default=0.25)  # Only required when performing undistortion
    parser.add_argument('--offset', type=int, default=50)
    parser.add_argument('--min_length', type=float, default="60.0", help="minimum video length (sec)")
    parser.add_argument('--max_scan_length', type=float, default="10.0", help="maximum scan length (sec)")
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    print("Target date: {}".format(args.date))
    target_month, target_day = list(map(int, args.date.split("/")))

    # Metadata configuration
    # File location
    # Date
    # Participant id
    # Task
    # Take
    meta_strs = []

    for dir_name in sorted(os.listdir(args.root_dir)):
        if args.dir_name != "" and dir_name != args.dir_name:
            continue
        print(dir_name)
        for video_path in sorted(glob.glob(osp.join(args.root_dir, dir_name, f"*.{args.ext}"))):
            if args.video_name != "" and args.video_name != osp.basename(video_path):
                continue
            meta_str = get_metadata(args, dir_name, video_path)
            if meta_str is None:
                continue
            if len(meta_str.split(",")) >= 11:
                month, day = list(map(int, meta_str.split(",")[8:10]))
                if month != target_month or day != target_day:
                    continue
            print(meta_str)
            meta_strs.append(meta_str)

    print("Number of target files: {}".format(len(meta_strs)))
    if len(meta_strs) == 0:
        sys.exit(1)

    if not args.debug:
        out_path = osp.join(args.root_dir, "summary_{:02d}_{:02d}.csv".format(target_month, target_day))
        print(f"Output path: {out_path}")

        header = "video_path,camera_id,nb_frames,fps,seconds,frame_pos,start_timestamp,year,month,day,hour,minute,second,participant_id,task,take"
        with open(out_path, "w") as f:
            for line in [header] + meta_strs:
                f.write(line + "\n")


if __name__ == "__main__":
    main()
