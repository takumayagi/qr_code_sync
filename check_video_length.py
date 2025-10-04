#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2023 Takuma Yagi <tyagi@iis.u-tokyo.ac.jp>
#
# Distributed under terms of the MIT license.

import os
import os.path as osp
import sys
import gnureadline
import argparse
import subprocess

import pandas as pd


def check_video_length(args, df):

    blacklist = []
    if osp.exists(args.blacklist_path):
        with open(args.blacklist_path, "r") as f:
            for line in f:
                blacklist.append(line.strip("\n"))

    sync_time = max(df["start_timestamp"].tolist())

    start_frames = [row.frame_pos + round((sync_time - row.start_timestamp) * row.fps) for index, row in df.iterrows()]

    nb_crop_frames = min([nb_frames - start_frame for nb_frames, start_frame in zip(df["nb_frames"].tolist(), start_frames)])
    start_seconds = [start_frame / fps for start_frame, fps in zip(start_frames, df["fps"].tolist())]

    month, day = list(map(int, args.date.split("/")))
    out_paths = []
    for (index, row), start_sec in zip(df.iterrows(), start_seconds):
        # date, participant id, task, take, camera
        # 0915_1_1_1_1.mp4
        video_path = osp.join(args.root_dir, row.video_path)
        #video_id = f"{month:02d}_{day:02d}_{row.participant_id:02d}_{row.task:02d}_{row['take']:02d}_{row.camera_id}"
        video_id = f"participant_{row.participant_id:02d}_protocol_{row.task:02d}_take_{row['take']:02d}"
        video_path = osp.join(args.check_dir, f"{video_id}.mp4")

        if not osp.exists(video_path):
            continue

        invalid = False
        for blacklist_id in blacklist:
            if video_id.startswith(blacklist_id):
                invalid = True
        if invalid:
            continue

        command_str = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {video_path}"
        #command_str = f"ffprobe -i {video_path} -y -loglevel error -ss {start_sec} -c:v libx264 -c:a aac -frames:v {nb_crop_frames} -r 30000/1001 {out_path}"
        if int(row.camera_id) in args.process_id_list:
            #print(command_str)
            ret = subprocess.run(command_str.split(" "), encoding='utf-8', stdout=subprocess.PIPE)
            duration = float(ret.stdout)
            #print(int(duration * 30000 / 1001), nb_crop_frames)
            if abs(int(duration * 30000 / 1001) - nb_crop_frames) > 15:
                print(video_path, int(duration * 30000 / 1001), nb_crop_frames)


def main():
    """
    Crop videos via ffmpeg
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir', type=str)  # e.g. /media/yagi/AIP/221013
    parser.add_argument('--date', type=str, default="01/01")
    parser.add_argument('--check_dir', type=str, default="")
    parser.add_argument('--camera_id_list', type=int, nargs="+", default=[1, 2, 3, 4, 5, 6])
    parser.add_argument('--process_id_list', type=int, nargs="*", default=[1, 2, 3, 4, 5, 6])
    parser.add_argument('--vis_id_list', type=int, nargs="+", default=[1, 2, 3, 4, 5, 6])
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--vis', action='store_true')
    parser.add_argument('--blacklist_path', type=str, default="/media/yagi/AIP/blacklist.txt")
    args = parser.parse_args()

    # Remove /
    if args.root_dir.endswith("/"):
        args.root_dir = args.root_dir[:-1]

    print("Target date: {}".format(args.date))
    target_month, target_day = list(map(int, args.date.split("/")))

    summary_path = osp.join(args.root_dir, "summary_{:02d}_{:02d}.csv".format(target_month, target_day))
    if not osp.exists(summary_path):
        print(f"{summary_path} does not exist. Run get_metadata.py first.")
        sys.exit(1)

    df = pd.read_csv(summary_path)
    #print(df)

    # XXX Brute-force
    for pid in range(1, 10+1, 1):
        for task in range(1, 5+1, 1):
            for take in range(1, 10+1, 1):
                sub_df = df.query(f'participant_id == {pid} & task == {task} & take == {take}')
                if len(sub_df) == 0:
                    continue
                #print(f"Participant id: {pid}, Task: {task}, Take: {take}")
                check_video_length(args, sub_df)


if __name__ == "__main__":
    main()
