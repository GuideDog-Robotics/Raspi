# detection_memory.py

import time


class DetectionMemory:
    """
    YOLO가 순간적으로 객체를 놓쳤을 때,
    마지막으로 감지된 객체 정보를 짧은 시간 동안만 기억하는 클래스입니다.

    중요 동작:
    - 현재 프레임에서 객체가 감지되면 현재 감지 결과를 그대로 사용합니다.
    - 현재 프레임에서 객체가 감지되지 않으면 hold_time_sec 동안 이전 감지 결과를 잠깐 사용합니다.
    """

    def __init__(self, hold_time_sec=0.5):
        # 감지 결과를 유지할 시간
        # 예: 0.5초 동안만 이전 감지 결과를 기억
        self.hold_time_sec = hold_time_sec

        # 마지막으로 감지된 객체 정보 저장
        self.last_detections = []

        # 마지막으로 객체가 감지된 시간 저장
        self.last_seen_time = 0

    def update(self, detections):
        # 현재 시간 저장
        now = time.time()

        # 현재 프레임에서 YOLO가 객체를 감지한 경우
        if len(detections) > 0:
            # 현재 감지 결과를 메모리에 저장
            # det.copy()를 사용하는 이유:
            # 원본 detections가 다른 곳에서 수정되어도 메모리 값이 영향을 받지 않게 하기 위해
            self.last_detections = [det.copy() for det in detections]

            # 마지막 감지 시간을 현재 시간으로 업데이트
            self.last_seen_time = now

            # 현재 감지 결과를 그대로 반환
            return detections

        # 현재 프레임에서 YOLO가 아무 객체도 감지하지 못한 경우
        # 마지막 감지 후 hold_time_sec 이내라면 이전 감지 결과를 잠깐 사용
        if now - self.last_seen_time <= self.hold_time_sec:
            # 저장된 감지 결과를 복사해서 반환
            return [det.copy() for det in self.last_detections]

        # 마지막 감지 후 hold_time_sec 시간이 지났다면
        # 더 이상 객체가 있다고 판단하지 않고 메모리를 비움
        self.last_detections = []

        # 감지된 객체가 없다고 반환
        return []