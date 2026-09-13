# obstacle_checker.py

from config import AVOID_DISTANCE_CM

from box_utils import (
    get_box_area,
    get_min_box_area_for_class,
)


class ObstacleChecker:
    """
    현재 카메라/초음파 기준으로
    위험이 있는지 확인하는 모듈
    """

    def camera_has_big_object(self, detections):
        """
        카메라 화면에 MIN_BOX_AREA 이상 크기의 객체가 있는지 확인
        """

        for det in detections:
            box = det.get("box")

            if box is None:
                continue

            box_area = get_box_area(box)
            class_name = det.get("class_name")

            min_box_area = get_min_box_area_for_class(class_name)

            if box_area >= min_box_area:
                return True

        return False

    def ultrasonic_too_close(self, distances_cm):
        """
        FRONT 초음파 센서가 너무 가까운지 확인
        """

        if distances_cm is None:
            return False

        front_distance = distances_cm.get("FRONT")

        if front_distance is not None and front_distance < AVOID_DISTANCE_CM:
            return True

        return False

    def is_clear(self, detections, distances_cm):
        """
        카메라와 초음파가 모두 안전하면 True
        """

        camera_clear = not self.camera_has_big_object(detections)
        ultrasonic_clear = not self.ultrasonic_too_close(distances_cm)

        return camera_clear and ultrasonic_clear

    def danger_triggered(self, detections, distances_cm):
        """
        카메라 또는 초음파 중 하나라도 위험하면 True
        """

        return (
            self.camera_has_big_object(detections)
            or self.ultrasonic_too_close(distances_cm)
        )