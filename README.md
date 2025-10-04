# Usage

## Prerequisites
The mp4 files should be stored as follows:
```
video_dir/
    1/
        XXX.mp4
    2/
        YYY.mp4
    3/
        ZZZ.mp4
```
The mp4 files should be stored in the folder for corresponding camera id.


## QR Code display
```
python video_qr_code.py --pid 1 --task 1 --take 1
```

## QR Code recognition test
```
python recog_qr_code.py <video_path>
```

## Get metadata
```
python get_metadata <input_dir_with_mp4> --date <recording_date>
# Example
python get_metadata.py /media/yagi/AIP/221124/ --date 11/24
```

## Perform temporal sync
```
python sync_videos_v2.py <input_dir_with_mp4> --out_dir <output_dir> --date <recording_date> --camera_id_list <list of camera ids>
# Example
python sync_videos_v2.py ~/data/221208/ --out_dir ~/data/221208_sync/ --date 12/08 --camera_id_list 2
# Specify --vis for visualization
python sync_videos_v2.py <input_dir_with_mp4> --out_dir <output_dir> --date <recording_date> --camera_id_list <list of camera ids> --vis
```

