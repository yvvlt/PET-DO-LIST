# data_manager.py

import pickle
import os 
import datetime 

from config import DATA_FILE_NAME 

# save_data 함수 시그니처 변경 (historical_pets 인자 추가)
def save_data(pet_data, daily_todos, snack_counts, historical_pets):
    """
    현재 펫 데이터, 날짜별 할 일 목록, 간식 개수, 그리고 과거 펫 기록을 파일에 저장합니다.
    Args:
        pet_data (Pet object): 현재 펫 객체 인스턴스.
        daily_todos (dict): 날짜(datetime.date 객체)를 키로 하고, 해당 날짜의 할 일 목록(list)을 값으로 하는 딕셔너리.
        snack_counts (dict): 간식 종류별 개수를 담은 딕셔너리.
        historical_pets (list): 과거 펫 기록을 담은 리스트. 각 요소는 딕셔너리로 {species, level, start_date, end_date} 등을 포함.
    """
    data_to_save = {
        'pet': pet_data,
        'daily_todos': daily_todos,
        'snack_counts': snack_counts,
        'historical_pets': historical_pets # 새로운 저장 항목 추가
    }
    try:
        with open(DATA_FILE_NAME, 'wb') as f: 
            pickle.dump(data_to_save, f)
        print(f"데이터가 '{DATA_FILE_NAME}'에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")

# load_data 함수 시그니처 변경 (historical_pets 반환값 추가)
def load_data():
    """
    파일에서 저장된 데이터를 불러옵니다.
    저장된 파일이 없거나 오류 발생 시 초기값을 반환합니다.
    Returns:
        tuple: (pet_data, daily_todos, snack_counts, historical_pets)
    """
    if os.path.exists(DATA_FILE_NAME):
        try:
            with open(DATA_FILE_NAME, 'rb') as f: 
                loaded_data = pickle.load(f)
            print(f"데이터를 '{DATA_FILE_NAME}'에서 성공적으로 불러왔습니다.")
            
            # 기존 형식의 데이터와 호환성 유지 로직 (새로 추가된 항목들에 대한 기본값 설정)
            if 'todo_list' in loaded_data: # 이전 버전 호환 (daily_todos 없을 때)
                today = datetime.date.today()
                loaded_data['daily_todos'] = {today: loaded_data['todo_list']}
                del loaded_data['todo_list'] 
                print("이전 형식의 할 일 데이터를 현재 날짜로 변환하여 로드했습니다.")
            if 'daily_todos' not in loaded_data: # daily_todos가 아예 없으면 빈 딕셔너리로
                loaded_data['daily_todos'] = {}
            if 'historical_pets' not in loaded_data: # historical_pets가 없으면 빈 리스트로
                loaded_data['historical_pets'] = [] 
            if 'snack_counts' not in loaded_data: # snack_counts가 없으면 빈 딕셔너리로 (TodoManager에서 처리 예정)
                loaded_data['snack_counts'] = {}


            if all(key in loaded_data for key in ['pet', 'daily_todos', 'snack_counts', 'historical_pets']):
                return loaded_data['pet'], loaded_data['daily_todos'], loaded_data['snack_counts'], loaded_data['historical_pets']
            else:
                print("저장된 파일의 형식이 올바르지 않아 초기 데이터를 반환합니다.")
                return None, {}, {}, [] # 잘못된 형식일 경우 초기값 반환
        except Exception as e:
            print(f"데이터 불러오기 중 오류 발생 또는 파일 손상: {e}")
            return None, {}, {}, [] # 오류 발생 시 초기값 반환
    else:
        print(f"'{DATA_FILE_NAME}' 파일이 존재하지 않아 초기 데이터를 반환합니다.")
        return None, {}, {}, [] # 파일이 없을 경우 초기값 반환
