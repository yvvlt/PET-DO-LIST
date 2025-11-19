# config.py

import datetime

# --- [1] 애플리케이션 기본 설정 ---
APP_TITLE = "Pet-Do-List: 환생 펫 투두리스트"
DATA_FILE_NAME = "pet_do_list_data.pkl" # 데이터 저장 파일명
INITIAL_PET_NAME = "새 친구" # 펫 이름 미입력 시 기본값

# --- [2] 펫 성장 관련 설정 ---
PET_SPECIES_LIST = ["사람", "나무", "고양이"] # 선택 가능한 펫 종류
MAX_PET_LEVEL = 7 # 펫의 최대 레벨

INITIAL_PET_LEVEL = 1
INITIAL_PET_EXP = 0

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

# 간식별 효과 (행복도, 포만감) 및 아이콘 파일명 (요청에 따라 값 변경)
SNACK_EFFECTS = {
    "기본 간식": {"happiness": 20, "fullness": 20, "icon": "basic_snack_icon.png"}, # ⭐ 변경됨
    "고급 간식": {"happiness": 50, "fullness": 50, "icon": "premium_snack_icon.png"} # ⭐ 변경됨
}
# 이전에 개별 설정된 값은 이제 SNACK_EFFECTS 안에 있습니다.
# HAPPINESS_PER_SNACK = 10 
# FULLNESS_PER_SNACK = 10   


# --- [4] 펫 환생(리셋) 관련 설정 ---
WEEKLY_RESET_DAY = 2 # 매주 화요일 (월:0, 화:1, 수:2, 목:3, 금:4, 토:5, 일:6)
RESET_TIME_HOUR = 3 # 새벽 3시
PET_RESET_INTERVAL_DAYS = 7 # 펫 환생 주기 (7일)


# --- [5] 환경 변수 또는 경로 설정 (미사용) ---
# API_KEY = os.getenv("MY_API_KEY")


# --- [6] Tkinter GUI 기본 설정 ---
WINDOW_WIDTH = 1000 
WINDOW_HEIGHT = 800 
BG_COLOR = "#e0e0e0" # 연한 회색 배경
SECONDARY_TEXT_COLOR = "#471B1B" # 진한 회색
PRIMARY_COLOR = "#fec8b3" # 연한 오렌지/피치 계열 (버튼, 제목 등에 사용)
TEXT_BG_COLOR = "#d48d6f" # 사용되지 않는 것 같아 일단 유지
ACCENT_COLOR = "#674334" # 주황-갈색 계열 (강조 색상)

# ⭐⭐ 폰트 설정 ⭐⭐
MAIN_FONT_FAMILY = "맑은 고딕" 
HEADING_FONT_SIZE_LARGE = 18 
HEADING_FONT_SIZE_MEDIUM = 14 
BODY_FONT_SIZE = 12          
BUTTON_FONT_SIZE = 10        


# --- [7] 로그 파일 설정 (미사용) ---
# LOG_FILE = "app_log.txt"


# --- [8] 리소스 파일 경로 설정 ---
RESOURCES_PATH = "resources/" # 모든 리소스가 담길 기본 폴더
PET_IMAGES_SUBFOLDER = "pet_images/"  # 펫 이미지 파일들이 들어갈 resources 하위 폴더
ITEM_IMAGES_SUBFOLDER = "item_images/" # 아이템/간식 이미지 파일들이 들어갈 resources 하위 폴더
ETC_SUBFOLDER = "etc/"               # 기타 이미지들이 들어갈 resources 하위 폴더
# ⭐⭐ 사운드 리소스 경로 추가 ⭐⭐
SOUNDS_SUBFOLDER = "sounds"

# ⭐⭐ 효과음 파일 이름 정의 (실제 파일 이름에 맞춰 수정해주세요!) ⭐⭐
SOUND_EFFECT_TODO_COMPLETE = "todo_complete.wav" 
SOUND_EFFECT_SNACK_GIVE = "snack_eat.wav"     
SOUND_EFFECT_PET_LEVEL_UP = "level_up.wav"    
SOUND_EFFECT_PET_REBIRTH = "rebirth.wav"      


# --- [9] 개발/디버깅 설정 ---
DEBUG_MODE = True 