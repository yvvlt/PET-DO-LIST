# 데이터 저장 및 불러오기 (펫 데이터, 투두리스트 데이터)

# data_manager.py

import pickle
import os 
import datetime # 날짜 처리를 위해 datetime 모듈 추가

from config import DATA_FILE_NAME 

# save_data 함수 시그니처 변경 (todo_list -> daily_todos)
def save_data(pet_data, daily_todos, snack_counts):
    """
    현재 펫 데이터, 날짜별 할 일 목록, 간식 개수를 파일에 저장합니다.
    Args:
        pet_data (Pet object): 현재 펫 객체 인스턴스.
        daily_todos (dict): 날짜(datetime.date 객체)를 키로 하고, 해당 날짜의 할 일 목록(list)을 값으로 하는 딕셔너리.
                            예: {datetime.date(2025, 11, 11): [{'text': '코딩', 'completed': False}]}
        snack_counts (dict): 간식 종류별 개수를 담은 딕셔너리.
    """
    data_to_save = {
        'pet': pet_data,
        'daily_todos': daily_todos, # todo_list 대신 daily_todos 저장
        'snack_counts': snack_counts
    }
    try:
        with open(DATA_FILE_NAME, 'wb') as f: # 'wb'는 바이너리 쓰기 모드
            pickle.dump(data_to_save, f)
        print(f"데이터가 '{DATA_FILE_NAME}'에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")

# load_data 함수 시그니처 변경 (todo_list -> daily_todos)
def load_data():
    """
    파일에서 저장된 데이터를 불러옵니다.
    저장된 파일이 없거나 오류 발생 시 초기값을 반환합니다.
    Returns:
        tuple: (pet_data, daily_todos, snack_counts)
    """
    if os.path.exists(DATA_FILE_NAME):
        try:
            with open(DATA_FILE_NAME, 'rb') as f: # 'rb'는 바이너리 읽기 모드
                loaded_data = pickle.load(f)
            print(f"데이터를 '{DATA_FILE_NAME}'에서 성공적으로 불러왔습니다.")
            # 불러온 데이터가 기대하는 형태인지 확인 (방어적인 코드)
            # 기존 save_data()로 저장된 파일과 호환성 유지 (todo_list가 있다면 daily_todos로 변환)
            if 'todo_list' in loaded_data:
                # 기존 todo_list 데이터를 오늘 날짜의 daily_todos로 변환
                today = datetime.date.today()
                loaded_data['daily_todos'] = {today: loaded_data['todo_list']}
                del loaded_data['todo_list'] # 기존 키는 삭제
                print("이전 형식의 할 일 데이터를 현재 날짜로 변환하여 로드했습니다.")
            
            if all(key in loaded_data for key in ['pet', 'daily_todos', 'snack_counts']):
                return loaded_data['pet'], loaded_data['daily_todos'], loaded_data['snack_counts']
            else:
                print("저장된 파일의 형식이 올바르지 않아 초기 데이터를 반환합니다.")
                return None, {}, {} # 잘못된 형식일 경우 초기값 반환 (daily_todos는 딕셔너리로 초기화)
        except Exception as e:
            print(f"데이터 불러오기 중 오류 발생 또는 파일 손상: {e}")
            return None, {}, {} # 오류 발생 시 초기값 반환
    else:
        print(f"'{DATA_FILE_NAME}' 파일이 존재하지 않아 초기 데이터를 반환합니다.")
        return None, {}, {} # 파일이 없을 경우 초기값 반환 (daily_todos는 딕셔너리로 초기화)
