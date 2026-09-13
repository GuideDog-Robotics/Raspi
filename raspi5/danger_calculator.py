# danger_calculator.py

from config import (
    AVOID_DISTANCE_CM,
    BOX_AREA_SCALE,
)

from box_utils import (
    get_box_area,
    get_min_box_area_for_class,
    get_zone,
)


class DangerCalculator:
    """
    YOLO 탐지 결과와 초음파 센서값을 이용해서
    LEFT / CENTER / RIGHT 위험도를 계산하는 모듈
    """

    def calculate(self, detections, distances_cm):
        danger = {
            "LEFT": 0.0,
            "CENTER": 0.0,
            "RIGHT": 0.0,
        }

        # ==============================
        # 1. 카메라 기반 위험도 계산
        # ==============================
        for det in detections:
            box = det.get("box")
            center = det.get("center")

            if box is None or center is None:
                continue

            box_area = get_box_area(box)
            class_name = det.get("class_name")

            min_box_area = get_min_box_area_for_class(class_name)

            # 너무 작은 박스는 장애물로 보지 않음
            if box_area < min_box_area:
                continue

            center_x = center[0]
            zone = get_zone(center_x)

            danger_score = box_area / BOX_AREA_SCALE
            danger[zone] += danger_score

        # ==============================
        # 2. 초음파 기반 위험도 추가
        # ==============================
        if distances_cm is not None:
            front_distance = distances_cm.get("FRONT")

            if front_distance is not None and front_distance < AVOID_DISTANCE_CM:
                danger["CENTER"] += 10.0

        return danger