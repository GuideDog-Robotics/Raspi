# obstacle_presence.py

from box_utils import get_box_area


class ObstaclePresence:
    """
    화면에 객체가 아직 남아있는지 확인하는 모듈.

    목적:
    - MIN_BOX_AREA보다 작아져도 객체가 화면에 보이면
      바로 FREE로 바뀌지 않게 하기 위함.
    - 즉, 회전 중에 박스가 작아졌다는 이유만으로
      장애물이 완전히 사라졌다고 판단하지 않음.
    """

    def __init__(self, min_visible_area=1000):
        self.min_visible_area = min_visible_area

    def camera_has_visible_object(self, detections):
        """
        화면에 아직 보이는 객체가 있는지 확인.

        MIN_BOX_AREA_BY_CLASS보다 훨씬 작은 기준을 사용해서
        '위험한 큰 장애물'이 아니라
        '아직 화면에 남아있는 장애물'을 판단한다.
        """

        for det in detections:
            box = det.get("box")

            if box is None:
                continue

            box_area = get_box_area(box)

            if box_area >= self.min_visible_area:
                return True

        return False