# box_utils.py

from config import (
    FRAME_WIDTH,
    MIN_BOX_AREA_BY_CLASS,
    DEFAULT_MIN_BOX_AREA,
)


def get_box_area(box):
    """
    바운딩 박스 면적 계산

    box 형식:
    [x1, y1, x2, y2]
    """

    x1, y1, x2, y2 = box

    width = max(0, x2 - x1)
    height = max(0, y2 - y1)

    return width * height


def get_min_box_area_for_class(class_name):
    """
    객체 클래스별 최소 박스 면적 반환
    """

    return MIN_BOX_AREA_BY_CLASS.get(class_name, DEFAULT_MIN_BOX_AREA)


def get_zone(center_x):
    """
    객체 중심 x좌표를 기준으로
    LEFT / CENTER / RIGHT 구역 판단
    """

    left_boundary = FRAME_WIDTH / 3
    right_boundary = FRAME_WIDTH * 2 / 3

    if center_x < left_boundary:
        return "LEFT"
    elif center_x < right_boundary:
        return "CENTER"
    else:
        return "RIGHT"