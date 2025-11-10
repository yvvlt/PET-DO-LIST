# 메인 어플리케이션 실행 파일 (GUI 생성, 전체 흐름 제어)


import tkinter as tk
from tkinter import simpledialog, messagebox # 펫 이름, 종류 입력 및 메시지 박스를 위해 추가
import datetime

# 우리가 만든 모듈들 임포트
import config
from pet_manager import Pet
from todo_manager import TodoManager
import data_manager

class PetDoListApp:
    def __init__(self, master):
        self.master = master
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.protocol("WM_DELETE_WINDOW", self.on_closing) # 윈도우 닫기 버튼(X) 클릭 시 이벤트 연결

        self.pet = None
        self.todo_manager = None
        self.snack_counts = {}

        self.initialize_app_data()
        self.check_weekly_reset()
        
        # --- [임시] GUI가 구현되기 전까지는 콘솔 출력을 사용합니다 ---
        self.display_current_status()
        self.create_test_buttons() # 임시 테스트 버튼 생성
        # --- [임시 끝] ---


    def initialize_app_data(self):
        """저장된 데이터를 로드하거나, 없을 경우 초기 데이터를 생성합니다."""
        loaded_pet, loaded_todos, loaded_snack_counts = data_manager.load_data()

        if loaded_pet and loaded_todos is not None and loaded_snack_counts:
            # 저장된 데이터가 있을 경우 로드
            self.pet = loaded_pet
            self.todo_manager = TodoManager(initial_todos=loaded_todos, initial_snack_counts=loaded_snack_counts)
            self.snack_counts = self.todo_manager.get_current_snack_counts()
            print("기존 데이터를 성공적으로 로드했습니다.")
        else:
            # 저장된 데이터가 없거나 유효하지 않을 경우 새로 생성
            print("새로운 데이터를 초기화합니다.")
            self.create_initial_pet_and_data()

    def create_initial_pet_and_data(self):
        """새로운 펫과 데이터를 생성하고 사용자에게 이름/종류를 입력받습니다."""
        
        # 1. 펫 이름 입력 받기
        # simpledialog는 root 윈도우가 필요하므로 임시로 master를 사용하여 팝업 띄우기
        pet_name = simpledialog.askstring("펫 이름", "새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not pet_name or pet_name.strip() == "":
            pet_name = config.INITIAL_PET_NAME # 입력 없으면 기본 이름 사용
        
        # 2. 펫 종류 선택 받기
        # Combobox를 사용하는 GUI는 gui.py에서 구현해야 더 좋지만, 
        # main.py에서는 simpledialog.askstring으로 일단 대체하여 진행
        species_options = config.PET_SPECIES_LIST
        species_choice = simpledialog.askstring("펫 종류 선택", 
                                                f"펫 종류를 선택하세요: {', '.join(species_options)}\n(기본값: {species_options[0]})",
                                                parent=self.master)
        if species_choice and species_choice.strip() in species_options:
            selected_species = species_choice.strip()
        else:
            selected_species = species_options[0] # 유효하지 않으면 첫 번째 종으로 설정

        self.pet = Pet(name=pet_name, species=selected_species)
        self.todo_manager = TodoManager() # 초기 할 일과 간식 개수는 config 값 사용
        self.snack_counts = self.todo_manager.get_current_snack_counts()
        print(f"새로운 펫 '{self.pet.name}' ({self.pet.species}) 생성 완료!")

    def check_weekly_reset(self):
        """매주 지정된 요일/시간에 펫이 환생했는지 확인하고 처리합니다."""
        today = datetime.date.today()
        # 마지막 리셋 날짜와 오늘 날짜 비교
        if self.pet: # 펫이 존재해야 체크 가능
            days_since_reset = (today - self.pet.last_reset_date).days
            
            # 주간 리셋 요일과 시간 확인 (예: 매주 월요일 0시)
            if today.weekday() == config.WEEKLY_RESET_DAY and datetime.datetime.now().hour >= config.RESET_TIME_HOUR:
                # 마지막 리셋 날짜가 이번 주 리셋 요일보다 이전이고 오늘 리셋이 안된 경우
                # (예: 오늘이 월요일이고, 마지막 리셋이 지난주 금요일)
                if days_since_reset >= 7 or (self.pet.last_reset_date.weekday() != config.WEEKLY_RESET_DAY and days_since_reset > 0):
                    print("펫 환생 조건 충족! 새로운 펫을 맞이합니다.")
                    self.perform_rebirth()
            
            # (선택 사항: 디버깅용) 강제로 환생 로직을 테스트하고 싶을 때 사용
            # if messagebox.askyesno("환생 테스트", "펫을 지금 강제로 환생시키겠습니까?"):
            #     self.perform_rebirth()


    def perform_rebirth(self):
        """펫을 환생시키고 초기 데이터를 재설정합니다."""
        print("펫 환생을 시작합니다!")
        
        # 새 펫 이름 입력
        new_pet_name = simpledialog.askstring("펫 환생!", f"새로운 펫 '{self.pet.name}'이 환생했습니다! 새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not new_pet_name or new_pet_name.strip() == "":
            new_pet_name = config.INITIAL_PET_NAME # 입력 없으면 기본 이름 사용
        
        # 새 펫 종류 선택
        species_options = config.PET_SPECIES_LIST
        new_species_choice = simpledialog.askstring("새 펫 종류 선택", 
                                                    f"환생한 펫의 종류를 선택하세요: {', '.join(species_options)}\n(기본값: {species_options[0]})",
                                                    parent=self.master)
        if new_species_choice and new_species_choice.strip() in species_options:
            selected_new_species = new_species_choice.strip()
        else:
            selected_new_species = species_options[0] # 유효하지 않으면 첫 번째 종으로 설정
            
        self.pet.name = new_pet_name # 이름은 덮어씌움
        self.pet.reset_for_rebirth(new_species=selected_new_species)
        self.todo_manager = TodoManager() # 할 일 목록과 간식은 초기화
        self.snack_counts = self.todo_manager.get_current_snack_counts()
        messagebox.showinfo("펫 환생!", f"'{self.pet.name}' ({self.pet.species})으로 새롭게 태어났습니다! 환영해주세요!", parent=self.master)
        self.display_current_status() # 상태 업데이트 출력

    def on_closing(self):
        """애플리케이션 종료 시 데이터를 저장하고 윈도우를 닫습니다."""
        self.save_all_data()
        self.master.destroy()

    def save_all_data(self):
        """현재 모든 데이터를 저장합니다."""
        if self.pet and self.todo_manager:
            data_manager.save_data(self.pet, self.todo_manager.get_current_todos(), self.todo_manager.get_current_snack_counts())
            print("애플리케이션 종료 전 데이터 저장 완료.")
        else:
            print("저장할 데이터가 없습니다.")

    # --- [임시] GUI 구현 전 테스트를 위한 메서드 ---
    def display_current_status(self):
        """현재 펫과 투두리스트 상태를 콘솔에 출력합니다."""
        if self.pet:
            print("\n--- 현재 펫 상태 ---")
            print(f"이름: {self.pet.name}")
            print(f"종류: {self.pet.species}")
            print(f"레벨: {self.pet.level} (EXP: {self.pet.exp}/{self.pet.get_required_exp_for_level_up()})")
            print(f"행복도: {self.pet.happiness}/{self.pet.max_happiness}")
            print(f"포만감: {self.pet.fullness}/{self.pet.max_fullness}")
            print(f"마지막 환생일: {self.pet.last_reset_date}")
        
        if self.todo_manager:
            print("\n--- 할 일 목록 ---")
            todos = self.todo_manager.get_current_todos()
            if todos:
                for i, todo in enumerate(todos):
                    status = "✅" if todo['completed'] else "☐"
                    print(f"{i}. {status} {todo['text']}")
            else:
                print("할 일이 없습니다.")
            
            print("\n--- 간식 인벤토리 ---")
            snack_counts = self.todo_manager.get_current_snack_counts()
            if snack_counts:
                for snack_name, count in snack_counts.items():
                    print(f"{snack_name}: {count}개")
            else:
                print("보유 간식이 없습니다.")
        print("---------------------\n")

    def create_test_buttons(self):
        """GUI가 완성되기 전, 콘솔 테스트를 위한 임시 버튼들을 생성합니다."""
        frame = tk.Frame(self.master)
        frame.pack(pady=10)

        tk.Label(frame, text="할 일 테스트").pack()
        self.todo_entry = tk.Entry(frame)
        self.todo_entry.pack()
        tk.Button(frame, text="할 일 추가", command=self.add_todo_via_button).pack()
        tk.Button(frame, text="할 일 완료 (0번)", command=lambda: self.complete_todo_via_button(0)).pack()

        tk.Label(frame, text="펫 테스트").pack()
        tk.Button(frame, text="기본 간식 주기", command=lambda: self.give_snack_to_pet("기본 간식")).pack()
        tk.Button(frame, text="고급 간식 주기", command=lambda: self.give_snack_to_pet("고급 간식")).pack()
        tk.Button(frame, text="상태 업데이트", command=self.display_current_status).pack()
        tk.Button(frame, text="강제 환생", command=self.perform_rebirth).pack() # 강제 환생 버튼

    def add_todo_via_button(self):
        todo_text = self.todo_entry.get()
        if self.todo_manager.add_todo(todo_text):
            self.todo_entry.delete(0, tk.END)
            self.display_current_status()
        else:
            messagebox.showerror("오류", "유효한 할 일 내용을 입력해주세요.")

    def complete_todo_via_button(self, index):
        snack_reward = self.todo_manager.complete_todo(index)
        if snack_reward > 0:
            self.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE) # 할 일 완료 경험치 지급
            self.display_current_status()
        elif snack_reward == 0:
            messagebox.showinfo("정보", "이미 완료되었거나, 할 일이 없습니다.")
        else:
            messagebox.showerror("오류", "할 일 완료에 실패했습니다.")


    def give_snack_to_pet(self, snack_name):
        effect = self.todo_manager.use_snack(snack_name)
        if effect:
            self.pet.give_snack(effect)
            self.display_current_status()
        else:
            messagebox.showinfo("정보", f"'{snack_name}' 간식이 없습니다.")


# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PetDoListApp(root)
    root.mainloop()
