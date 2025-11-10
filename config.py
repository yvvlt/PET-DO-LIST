# 설정 파일 (상수 정의 : 펫 초기값, 환생 주기 등)

import datetime

# --- [1] 펫 기본 설정 ---
# 펫이 처음 태어날 때의 기본 능력치 및 정보
INITIAL_PET_NAME = "새싹이" # 사용자가 이름을 입력하지 않았을 때의 기본 이름
INITIAL_PET_LEVEL = 1      # 펫의 초기 레벨
INITIAL_PET_EXP = 0        # 펫의 초기 경험치
INITIAL_PET_HAPPINESS = 70 # 펫의 초기 행복도 (최대 100)
INITIAL_PET_FULLNESS = 70  # 펫의 초기 포만감 (최대 100)
PET_MAX_HAPPINESS = 100    # 펫의 최대 행복도
PET_MAX_FULLNESS = 100     # 펫의 최대 포만감

# --- [2] 펫 성장 및 경험치 설정 ---
EXP_PER_TODO_COMPLETE = 10 # 할 일 하나 완료 시 획득하는 경험치
LEVEL_UP_EXP_REQUIREMENTS = { # 레벨업에 필요한 경험치 (레벨별로 다르게 설정 가능)
    1: 50,  # Lv.1 -> Lv.2
    2: 100, # Lv.2 -> Lv.3
    3: 150, # Lv.3 -> Lv.4
    # ... 더 추가할 수 있습니다.
}
DEFAULT_LEVEL_UP_EXP = 50 # 위에 정의되지 않은 레벨의 기본 레벨업 경험치

# --- [3] 간식 관련 설정 ---
SNACK_EFFECTS = { # 간식 아이템이 펫에게 주는 효과 (추후 다양한 간식 추가 가능)
    "기본 간식": {"happiness": 10, "fullness": 20},
    # "고급 간식": {"happiness": 20, "fullness": 40},
}
INITIAL_SNACK_COUNT = 3 # 처음 시작 시 제공되는 간식 개수
SNACK_PER_TODO_COMPLETE = 1 # 할 일 하나 완료 시 획득하는 간식 개수

# --- [4] 펫 환생(초기화) 시스템 설정 ---
WEEKLY_RESET_DAY = 0 # 월요일 (0) - 펫이 환생하는 요일
RESET_TIME_HOUR = 0  # 펫이 환생하는 시간 (0시 = 자정)
PET_SPECIES_LIST = ["알", "새싹이", "토끼", "강아지", "고양이", "펭귄", "용"]

# --- [5] 파일 경로 설정 ---
DATA_FILE_NAME = "pet_do_list_data.pkl" 