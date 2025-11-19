# todo_manager.py

# 사용자의 할 일(Todo) 목록과 간식 인벤토리를 관리하는 모듈입니다.
# 날짜별 할 일 추가, 삭제, 완료 처리 및 간식 획득, 사용 등의 로직을 담당합니다.

import datetime # 날짜 객체 처리에 사용.
# config.py에서 간식 관련 상수들을 임포트합니다.
from config import SNACK_PER_TODO_COMPLETE, INITIAL_SNACK_COUNTS, SNACK_EFFECTS

class TodoManager:
    """
    할 일 목록과 간식 인벤토리를 관리하는 클래스.
    """
    def __init__(self, initial_daily_todos=None, initial_snack_counts=None):
        # 날짜별 할 일 딕셔너리 초기화 (기존 데이터 로드 또는 새로 생성).
        self.daily_todos = initial_daily_todos if initial_daily_todos is not None else {}
        
        self.current_date = datetime.date.today() # 현재 조회 중인 날짜.
        # 현재 날짜의 할 일 목록이 없으면 빈 리스트로 초기화.
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []

        # 간식 개수 딕셔너리 초기화 (기존 데이터 로드 또는 config의 초기값 사용).
        self.snack_counts = initial_snack_counts if initial_snack_counts else INITIAL_SNACK_COUNTS.copy()
        # 모든 종류의 간식이 self.snack_counts에 있도록 보장 (새로운 간식이 추가되었을 때 초기값 0으로 처리).
        for snack_name in SNACK_EFFECTS:
            if snack_name not in self.snack_counts:
                self.snack_counts[snack_name] = 0

        print(f"TodoManager 초기화됨. 현재 날짜: {self.current_date}, 간식: {self.snack_counts}")
        
    def set_current_date(self, new_date):
        """
        현재 조회 중인 날짜를 변경합니다.
        Args:
            new_date (datetime.date): 새로 설정할 날짜 객체.
        Raises:
            TypeError: new_date가 datetime.date 객체가 아닐 경우.
        """
        if not isinstance(new_date, datetime.date):
            raise TypeError("날짜는 datetime.date 객체여야 합니다.")
        
        self.current_date = new_date # 날짜 업데이트.
        # 새 날짜의 할 일 목록이 없으면 빈 리스트로 초기화.
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []
        print(f"현재 할 일 확인 날짜 변경: {self.current_date}")

    def add_todo(self, todo_text):
        """
        현재 날짜의 할 일 목록에 새로운 할 일을 추가합니다.
        Args:
            todo_text (str): 추가할 할 일 내용.
        Returns:
            bool: 할 일 추가 성공 여부.
        """
        if not isinstance(todo_text, str) or not todo_text.strip(): # 유효성 검사.
            print("유효하지 않은 할 일 내용입니다.")
            return False
        
        # 할 일 추가 (text와 completed 상태 포함).
        self.daily_todos[self.current_date].append({'text': todo_text.strip(), 'completed': False})
        print(f"할 일 추가 ({self.current_date}): {todo_text.strip()}")
        return True

    def remove_todo(self, index):
        """
        현재 날짜의 할 일 목록에서 특정 인덱스의 할 일을 삭제합니다.
        Args:
            index (int): 삭제할 할 일의 인덱스.
        Returns:
            dict or None: 삭제된 할 일 객체 또는 실패 시 None.
        """
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos): # 유효한 인덱스인지 확인.
            removed_todo = current_day_todos.pop(index) # 할 일 삭제.
            print(f"할 일 삭제 ({self.current_date}): {removed_todo['text']}")
            return removed_todo
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return None

    def complete_todo(self, index):
        """
        현재 날짜의 할 일 목록에서 특정 인덱스의 할 일을 완료 처리합니다.
        할 일 완료 시 기본 간식을 지급합니다.
        Args:
            index (int): 완료할 할 일의 인덱스.
        Returns:
            int: 지급된 간식의 개수. (이미 완료된 할 일이라면 0).
        """
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos): # 유효한 인덱스인지 확인.
            if not current_day_todos[index]['completed']: # 아직 완료되지 않은 할 일일 경우.
                current_day_todos[index]['completed'] = True # 완료 상태로 변경.
                todo_text = current_day_todos[index]['text']
                
                self.add_snack("기본 간식", SNACK_PER_TODO_COMPLETE) # 간식 지급.
                
                print(f"할 일 완료 ({self.current_date}): {todo_text}, 간식 지급: {SNACK_PER_TODO_COMPLETE}개")
                return SNACK_PER_TODO_COMPLETE
            print(f"이미 완료된 할 일입니다 ({self.current_date}): {current_day_todos[index]['text']}")
            return 0
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return 0
    
    def add_snack(self, snack_name, count):
        """
        지정된 이름의 간식을 지정된 개수만큼 추가합니다.
        Args:
            snack_name (str): 추가할 간식의 이름.
            count (int): 추가할 간식의 개수.
        Returns:
            bool: 간식 추가 성공 여부.
        """
        if snack_name in SNACK_EFFECTS: # 유효한 간식 종류인지 확인.
            # 간식 개수 증가. (처음 추가하는 간식일 경우 0 + count로 처리).
            self.snack_counts[snack_name] = self.snack_counts.get(snack_name, 0) + count
            print(f"'{snack_name}' {count}개 획득! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}")
            return True
        print(f"알 수 없는 간식 종류여서 추가할 수 없습니다: {snack_name}")
        return False

    def use_snack(self, snack_name):
        """
        지정된 이름의 간식을 1개 사용합니다.
        Args:
            snack_name (str): 사용할 간식의 이름.
        Returns:
            dict or None: 간식의 효과 딕셔너리 또는 간식이 없거나 실패 시 None.
        """
        # 간식이 존재하고 개수가 0보다 많을 경우.
        if snack_name in self.snack_counts and self.snack_counts[snack_name] > 0:
            self.snack_counts[snack_name] -= 1 # 간식 개수 감소.
            effect = SNACK_EFFECTS[snack_name] # 간식 효과 가져오기.
            print(f"'{snack_name}' 1개 사용! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}, 효과: {effect}")
            return effect
        print(f"'{snack_name}' 간식이 없거나 부족합니다.")
        return None

    def get_current_date_todos(self):
        """현재 조회 중인 날짜의 할 일 목록을 반환합니다."""
        return self.daily_todos.get(self.current_date, [])
    
    def get_daily_todos_data(self):
        """전체 날짜별 할 일 데이터(딕셔너리)를 반환합니다."""
        return self.daily_todos

    def get_current_snack_counts(self):
        """현재 간식 인벤토리(간식 개수 딕셔너리)를 반환합니다."""
        return self.snack_counts
    
    def get_current_date(self):
        """현재 조회 중인 날짜를 반환합니다."""
        return self.current_date