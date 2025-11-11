# 메인 어플리케이션 실행 파일 (GUI 생성, 전체 흐름 제어)

import tkinter as tk
from tkinter import simpledialog, messagebox
import datetime
import random # 펫 환생 시 새로운 펫 종류 선택에 사용될 수 있으므로 임포트 유지

# 우리가 만든 모듈들 임포트
import config
from pet_manager import Pet
from todo_manager import TodoManager
import data_manager
from gui import PetDoListGUI # <-- gui.py에서 PetDoListGUI 클래스를 임포트합니다!

class PetDoListApp:
    def __init__(self, master):
        self.master = master
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.resizable(False, False) # gui.py와 동일하게 창 크기 고정
        master.configure(bg=config.BG_COLOR) # gui.py와 동일하게 배경색 설정
        master.protocol("WM_DELETE_WINDOW", self.on_closing) # 윈도우 닫기 버튼(X) 클릭 시 이벤트 연결

        self.pet = None
        self.todo_manager = None
        # self.snack_counts는 이제 todo_manager에서 직접 가져와 사용하므로 별도 멤버 변수는 필요 없습니다.

        # --- 데이터 초기화 및 펫 환생 체크 ---
        self._pre_gui_setup() # GUI 생성 전에 필요한 데이터 로드/펫 초기화 로직 실행
        
        # --- GUI 인스턴스 생성 ---
        # PetDoListGUI에 self(PetDoListApp 인스턴스)를 전달하여 GUI가 앱 로직에 접근할 수 있도록 합니다.
        self.gui = PetDoListGUI(master, self) 

        # --- 초기 GUI 상태 업데이트 --- 
        self.gui.update_gui_with_pet_data() # GUI가 생성된 후 바로 최신 데이터로 업데이트


    def _pre_gui_setup(self):
        """GUI를 생성하기 전에 데이터 로드, 펫 초기화, 환생 체크를 수행합니다."""
        loaded_pet, loaded_todos, loaded_snack_counts = data_manager.load_data()

        if loaded_pet and loaded_todos is not None and loaded_snack_counts:
            # 저장된 데이터가 있을 경우 로드
            self.pet = loaded_pet
            self.todo_manager = TodoManager(initial_todos=loaded_todos, initial_snack_counts=loaded_snack_counts)
            print("기존 데이터를 성공적으로 로드했습니다.")
        else:
            # 저장된 데이터가 없거나 유효하지 않을 경우 새로 생성
            print("새로운 데이터를 초기화합니다.")
            self.create_initial_pet_and_data_via_dialog() # GUI 팝업으로 사용자 입력 받기

        # 펫이 로드되거나 새로 생성된 후, 주간 환생 체크
        self.check_weekly_reset()

    def create_initial_pet_and_data_via_dialog(self):
        """새로운 펫과 데이터를 생성하고 사용자에게 이름/종류를 팝업으로 입력받습니다."""
        
        # 1. 펫 이름 입력 받기
        pet_name = simpledialog.askstring("펫 이름", "새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not pet_name or pet_name.strip() == "":
            pet_name = config.INITIAL_PET_NAME # 입력 없으면 config의 기본 이름 사용
        
        # 2. 펫 종류 선택 받기 (옵션 목록 제공)
        species_options = config.PET_SPECIES_LIST
        species_msg = "환영합니다! 어떤 종류의 펫을 키우시겠어요?\n" + ", ".join(species_options) + "\n\n(입력하지 않으면 '사람' 펫으로 시작합니다)"
        
        selected_species_raw = simpledialog.askstring("펫 종류 선택", species_msg, parent=self.master)

        if selected_species_raw and selected_species_raw.strip() in species_options:
            selected_species = selected_species_raw.strip()
        else:
            selected_species = species_options[0] # 유효하지 않으면 PET_SPECIES_LIST의 첫 번째 종으로 설정 (기본값)
            messagebox.showinfo("알림", f"선택이 유효하지 않아 '{selected_species}' 펫으로 시작합니다.", parent=self.master)

        self.pet = Pet(name=pet_name, species=selected_species)
        self.todo_manager = TodoManager() # 초기 할 일과 간식 개수는 config 값 사용
        messagebox.showinfo("펫 생성", f"'{self.pet.name}' ({self.pet.species}) 펫과 함께 Pet-Do-List를 시작합니다!", parent=self.master)
        print(f"새로운 펫 '{self.pet.name}' ({self.pet.species}) 생성 완료!")


    def check_weekly_reset(self):
        """매주 지정된 요일/시간에 펫이 환생했는지 확인하고 처리합니다."""
        today = datetime.date.today()
        # 펫이 존재해야 체크 가능하며, 이미 환생 여부를 GUI에서 한번 물어봤거나, 아직 펫이 없는 경우는 스킵
        if self.pet: 
            # 마지막 리셋 날짜와 오늘 날짜 비교
            days_since_reset = (today - self.pet.last_reset_date).days
            
            # 주간 리셋 요일과 시간 확인 (예: 매주 월요일 0시)
            is_reset_day_and_time = (today.weekday() == config.WEEKLY_RESET_DAY and datetime.datetime.now().hour >= config.RESET_TIME_HOUR)

            # 마지막 리셋 날짜가 오늘 날짜와 다르고 (즉, 다른 날), 리셋 요일/시간 조건이 충족될 경우
            if today != self.pet.last_reset_date and is_reset_day_and_time:
                 # 그리고 마지막 리셋 이후 7일 이상 지났거나 (지난주 리셋 이후 처음 리셋일 경우)
                 # 또는 마지막 리셋 날짜의 요일이 리셋 요일이 아닌 경우 (예: 수요일에 시작해서 월요일에 리셋하는 경우)
                if days_since_reset >= 7 or self.pet.last_reset_date.weekday() != config.WEEKLY_RESET_DAY:
                    print("펫 환생 조건 충족! 새로운 펫을 맞이합니다.")
                    if messagebox.askyesno("펫 환생 알림", f"이번 주 ({self.pet.last_reset_date} ~ {today})의 여정이 끝났습니다!\n새로운 펫으로 환생하시겠어요?", parent=self.master):
                        self.perform_rebirth_via_dialog()
                    else:
                        messagebox.showinfo("알림", "이번 주 펫과 계속 여정을 함께합니다!", parent=self.master)
            
            # 개발/테스트용 - 강제 환생 로직은 GUI의 버튼에 연결하거나 주석 처리
            # if messagebox.askyesno("개발자 모드", "펫을 지금 강제로 환생시키겠습니까? (테스트용)", parent=self.master):
            #     self.perform_rebirth_via_dialog()


    def perform_rebirth_via_dialog(self):
        """펫을 환생시키고 초기 데이터를 재설정하며 사용자에게 입력받습니다."""
        print("펫 환생을 시작합니다!")
        
        # 새 펫 이름 입력
        new_pet_name = simpledialog.askstring("펫 환생!", f"이전 펫 '{self.pet.name}'이 환생했습니다! 새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not new_pet_name or new_pet_name.strip() == "":
            new_pet_name = config.INITIAL_PET_NAME 
        
        # 새 펫 종류 선택
        species_options = config.PET_SPECIES_LIST
        new_species_msg = f"어떤 종류의 펫으로 다시 태어날까요?\n" + ", ".join(species_options) + "\n\n(입력하지 않으면 '{species_options[0]}' 펫으로 시작합니다)"
        selected_new_species_raw = simpledialog.askstring("새 펫 종류 선택", new_species_msg, parent=self.master)

        if selected_new_species_raw and selected_new_species_raw.strip() in species_options:
            selected_new_species = selected_new_species_raw.strip()
        else:
            selected_new_species = species_options[0] # 유효하지 않으면 첫 번째 종으로 설정
            messagebox.showinfo("알림", f"선택이 유효하지 않아 '{selected_new_species}' 펫으로 다시 태어납니다.", parent=self.master)
            
        self.pet.name = new_pet_name # 펫 이름 업데이트
        self.pet.reset_for_rebirth(new_species=selected_new_species) # 펫 초기화 및 새 종류 설정
        self.todo_manager = TodoManager() # 할 일 목록과 간식은 초기화 (새로운 시작!)
        messagebox.showinfo("펫 환생 완료!", f"'{self.pet.name}' ({self.pet.species})으로 새롭게 태어났습니다! 환영해주세요!", parent=self.master)
        self.gui.update_gui_with_pet_data() # GUI 업데이트
        
        self.save_all_data() # 환생 후 즉시 데이터 저장 (중요!)

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
            print("저장할 데이터가 없어 저장을 건너뜝니다.")

    # --- GUI 이벤트 핸들러 (PetDoListGUI에서 호출될 실제 로직) ---
    def add_todo_logic(self, todo_text):
        if self.todo_manager.add_todo(todo_text):
            self.gui.update_gui_with_pet_data()
            self.save_all_data() # 변경사항 즉시 저장
            return True
        return False

    def complete_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_todos()):
            if self.todo_manager.get_current_todos()[index]['completed']:
                messagebox.showinfo("알림", "이미 완료된 할 일입니다.", parent=self.master)
                return False

            snack_reward_count = self.todo_manager.complete_todo(index) # 간식 지급
            if snack_reward_count > 0:
                self.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE) # 펫 경험치 지급
                self.gui.update_gui_with_pet_data() # GUI 업데이트
                self.save_all_data() # 변경사항 즉시 저장
                return True
        messagebox.showerror("오류", "할 일 완료 처리에 실패했습니다.", parent=self.master)
        return False
            
    def remove_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_todos()):
            if self.todo_manager.remove_todo(index):
                self.gui.update_gui_with_pet_data()
                self.save_all_data() # 변경사항 즉시 저장
                return True
        return False

    def give_snack_to_pet(self, snack_name):
        effect = self.todo_manager.use_snack(snack_name)
        if effect:
            self.pet.give_snack(effect)
            self.gui.update_gui_with_pet_data() # GUI 업데이트
            self.save_all_data() # 변경사항 즉시 저장
            return True
        else:
            messagebox.showinfo("알림", f"'{snack_name}' 간식이 없거나 부족합니다.", parent=self.master)
            return False


# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PetDoListApp(root)
    root.mainloop()
