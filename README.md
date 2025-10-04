# QR code based temporal sync

This repository implements a simple temporal synchronization across multiple cameras

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
At the beginning of the recording, display this QR code in fromt of each camera to get synchronized timestamps.
```
python video_qr_code.py --pid 1 --task 1 --take 1
```

## QR Code recognition test
```
python recog_qr_code.py <video_path>
```

## Get metadata
This code will perform QR code detection to determine when to crop.
```
python get_metadata <input_dir_with_mp4> --date <recording_date>
# Example
python get_metadata.py ./videos_251001/ --date 10/01
# If you want to debug QR code detection
python get_metadata.py ./videos_251001/ --date 10/01 --debug
# You may change the scan duration if QR code is shown later
python get_metadata.py ./videos_251001/ --date 10/01 --max_scan_length 30.0
```

## Perform temporal sync
```
python sync_videos.py <input_dir_with_mp4> --out_dir <output_dir> --date <recording_date> --camera_id_list <list of camera ids>
# Example
python sync_videos.py ./videos_251001/ --out_dir ./251001_sync/ --date 10/01 --camera_id_list 2
# Specify --vis for visualization
python sync_videos.py <input_dir_with_mp4> --out_dir <output_dir> --date <recording_date> --camera_id_list <list of camera ids> --vis
```

## Tips
* If the FOV of the videos differs across cameras (e.g., first-person vs. third-person cameras), you may resize the frames to make QR code detection works.
* You may need undistortion if your video include distortion, which may harms the QR code detection.
