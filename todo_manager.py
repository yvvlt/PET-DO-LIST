# 투두리스트 관련 로직 (할 일 추가/삭제/완료, 간식 지급)

# todo_manager.py

import datetime # 날짜 처리를 위해 datetime 모듈 추가
from config import SNACK_PER_TODO_COMPLETE, INITIAL_SNACK_COUNTS, SNACK_EFFECTS

class TodoManager:
    def __init__(self, initial_daily_todos=None, initial_snack_counts=None):
        # 날짜별 할 일 목록 초기화
        # initial_daily_todos가 None이거나 비어있으면 오늘 날짜로 빈 리스트 시작
        self.daily_todos = initial_daily_todos if initial_daily_todos is not None else {}
        
        # 현재 보고 있는 날짜
        self.current_date = datetime.date.today()
        # 현재 날짜의 할 일 목록이 없다면 빈 리스트로 초기화
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []

        # 간식 개수 초기화 (기존 로직 동일)
        self.snack_counts = initial_snack_counts if initial_snack_counts else INITIAL_SNACK_COUNTS.copy()
        for snack_name in SNACK_EFFECTS:
            if snack_name not in self.snack_counts:
                self.snack_counts[snack_name] = 0

        print(f"TodoManager 초기화됨. 현재 날짜: {self.current_date}, 간식: {self.snack_counts}")
        print(f"로드된 날짜별 할 일 목록 수: {len(self.daily_todos)}")


    def set_current_date(self, new_date):
        """현재 날짜를 변경하고, 해당 날짜의 할 일 목록을 로드/초기화합니다."""
        if not isinstance(new_date, datetime.date):
            raise TypeError("날짜는 datetime.date 객체여야 합니다.")
        
        self.current_date = new_date
        # 새로운 날짜에 대한 할 일 목록이 없다면 빈 리스트로 초기화
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []
        print(f"현재 할 일 확인 날짜 변경: {self.current_date}")

    def add_todo(self, todo_text):
        """현재 날짜의 할 일 목록에 새로운 할 일을 추가합니다."""
        if not isinstance(todo_text, str) or not todo_text.strip():
            print("유효하지 않은 할 일 내용입니다.")
            return False
        
        # 현재 날짜의 할 일 목록에 추가
        self.daily_todos[self.current_date].append({'text': todo_text.strip(), 'completed': False})
        print(f"할 일 추가 ({self.current_date}): {todo_text.strip()}")
        return True

    def remove_todo(self, index):
        """현재 날짜의 할 일 목록에서 지정된 인덱스의 할 일을 삭제합니다."""
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos):
            removed_todo = current_day_todos.pop(index)
            print(f"할 일 삭제 ({self.current_date}): {removed_todo['text']}")
            return removed_todo
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return None

    def complete_todo(self, index):
        """
        현재 날짜의 할 일 목록에서 지정된 인덱스의 할 일을 완료 처리하고, 간식을 지급합니다.
        Returns:
            int: 지급된 간식 개수. (지급 실패 시 0)
        """
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos):
            if not current_day_todos[index]['completed']:
                current_day_todos[index]['completed'] = True
                todo_text = current_day_todos[index]['text']
                self._give_snack_item("기본 간식", SNACK_PER_TODO_COMPLETE) # 기본 간식 지급
                print(f"할 일 완료 ({self.current_date}): {todo_text}, 간식 지급: {SNACK_PER_TODO_COMPLETE}개")
                return SNACK_PER_TODO_COMPLETE
            print(f"이미 완료된 할 일입니다 ({self.current_date}): {current_day_todos[index]['text']}")
            return 0
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return 0
    
    def _give_snack_item(self, snack_name, count):
        """
        내부적으로 특정 종류의 간식을 지급합니다.
        """
        if snack_name in SNACK_EFFECTS:
            self.snack_counts[snack_name] = self.snack_counts.get(snack_name, 0) + count
            print(f"{snack_name} {count}개 획득! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}")
            return True
        print(f"알 수 없는 간식 종류: {snack_name}")
        return False

    def use_snack(self, snack_name):
        """
        간식을 사용합니다. 사용 가능한 간식인지 확인 후 개수를 감소시킵니다.
        Returns:
            dict: 사용된 간식의 효과. (사용 실패 시 None)
        """
        if snack_name in self.snack_counts and self.snack_counts[snack_name] > 0:
            self.snack_counts[snack_name] -= 1
            effect = SNACK_EFFECTS[snack_name]
            print(f"'{snack_name}' 1개 사용! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}, 효과: {effect}")
            return effect
        print(f"'{snack_name}' 간식이 없거나 부족합니다.")
        return None

    def get_current_date_todos(self):
        """현재 설정된 날짜의 할 일 목록을 반환합니다."""
        return self.daily_todos.get(self.current_date, [])
    
    def get_daily_todos_data(self):
        """모든 날짜별 할 일 목록 데이터를 반환합니다 (저장용)."""
        return self.daily_todos

    def get_current_snack_counts(self):
        """현재 간식 개수 딕셔너리를 반환합니다."""
        return self.snack_counts
    
    def get_current_date(self):
        """현재 설정된 날짜(datetime.date)를 반환합니다."""
        return self.current_date
