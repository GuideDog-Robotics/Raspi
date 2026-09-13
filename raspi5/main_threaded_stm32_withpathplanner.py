# main_threaded_stm32.py

import time
import cv2

from camera import setup_camera, release_camera
from detector import ObjectDetector
from visualizer import setup_window, draw_detections, draw_fps, draw_command, draw_distance, show_frame
from fps_counter import FPSCounter
from stm32_comm import STM32Comm
from path_planner import PathPlanner
from detection_memory import DetectionMemory
from find_port import find_stm32_port
from config import (
    COMMAND_INTERVAL_SEC,
    USE_STM32,
    FAKE_DISTANCES_CM,
    DETECTION_MEMORY_HOLD_TIME_SEC,
    COMMAND_TO_CHAR,
)



def main():
    cap = setup_camera()
    detector = ObjectDetector()
    fps_counter = FPSCounter()
    path_planner = PathPlanner()
    detection_memory = DetectionMemory(hold_time_sec=DETECTION_MEMORY_HOLD_TIME_SEC)
    # STM32과 Serial 통신을 시작
    if USE_STM32:
        stm32_port = find_stm32_port()

        stm32 = STM32Comm(
            port=stm32_port,
            baudrate=115200,
            timeout=0.01
        )

        stm32.start()
    else:
        stm32 = None
        print("STM32 disabled. Running with fake distances.")

    setup_window()  # 윈도우 없이 실행할 때는 주석 처리

    # 명령 중복 전송 방지 변수
    last_command = None
    last_command_time = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("Camera frame not received.")
                break

            # 1. 현재 프레임에서 객체 탐지
            raw_detections = detector.detect(frame)

            # 1-1. YOLO가 잠깐 놓친 객체를 몇 프레임 동안 기억
            detections = detection_memory.update(raw_detections)

            # 2. STM32에서 가장 최근 초음파 거리값 가져오기
            if USE_STM32:
                distances_cm = stm32.get_latest_distances()
            else:
                distances_cm = FAKE_DISTANCES_CM.copy()

            # 3. path planner 모듈로 이동 명령 결정
            command, danger = path_planner.update(
                detections=detections,
                distances_cm=distances_cm
            )


            # 4. 명령이 바뀌었고, 최소 전송 간격이 지났을 때만 STM32로 전송
            now = time.time()
            if command != last_command and now - last_command_time >= COMMAND_INTERVAL_SEC:
                stm32_command = COMMAND_TO_CHAR.get(command, "S") # 명령이 매핑에 없으면 "S" (STOP)로 전송

                if USE_STM32:
                    stm32.send_command(stm32_command)
                    print("Sent command:", command, "->", stm32_command, "distance:", distances_cm, "danger:", danger)
                else:
                    print("[TEST MODE] Command:", command, "->", stm32_command, "distance:", distances_cm, "danger:", danger)

                last_command = command
                last_command_time = now

            # 디버깅 출력
            # print("Sensor distances:", distances_cm)             #센서 터미널 출력

            # for det in detections:                               #탐지된 객체 정보 터미널 출력
            #     print(
            #         det["class_name"],
            #         f"{det['confidence']:.2f}",
            #         det["box"],
            #         "center:",
            #         det["center"]
            #     )

            # 화면에 결과 그리기
            frame = draw_detections(frame, detections)
            frame = draw_distance(frame, distances_cm)
            frame = draw_command(frame, command, danger)

            # FPS 출력
            fps = fps_counter.calculate()
            frame = draw_fps(frame, fps)

            show_frame(frame)       # 윈도우 없이 실행할 때는 주석 처리

            key = cv2.waitKey(1)    # 윈도우 없이 실행할 때는 주석 처리
            if key == ord("q"):     # 윈도우 없이 실행할 때는 주석 처리
                break               # 윈도우 없이 실행할 때는 주석 처리

    finally:
        if USE_STM32 and stm32 is not None:
            stm32.stop()

        release_camera(cap)


if __name__ == "__main__":
    main()