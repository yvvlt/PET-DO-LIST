# todo_manager.py

import datetime 
from config import SNACK_PER_TODO_COMPLETE, INITIAL_SNACK_COUNTS, SNACK_EFFECTS

class TodoManager:
    def __init__(self, initial_daily_todos=None, initial_snack_counts=None):
        self.daily_todos = initial_daily_todos if initial_daily_todos is not None else {}
        
        self.current_date = datetime.date.today()
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []

        self.snack_counts = initial_snack_counts if initial_snack_counts else INITIAL_SNACK_COUNTS.copy()
        for snack_name in SNACK_EFFECTS:
            if snack_name not in self.snack_counts:
                self.snack_counts[snack_name] = 0

        print(f"TodoManager 초기화됨. 현재 날짜: {self.current_date}, 간식: {self.snack_counts}")
        

    def set_current_date(self, new_date):
        if not isinstance(new_date, datetime.date):
            raise TypeError("날짜는 datetime.date 객체여야 합니다.")
        
        self.current_date = new_date
        if self.current_date not in self.daily_todos:
            self.daily_todos[self.current_date] = []
        print(f"현재 할 일 확인 날짜 변경: {self.current_date}")

    def add_todo(self, todo_text):
        if not isinstance(todo_text, str) or not todo_text.strip():
            print("유효하지 않은 할 일 내용입니다.")
            return False
        
        self.daily_todos[self.current_date].append({'text': todo_text.strip(), 'completed': False})
        print(f"할 일 추가 ({self.current_date}): {todo_text.strip()}")
        return True

    def remove_todo(self, index):
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos):
            removed_todo = current_day_todos.pop(index)
            print(f"할 일 삭제 ({self.current_date}): {removed_todo['text']}")
            return removed_todo
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return None

    def complete_todo(self, index):
        current_day_todos = self.daily_todos.get(self.current_date, [])
        if 0 <= index < len(current_day_todos):
            if not current_day_todos[index]['completed']:
                current_day_todos[index]['completed'] = True
                todo_text = current_day_todos[index]['text']
                
                self.add_snack("기본 간식", SNACK_PER_TODO_COMPLETE) 
                
                print(f"할 일 완료 ({self.current_date}): {todo_text}, 간식 지급: {SNACK_PER_TODO_COMPLETE}개")
                return SNACK_PER_TODO_COMPLETE
            print(f"이미 완료된 할 일입니다 ({self.current_date}): {current_day_todos[index]['text']}")
            return 0
        print(f"잘못된 인덱스입니다 ({self.current_date}): {index}")
        return 0
    
    def add_snack(self, snack_name, count):
        """
        지정된 이름의 간식을 지정된 개수만큼 추가합니다.
        새로운 간식인 경우 초기화하고, 기존 간식인 경우 개수를 증가시킵니다.
        """
        if snack_name in SNACK_EFFECTS: 
            self.snack_counts[snack_name] = self.snack_counts.get(snack_name, 0) + count
            print(f"'{snack_name}' {count}개 획득! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}")
            return True
        print(f"알 수 없는 간식 종류여서 추가할 수 없습니다: {snack_name}")
        return False


    def use_snack(self, snack_name):
        if snack_name in self.snack_counts and self.snack_counts[snack_name] > 0:
            self.snack_counts[snack_name] -= 1
            effect = SNACK_EFFECTS[snack_name]
            print(f"'{snack_name}' 1개 사용! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}, 효과: {effect}")
            return effect
        print(f"'{snack_name}' 간식이 없거나 부족합니다.")
        return None

    def get_current_date_todos(self):
        return self.daily_todos.get(self.current_date, [])
    
    def get_daily_todos_data(self):
        return self.daily_todos

    def get_current_snack_counts(self):
        return self.snack_counts
    
    def get_current_date(self):
        return self.current_date
