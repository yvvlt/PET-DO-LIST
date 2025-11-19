# config.py

import datetime

# --- [1] 애플리케이션 기본 설정 ---
APP_TITLE = "Pet-Do-List: 환생 펫 투두리스트"  # 애플리케이션 창의 제목. (main.py)
DATA_FILE_NAME = "pet_do_list_data.pkl"     # 데이터 저장 파일명. (data_manager.py)
INITIAL_PET_NAME = "펫"                 # 펫 이름 미입력 시 기본값. (main.py, pet_manager.py)

# --- [2] 펫 성장 관련 설정 ---
PET_SPECIES_LIST = ["사람", "나무", "고양이"] # 선택 가능한 펫 종류 목록. (main.py, pet_manager.py, gui.py)
MAX_PET_LEVEL = 7                             # 펫의 최대 레벨. (pet_manager.py)

INITIAL_PET_LEVEL = 1                         # 펫의 초기 레벨. (pet_manager.py)
INITIAL_PET_EXP = 0                           # 펫의 초기 경험치. (pet_manager.py)

EXP_PER_TODO_COMPLETE = 10                    # 할 일 완료 시 획득 경험치. (pet_manager.py, main.py)
# 레벨업에 필요한 경험치 (레벨: 필요 경험치). (pet_manager.py)
EXP_REQUIRED_FOR_LEVEL_UP = { 
    1: 0, # 레벨 1은 시작 레벨
    2: 50,
    3: 120,
    4: 200,
    5: 300,
    6: 450,
    7: 600, # MAX_PET_LEVEL
}
INITIAL_PET_HAPPINESS = 50                    # 펫의 초기 행복도. (pet_manager.py)
INITIAL_PET_FULLNESS = 50                     # 펫의 초기 포만감. (pet_manager.py)
MAX_PET_HAPPINESS = 100                       # 펫의 최대 행복도. (pet_manager.py)
MAX_PET_FULLNESS = 100                        # 펫의 최대 포만감. (pet_manager.py)


# --- [3] 간식 및 효과 설정 ---
SNACK_PER_TODO_COMPLETE = 1                   # 할 일 완료 시 지급되는 간식 개수. (todo_manager.py)
# 시작 시 주어지는 간식 개수. (todo_manager.py)
INITIAL_SNACK_COUNTS = { 
    "기본 간식": 3,
    "고급 간식": 1
}

# 간식별 효과 (happiness, fullness 증가량) 및 아이콘 파일명. (todo_manager.py)
SNACK_EFFECTS = {
    "기본 간식": {"happiness": 20, "fullness": 20, "icon": "basic_snack_icon.png"}, 
    "고급 간식": {"happiness": 50, "fullness": 50, "icon": "premium_snack_icon.png"} 
}


# --- [4] 펫 환생(리셋) 관련 설정 ---
WEEKLY_RESET_DAY = 2    # 펫이 환생할 요일 (월:0, 화:1, 수:2, ... 일:6). (main.py)
RESET_TIME_HOUR = 3     # 환생 처리 시간 (새벽 3시). (main.py)
PET_RESET_INTERVAL_DAYS = 7 # 펫 환생 주기 (7일). (main.py)


# --- [5] 환경 변수 또는 경로 설정 (미사용) ---
# API_KEY = os.getenv("MY_API_KEY") # 환경 변수 예시


# --- [6] Tkinter GUI 기본 설정 ---
WINDOW_WIDTH = 1000                     # 앱 창 너비.
WINDOW_HEIGHT = 800                     # 앱 창 높이. (main.py)
BG_COLOR = "#e0e0e0"                    # 전반적인 배경색 (연한 회색). (main.py, gui.py)
SECONDARY_TEXT_COLOR = "#471B1B"        # 보조 텍스트 색상 (진한 갈색). (gui.py)
PRIMARY_COLOR = "#fec8b3"               # 주된 요소 색상 (연한 오렌지/피치 계열). (gui.py)
TEXT_BG_COLOR = "#d48d6f"               # (현재 미사용)
ACCENT_COLOR = "#674334"                # 강조 색상 (주황-갈색 계열). (gui.py)

# 폰트 설정. (gui.py)
MAIN_FONT_FAMILY = "맑은 고딕" 
HEADING_FONT_SIZE_LARGE = 18 
HEADING_FONT_SIZE_MEDIUM = 14 
BODY_FONT_SIZE = 12          
BUTTON_FONT_SIZE = 10        


# --- [7] 리소스 파일 경로 설정 ---
RESOURCES_PATH = "resources/"          # 모든 리소스 파일의 기본 폴더 경로. (main.py, gui.py)
PET_IMAGES_SUBFOLDER = "pet_images/"   # 펫 이미지 하위 폴더.
ITEM_IMAGES_SUBFOLDER = "item_images/" # 아이템/간식 이미지 하위 폴더.
ETC_SUBFOLDER = "etc/"                 # 기타 이미지 하위 폴더.
SOUNDS_SUBFOLDER = "sounds"            # 사운드 파일 하위 폴더. (main.py)

# 효과음 파일 이름 정의. (main.py)
SOUND_EFFECT_TODO_COMPLETE = "todo_complete.wav" 
SOUND_EFFECT_SNACK_GIVE = "snack_eat.wav"     
SOUND_EFFECT_PET_LEVEL_UP = "level_up.wav"    
SOUND_EFFECT_PET_REBIRTH = "rebirth.wav"      

# BGM 파일 설정. (main.py)
BGM_FILE = "bgm.mp3" # BGM 파일명 (MP3, WAV 등).
BGM_VOLUME = 1.0     # BGM 볼륨 (0.0 ~ 1.0).

# 효과음 볼륨 정의 (0.0 ~ 1.0). (main.py)
SFX_VOLUME_TODO_COMPLETE = 0.1
SFX_VOLUME_SNACK_GIVE = 0.1
SFX_VOLUME_PET_LEVEL_UP = 0.1
SFX_VOLUME_PET_REBIRTH = 0.1


# --- [8] 개발/디버깅 설정 ---
DEBUG_MODE = True # 디버그 모드 활성화 여부. (print문 출력 등)