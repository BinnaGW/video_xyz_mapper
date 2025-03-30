import streamlit as st
import cv2
import pandas as pd
import os
from datetime import timedelta
from pymediainfo import MediaInfo

st.title("Video to XYZ Mapper")

video_file = st.file_uploader("Upload Video", type=['mp4', 'mov'])

if video_file:
    with open(video_file.name, "wb") as f:
        f.write(video_file.read())

    video_capture = cv2.VideoCapture(video_file.name)

    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    interval_seconds = st.number_input("Frame Extraction Interval (seconds)", value=1, min_value=1)
    frames_interval = int(fps * interval_seconds)

    output_dir = 'extracted_frames'
    os.makedirs(output_dir, exist_ok=True)

    extracted_data = []
    current_frame = 0
    extracted_frame_number = 0

    with st.spinner('Processing video...'):
        while current_frame < frame_count:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            success, frame = video_capture.read()
            if not success:
                break

            frame_filename = f'frame_{extracted_frame_number}.jpg'
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)

            # Example extraction - replace this with actual GPS metadata extraction
            gps_data = {'Longitude': 34.0 + extracted_frame_number * 0.00001,
                        'Latitude': 32.0 + extracted_frame_number * 0.00001,
                        'Elevation': 100 + extracted_frame_number}

            timestamp = timedelta(seconds=(current_frame / fps))

            extracted_data.append({
                'Frame': extracted_frame_number,
                'Image Path': frame_path,
                'Longitude (X)': gps_data['Longitude'],
                'Latitude (Y)': gps_data['Latitude'],
                'Elevation (Z)': gps_data['Elevation'],
                'Timestamp': str(timestamp)
            })

            extracted_frame_number += 1
            current_frame += frames_interval

        video_capture.release()

        df = pd.DataFrame(extracted_data)
        csv_path = 'extracted_frames_data.csv'
        df.to_csv(csv_path, index=False)

    st.success('Processing complete!')

    st.download_button("Download CSV", data=df.to_csv(index=False), file_name='extracted_frames_data.csv')
