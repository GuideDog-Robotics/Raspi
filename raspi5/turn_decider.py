# turn_decider.py

from config import FRAME_WIDTH

from box_utils import (
    get_box_area,
    get_min_box_area_for_class,
)


class TurnDecider:
    """
    위험도와 객체 위치를 보고
    TURN_LEFT 또는 TURN_RIGHT를 결정하는 모듈
    """

    def choose_turn_direction(self, detections, distances_cm, danger):
        """
        회피 방향 결정 원칙:

        1. 왼쪽 위험도가 크면 오른쪽으로 회피
        2. 오른쪽 위험도가 크면 왼쪽으로 회피
        3. 위험도가 비슷하면 가장 큰 객체 위치 기준
        4. 판단 불가능하면 기본 TURN_RIGHT
        """

        # 왼쪽이 더 위험하면 오른쪽으로 회피
        if danger["LEFT"] > danger["RIGHT"]:
            return "TURN_RIGHT"

        # 오른쪽이 더 위험하면 왼쪽으로 회피
        if danger["RIGHT"] > danger["LEFT"]:
            return "TURN_LEFT"

        # ==============================
        # 위험도가 같으면 가장 큰 객체 기준
        # ==============================
        biggest_area = 0
        biggest_center_x = None

        for det in detections:
            box = det.get("box")
            center = det.get("center")

            if box is None or center is None:
                continue

            box_area = get_box_area(box)
            class_name = det.get("class_name")

            min_box_area = get_min_box_area_for_class(class_name)

            if box_area >= min_box_area and box_area > biggest_area:
                biggest_area = box_area
                biggest_center_x = center[0]

        if biggest_center_x is not None:
            image_center_x = FRAME_WIDTH / 2

            # 객체가 화면 중앙보다 왼쪽이면 오른쪽으로 회피
            if biggest_center_x < image_center_x:
                return "TURN_RIGHT"

            # 객체가 화면 중앙보다 오른쪽이면 왼쪽으로 회피
            else:
                return "TURN_LEFT"

        # 판단할 정보가 없으면 기본 오른쪽 회전
        return "TURN_RIGHT"