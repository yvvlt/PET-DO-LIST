# config.py

import datetime

# --- [1] 애플리케이션 기본 설정 ---
APP_TITLE = "Pet-Do-List: 환생 펫 투두리스트"
DATA_FILE_NAME = "pet_do_list_data.pkl" # 데이터 저장 파일명
INITIAL_PET_NAME = "새 친구" # 펫 이름 미입력 시 기본값

# --- [2] 펫 성장 관련 설정 ---
PET_SPECIES_LIST = ["사람", "나무", "고양이"] # 선택 가능한 펫 종류
MAX_PET_LEVEL = 7 # 펫의 최대 레벨
EXP_PER_TODO_COMPLETE = 10 # 할 일 하나 완료 시 획득 경험치
EXP_REQUIRED_FOR_LEVEL_UP = { # 레벨업에 필요한 경험치 (레벨: 필요 경험치)
    1: 0, # 레벨 1은 시작 레벨이므로 경험치 0
    2: 50,
    3: 120,
    4: 200,
    5: 300,
    6: 450,
    7: 600, # MAX_PET_LEVEL (최대 레벨)
}
# 펫 초기 능력치 (행복도, 포만감은 0부터 시작)
INITIAL_PET_HAPPINESS = 50
INITIAL_PET_FULLNESS = 50
MAX_PET_HAPPINESS = 100
MAX_PET_FULLNESS = 100


# --- [3] 간식 및 효과 설정 ---
SNACK_PER_TODO_COMPLETE = 1 # 할 일 완료 시 지급되는 간식 개수
INITIAL_SNACK_COUNTS = { # 시작 시 주어지는 간식 개수
    "기본 간식": 3,
    "고급 간식": 1
}

# 간식별 효과 (행복도, 포만감) 및 아이콘 파일명
SNACK_EFFECTS = {
    "기본 간식": {"happiness": 10, "fullness": 10, "icon": "basic_snack_icon.png"},
    "고급 간식": {"happiness": 25, "fullness": 25, "icon": "premium_snack_icon.png"}
}
HAPPINESS_PER_SNACK = 10 # 기본 간식의 행복도 증가량 (예시)
FULLNESS_PER_SNACK = 10   # 기본 간식의 포만감 증가량 (예시)


# --- [4] 펫 환생(리셋) 관련 설정 ---
WEEKLY_RESET_DAY = 2 # 매주 화요일 (월:0, 화:1, 수:2, 목:3, 금:4, 토:5, 일:6)
RESET_TIME_HOUR = 3 # 새벽 3시
PET_RESET_INTERVAL_DAYS = 7 # 펫 환생 주기 (7일)


# --- [5] 환경 변수 또는 경로 설정 (미사용) ---
# API_KEY = os.getenv("MY_API_KEY")


# --- [6] Tkinter GUI 기본 설정 ---
WINDOW_WIDTH = 1000 
WINDOW_HEIGHT = 900 # <-- 창 크기 문제 해결을 위해 이 값을 900으로 높였습니다!
BG_COLOR = "#e0e0e0" # 연한 회색 배경
PRIMARY_COLOR = "#6a0dad" # 보라색 계열 (버튼, 제목 등에 사용)
ACCENT_COLOR = "#ff6f61" # 주황-분홍 계열 (강조 색상)


# --- [7] 로그 파일 설정 (미사용) ---
# LOG_FILE = "app_log.txt"


# --- [8] 리소스 파일 경로 설정 ---
RESOURCES_PATH = "resources/" # 모든 리소스가 담길 기본 폴더

# 👇 새로 추가된 하위 폴더 경로들입니다.
PET_IMAGES_SUBFOLDER = "pet_images/"  # 펫 이미지 파일들이 들어갈 resources 하위 폴더
ITEM_IMAGES_SUBFOLDER = "item_images/" # 아이템/간식 이미지 파일들이 들어갈 resources 하위 폴더
ETC_SUBFOLDER = "etc/"               # 기타 이미지들이 들어갈 resources 하위 폴더


# --- [9] 개발/디버깅 설정 ---
DEBUG_MODE = True # 디버깅 메시지를 출력할지 여부