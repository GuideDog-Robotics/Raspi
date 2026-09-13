import time

from config import STOP_HOLD_TIME_SEC, VISIBLE_OBJECT_MIN_AREA

from danger_calculator import DangerCalculator
from obstacle_checker import ObstacleChecker
from turn_decider import TurnDecider
from obstacle_presence import ObstaclePresence


class PathPlanner:
    """
    최종 경로 판단 모듈

    상태:
    - FREE      : 평상시 전진 가능 상태
    - STOPPING  : 위험 감지 후 STOP 유지 상태
    - AVOIDING  : TURN_LEFT 또는 TURN_RIGHT 회피 상태
    """

    def __init__(self):
        self.state = "FREE"

        self.stop_start_time = None
        self.turn_command = None

        self.danger_calculator = DangerCalculator()
        self.obstacle_checker = ObstacleChecker()
        self.turn_decider = TurnDecider()

        # 화면에 객체가 아직 남아있는지 확인하는 모듈
        self.obstacle_presence = ObstaclePresence(
            min_visible_area=VISIBLE_OBJECT_MIN_AREA
        )

    def update(self, detections, distances_cm):
        """
        매 프레임마다 호출되는 최종 판단 함수

        입력:
        - detections   : YOLO 탐지 결과
        - distances_cm : 초음파 거리값

        출력:
        - command : FREE / STOP / TURN_LEFT / TURN_RIGHT
        - danger  : LEFT / CENTER / RIGHT 위험도
        """

        danger = self.danger_calculator.calculate(
            detections,
            distances_cm
        )

        danger_trigger = self.obstacle_checker.danger_triggered(
            detections,
            distances_cm
        )

        clear = self.obstacle_checker.is_clear(
            detections,
            distances_cm
        )

        # 화면에 객체가 아직 보이는지 확인
        visible_object = self.obstacle_presence.camera_has_visible_object(
            detections
        )

        # ==============================
        # 1. 이미 회피 중인 상태
        # ==============================
        if self.state == "AVOIDING":

            # 중요:
            # MIN_BOX_AREA보다 작아져도 화면에 객체가 아직 보이면
            # FREE로 바꾸지 않고 계속 회전 유지
            if clear and not visible_object:
                self.state = "FREE"
                self.turn_command = None
                return "FREE", danger

            return self.turn_command, danger

        # ==============================
        # 2. STOP 중인 상태
        # ==============================
        if self.state == "STOPPING":
            now = time.time()

            if self.stop_start_time is None:
                self.stop_start_time = now

            # STOP 시간 유지
            if now - self.stop_start_time < STOP_HOLD_TIME_SEC:
                return "STOP", danger

            # STOP 시간이 끝나면 회피 상태로 이동
            self.state = "AVOIDING"
            self.stop_start_time = None

            if self.turn_command is None:
                self.turn_command = self.turn_decider.choose_turn_direction(
                    detections,
                    distances_cm,
                    danger
                )

            return self.turn_command, danger

        # ==============================
        # 3. 평상시 FREE 상태
        # ==============================
        if danger_trigger:
            self.turn_command = self.turn_decider.choose_turn_direction(
                detections,
                distances_cm,
                danger
            )

            self.state = "STOPPING"
            self.stop_start_time = time.time()

            return "STOP", danger

        # ==============================
        # 4. 위험 없음
        # ==============================
        self.state = "FREE"
        self.turn_command = None

        return "FREE", danger