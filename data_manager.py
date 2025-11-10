# 데이터 저장 및 불러오기 (펫 데이터, 투두리스트 데이터)


import pickle
import os # 파일 존재 여부 확인을 위해 os 모듈 추가

from config import DATA_FILE_NAME # config.py에서 파일 이름을 가져옵니다.

def save_data(pet_data, todo_list, snack_counts):
    """
    현재 펫 데이터, 투두리스트 목록, 간식 개수를 파일에 저장합니다.
    Args:
        pet_data (Pet object): 현재 펫 객체 인스턴스.
        todo_list (list): 할 일 목록 (문자열 리스트).
        snack_counts (dict): 간식 종류별 개수를 담은 딕셔너리.
    """
    data_to_save = {
        'pet': pet_data,
        'todo_list': todo_list,
        'snack_counts': snack_counts
    }
    try:
        with open(DATA_FILE_NAME, 'wb') as f: # 'wb'는 바이너리 쓰기 모드
            pickle.dump(data_to_save, f)
        print(f"데이터가 '{DATA_FILE_NAME}'에 성공적으로 저장되었습니다.")
    except Exception as e:
        print(f"데이터 저장 중 오류 발생: {e}")

def load_data():
    """
    파일에서 저장된 데이터를 불러옵니다.
    저장된 파일이 없거나 오류 발생 시 초기값을 반환합니다.
    Returns:
        tuple: (pet_data, todo_list, snack_counts)
    """
    if os.path.exists(DATA_FILE_NAME):
        try:
            with open(DATA_FILE_NAME, 'rb') as f: # 'rb'는 바이너리 읽기 모드
                loaded_data = pickle.load(f)
            print(f"데이터를 '{DATA_FILE_NAME}'에서 성공적으로 불러왔습니다.")
            # 불러온 데이터가 기대하는 형태인지 확인 (방어적인 코드)
            if all(key in loaded_data for key in ['pet', 'todo_list', 'snack_counts']):
                return loaded_data['pet'], loaded_data['todo_list'], loaded_data['snack_counts']
            else:
                print("저장된 파일의 형식이 올바르지 않아 초기 데이터를 반환합니다.")
                return None, [], {} # 잘못된 형식일 경우 초기값 반환
        except Exception as e:
            print(f"데이터 불러오기 중 오류 발생 또는 파일 손상: {e}")
            return None, [], {} # 오류 발생 시 초기값 반환
    else:
        print(f"'{DATA_FILE_NAME}' 파일이 존재하지 않아 초기 데이터를 반환합니다.")
        return None, [], {} # 파일이 없을 경우 초기값 반환
