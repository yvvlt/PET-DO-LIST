# 설정 파일 (상수 정의 : 펫 초기값, 환생 주기 등)

import datetime

# --- [1] 펫 기본 설정 ---
INITIAL_PET_NAME = "새싹이" # 사용자가 이름을 입력하지 않았을 때의 기본 이름
INITIAL_PET_LEVEL = 1      # 펫의 초기 레벨
INITIAL_PET_EXP = 0        # 펫의 초기 경험치
INITIAL_PET_HAPPINESS = 70 # 펫의 초기 행복도 (최대 100)
INITIAL_PET_FULLNESS = 70  # 펫의 초기 포만감 (최대 100)
PET_MAX_HAPPINESS = 100    # 펫의 최대 행복도 (행복도/포만감의 상한선)
PET_MAX_FULLNESS = 100     # 펫의 최대 포만감

# --- [2] 펫 성장 및 경험치 설정 ---
EXP_PER_TODO_COMPLETE = 10 # 할 일 하나 완료 시 획득하는 경험치

# 주간 환생 컨셉에 맞춰 1주일 = 7레벨로 성장하도록 설정
# 각 레벨업에 필요한 경험치 (현재 레벨에서 다음 레벨로 가기 위한 경험치)
LEVEL_UP_EXP_REQUIREMENTS = { 
    1: 30,  # Lv.1 -> Lv.2
    2: 40,  # Lv.2 -> Lv.3
    3: 50,  # Lv.3 -> Lv.4
    4: 60,  # Lv.4 -> Lv.5
    5: 70,  # Lv.5 -> Lv.6
    6: 80,  # Lv.6 -> Lv.7 (최대 레벨)
    7: 0    # Lv.7은 최대 레벨이므로 경험치 요구 없음 (선택 사항)
}
MAX_PET_LEVEL = 7 # 펫이 도달할 수 있는 최대 레벨

DEFAULT_LEVEL_UP_EXP = 50

# --- [3] 간식 관련 설정 ---
SNACK_EFFECTS = { # 간식 아이템이 펫에게 주는 효과
    "기본 간식": {"happiness": 10, "fullness": 20, "icon": "basic_snack_icon.png"},
    "고급 간식": {"happiness": 30, "fullness": 50, "icon": "premium_snack_icon.png"},
}
INITIAL_SNACK_COUNTS = { # 처음 시작 시 제공되는 간식 개수
    "기본 간식": 3,
    "고급 간식": 1,
}
SNACK_PER_TODO_COMPLETE = 1 # 할 일 하나 완료 시 획득하는 간식 개수 (항상 "기본 간식"으로 간주)

# --- [4] 펫 환생(초기화) 시스템 설정 ---
# 매주 특정 요일(WEEKLY_RESET_DAY)에 펫이 환생합니다.
# datetime.date.weekday()는 월요일(0)부터 일요일(6)까지 숫자를 반환합니다.
WEEKLY_RESET_DAY = 0 # 월요일 (0) - 펫이 환생하는 요일
RESET_TIME_HOUR = 0  # 펫이 환생하는 시간 (0시 = 자정)

# 환생 시 사용자가 직접 선택할 수 있는 펫 종류 리스트
PET_SPECIES_LIST = ["사람", "나무", "고양이"] 
# 펫 종류별 레벨 이미지 명명 규칙 예시: "resources/pet_images/사람_level1.png"

# --- [5] 파일 경로 설정 ---
DATA_FILE_NAME = "pet_do_list_data.pkl" # 펫 및 투두리스트 데이터를 저장할 파일 이름
RESOURCES_PATH = "resources/" # 이미지, 아이콘 등 리소스 폴더의 기본 경로

# --- [6] Tkinter GUI 기본 설정 ---
APP_TITLE = "Pet-Do-List: 환생 펫 투두리스트"
WINDOW_WIDTH = 1000 # 창 너비
WINDOW_HEIGHT = 700 # 창 높이
BG_COLOR = "#e0e0e0" # 배경 색상 (밝은 회색)
PRIMARY_COLOR = "#6a0dad" # 주요 색상 (보라색)
ACCENT_COLOR = "#ff6f61" # 강조 색상 (주황색)