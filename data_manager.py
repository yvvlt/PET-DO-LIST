# data_manager.py

# 애플리케이션 데이터를 파일에 저장하고 불러오는 모듈.

import pickle     # 객체 직렬화/역직렬화.
import os         # 파일 시스템 접근 (경로, 존재 여부 확인).
import datetime   # datetime 객체 처리 (이전 데이터 호환성).

from config import DATA_FILE_NAME # 데이터 파일명 임포트.

def save_data(pet_data, daily_todos, snack_counts, historical_pets):
    """
    애플리케이션의 모든 데이터를 파일에 저장.
    Args:
        pet_data (Pet object): 현재 펫 객체.
        daily_todos (dict): 날짜별 할 일 목록.
        snack_counts (dict): 간식 개수.
        historical_pets (list): 과거 펫 기록.
    """
    data_to_save = {
        'pet': pet_data,
        'daily_todos': daily_todos,
        'snack_counts': snack_counts,
        'historical_pets': historical_pets # 과거 펫 기록 포함.
    }
    try:
        with open(DATA_FILE_NAME, 'wb') as f: # 이진 쓰기 모드.
            pickle.dump(data_to_save, f)      # 데이터 직렬화 및 저장.
        print(f"데이터가 '{DATA_FILE_NAME}'에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")

def load_data():
    """
    저장된 데이터 파일을 불러옴. 파일 없거나 오류 발생 시 초기값 반환.
    Returns:
        tuple: (pet_data, daily_todos, snack_counts, historical_pets)
    """
    if os.path.exists(DATA_FILE_NAME):
        try:
            with open(DATA_FILE_NAME, 'rb') as f: # 이진 읽기 모드.
                loaded_data = pickle.load(f)      # 데이터 역직렬화.
            print(f"데이터를 '{DATA_FILE_NAME}'에서 성공적으로 불러왔습니다.")
            
            # 이전 데이터 형식과의 호환성 처리.
            if 'todo_list' in loaded_data: # 이전 버전의 'todo_list' 필드 처리.
                today = datetime.date.today()
                loaded_data['daily_todos'] = {today: loaded_data['todo_list']}
                del loaded_data['todo_list'] 
                print("이전 형식의 할 일 데이터를 현재 날짜로 변환하여 로드했습니다.")
            if 'daily_todos' not in loaded_data:    # 'daily_todos' 필드 부재 시 초기화.
                loaded_data['daily_todos'] = {}
            if 'historical_pets' not in loaded_data: # 'historical_pets' 필드 부재 시 초기화.
                loaded_data['historical_pets'] = [] 
            if 'snack_counts' not in loaded_data:   # 'snack_counts' 필드 부재 시 초기화.
                loaded_data['snack_counts'] = {}

            # 모든 필수 키 존재 여부 확인 후 반환.
            if all(key in loaded_data for key in ['pet', 'daily_todos', 'snack_counts', 'historical_pets']):
                return loaded_data['pet'], loaded_data['daily_todos'], loaded_data['snack_counts'], loaded_data['historical_pets']
            else:
                print("저장된 파일의 형식이 올바르지 않아 초기 데이터를 반환합니다.")
                return None, {}, {}, [] 
        except Exception as e:
            print(f"데이터 불러오기 중 오류 발생 또는 파일 손상: {e}")
            return None, {}, {}, [] 
    else:
        print(f"'{DATA_FILE_NAME}' 파일이 존재하지 않아 초기 데이터를 반환합니다.")
        return None, {}, {}, [] # 파일이 없을 경우 초기값 반환.