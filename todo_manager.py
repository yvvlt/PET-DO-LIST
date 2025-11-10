# 투두리스트 관련 로직 (할 일 추가/삭제/완료, 간식 지급)


from config import SNACK_PER_TODO_COMPLETE, INITIAL_SNACK_COUNTS, SNACK_EFFECTS

class TodoManager:
    def __init__(self, initial_todos=None, initial_snack_counts=None):
        # 할 일 목록 초기화
        # 각 할 일은 {'text': '할 일 내용', 'completed': False} 형태의 딕셔너리로 관리
        self.todos = initial_todos if initial_todos is not None else []
        
        # 간식 개수 초기화
        # initial_snack_counts가 None이거나 비어있으면 config의 초기값 사용
        self.snack_counts = initial_snack_counts if initial_snack_counts else INITIAL_SNACK_COUNTS.copy()
        
        # config에 없는 간식 종류가 들어오면 무시하거나 기본값 0으로 설정
        for snack_name in SNACK_EFFECTS:
            if snack_name not in self.snack_counts:
                self.snack_counts[snack_name] = 0

        print(f"TodoManager 초기화됨. 할 일 수: {len(self.todos)}, 현재 간식: {self.snack_counts}")

    def add_todo(self, todo_text):
        """새로운 할 일을 추가합니다."""
        if not isinstance(todo_text, str) or not todo_text.strip():
            print("유효하지 않은 할 일 내용입니다.")
            return False
        self.todos.append({'text': todo_text.strip(), 'completed': False})
        print(f"할 일 추가: {todo_text.strip()}")
        return True

    def remove_todo(self, index):
        """지정된 인덱스의 할 일을 삭제합니다."""
        if 0 <= index < len(self.todos):
            removed_todo = self.todos.pop(index)
            print(f"할 일 삭제: {removed_todo['text']}")
            return removed_todo
        print(f"잘못된 인덱스입니다: {index}")
        return None

    def complete_todo(self, index):
        """
        지정된 인덱스의 할 일을 완료 처리하고, 간식을 지급합니다.
        Returns:
            int: 지급된 간식 개수. (지급 실패 시 0)
        """
        if 0 <= index < len(self.todos):
            if not self.todos[index]['completed']:
                self.todos[index]['completed'] = True
                todo_text = self.todos[index]['text']
                self._give_snack_item("기본 간식", SNACK_PER_TODO_COMPLETE) # 기본 간식 지급
                print(f"할 일 완료: {todo_text}, 간식 지급: {SNACK_PER_TODO_COMPLETE}개")
                return SNACK_PER_TODO_COMPLETE
            print(f"이미 완료된 할 일입니다: {self.todos[index]['text']}")
            return 0
        print(f"잘못된 인덱스입니다: {index}")
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
            print(f"{snack_name} 1개 사용! 현재 {snack_name} 개수: {self.snack_counts[snack_name]}, 효과: {effect}")
            return effect
        print(f"'{snack_name}' 간식이 없거나 부족합니다.")
        return None

    def get_current_todos(self):
        """현재 할 일 목록을 반환합니다."""
        return self.todos
    
    def get_current_snack_counts(self):
        """현재 간식 개수 딕셔너리를 반환합니다."""
        return self.snack_counts
