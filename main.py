# main.py

import tkinter as tk
from tkinter import simpledialog, messagebox
import datetime
import random 

# 우리가 만든 모듈들 임포트
import config
from pet_manager import Pet
from todo_manager import TodoManager
import data_manager
from gui import PetDoListGUI # gui.py에서 PetDoListGUI를 임포트합니다!

class PetDoListApp:
    def __init__(self, master):
        self.master = master
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.resizable(False, False) 
        master.configure(bg=config.BG_COLOR) 
        master.protocol("WM_DELETE_WINDOW", self.on_closing) 

        self.pet = None
        self.todo_manager = None
        self.historical_pets = [] # ⭐ 새로 추가: 과거 펫 기록 리스트 초기화

        # --- 데이터 초기화 및 펫 환생 체크 ---
        self._pre_gui_setup() 
        
        # --- GUI 인스턴스 생성 ---
        self.gui = PetDoListGUI(master, self) # 이제 gui가 app_logic(self)를 통해 historical_pets에 접근할 수 있습니다.

        # --- 초기 GUI 상태 업데이트 ---
        self.gui.update_gui_with_pet_data()


    def _pre_gui_setup(self):
        """GUI를 생성하기 전에 데이터 로드, 펫 초기화, 환생 체크를 수행합니다."""
        # ⭐ data_manager.load_data()에서 historical_pets도 함께 로드합니다.
        loaded_pet, loaded_daily_todos, loaded_snack_counts, loaded_historical_pets = data_manager.load_data() 

        if loaded_pet and loaded_daily_todos is not None and loaded_snack_counts and loaded_historical_pets is not None:
            # 저장된 데이터가 있을 경우 로드
            self.pet = loaded_pet
            self.todo_manager = TodoManager(initial_daily_todos=loaded_daily_todos, initial_snack_counts=loaded_snack_counts)
            self.historical_pets = loaded_historical_pets # ⭐ 과거 펫 기록 로드
            print("기존 데이터를 성공적으로 로드했습니다.")
        else:
            # 저장된 데이터가 없거나 유효하지 않을 경우 새로 생성
            print("새로운 데이터를 초기화합니다.")
            self.create_initial_pet_and_data_via_dialog() 
            # ⭐ 새로운 데이터를 생성할 때 historical_pets는 빈 리스트로 유지됩니다.

        # 펫이 로드되거나 새로 생성된 후, 주간 환생 체크
        self.check_weekly_reset()

    def create_initial_pet_and_data_via_dialog(self):
        """새로운 펫과 데이터를 생성하고 사용자에게 이름/종류를 팝업으로 입력받습니다."""
        
        # 1. 펫 이름 입력 받기
        pet_name = simpledialog.askstring("펫 이름", "새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not pet_name or pet_name.strip() == "":
            pet_name = config.INITIAL_PET_NAME 
        
        # 2. 펫 종류 선택 받기 (버튼으로 선택하도록 변경)
        selected_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새 펫 종류 선택")

        if selected_species is None: # 사용자가 팝업을 닫았거나 선택하지 않은 경우
            selected_species = config.PET_SPECIES_LIST[0] # 기본값으로 첫 번째 종 사용
            messagebox.showinfo("알림", f"펫 종류를 선택하지 않아 '{selected_species}' 펫으로 시작합니다.", parent=self.master)


        self.pet = Pet(name=pet_name, species=selected_species)
        self.todo_manager = TodoManager() 
        messagebox.showinfo("펫 생성", f"'{self.pet.name}' ({self.pet.species}) 펫과 함께 Pet-Do-List를 시작합니다!", parent=self.master)
        print(f"새로운 펫 '{self.pet.name}' ({self.pet.species}) 생성 완료!")


    def check_weekly_reset(self):
        """매주 지정된 요일/시간에 펫이 환생했는지 확인하고 처리합니다."""
        today = datetime.date.today()
        if self.pet: 
            days_since_reset = (today - self.pet.last_reset_date).days
            is_reset_day_and_time = (today.weekday() == config.WEEKLY_RESET_DAY and datetime.datetime.now().hour >= config.RESET_TIME_HOUR)

            if today != self.pet.last_reset_date and is_reset_day_and_time:
                if days_since_reset >= config.PET_RESET_INTERVAL_DAYS or self.pet.last_reset_date.weekday() != config.WEEKLY_RESET_DAY: # ⭐ PET_RESET_INTERVAL_DAYS 사용
                    print("펫 환생 조건 충족! 새로운 펫을 맞이합니다.")
                    if messagebox.askyesno("펫 환생 알림", f"이번 주 ({self.pet.last_reset_date} ~ {today})의 여정이 끝났습니다!\n새로운 펫으로 환생하시겠어요?", parent=self.master):
                        self.perform_rebirth_via_dialog()
                    else:
                        messagebox.showinfo("알림", "이번 주 펫과 계속 여정을 함께합니다!", parent=self.master)

    def _record_current_pet_history(self):
        """현재 펫의 최종 상태를 역사 기록에 추가합니다."""
        if self.pet:
            # ⭐ 펫의 생존 기간을 계산합니다.
            end_date = datetime.date.today()
            start_date = self.pet.last_reset_date
            
            pet_record = {
                'species': self.pet.species,
                'level': self.pet.level,
                'start_date': start_date,
                'end_date': end_date
            }
            self.historical_pets.append(pet_record)
            print(f"과거 펫 기록 추가: {pet_record}")


    def perform_rebirth_via_dialog(self):
        """펫을 환생시키고 초기 데이터를 재설정하며 사용자에게 입력받습니다."""
        print("펫 환생을 시작합니다!")
        
        # ⭐ 현재 펫의 기록을 남깁니다. (새로운 펫이 생성되기 전에 호출)
        self._record_current_pet_history()

        # 새 펫 이름 입력
        new_pet_name = simpledialog.askstring("펫 환생!", f"이전 펫 '{self.pet.name}'이 환생했습니다! 새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not new_pet_name or new_pet_name.strip() == "":
            new_pet_name = config.INITIAL_PET_NAME 
        
        # 새 펫 종류 선택 (버튼으로 선택하도록 변경)
        selected_new_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새로운 펫 종류 선택")

        if selected_new_species is None: # 사용자가 팝업을 닫았거나 선택하지 않은 경우
            selected_new_species = config.PET_SPECIES_LIST[0] # 기본값으로 첫 번째 종 사용
            messagebox.showinfo("알림", f"펫 종류를 선택하지 않아 '{selected_new_species}' 펫으로 다시 태어납니다.", parent=self.master)
            
        self.pet.name = new_pet_name 
        self.pet.reset_for_rebirth(new_species=selected_new_species) 
        self.todo_manager = TodoManager() 
        messagebox.showinfo("펫 환생 완료!", f"'{self.pet.name}' ({self.pet.species})으로 새롭게 태어났습니다! 환영해주세요!", parent=self.master)
        self.gui.update_gui_with_pet_data() 
        self.save_all_data()

    def on_closing(self):
        """애플리케이션 종료 시 데이터를 저장하고 윈도우를 닫습니다."""
        self.save_all_data()
        self.master.destroy()

    def save_all_data(self):
        """현재 모든 데이터를 저장합니다."""
        if self.pet and self.todo_manager:
            # ⭐ save_data 함수에 historical_pets 데이터를 전달합니다.
            data_manager.save_data(self.pet, self.todo_manager.get_daily_todos_data(), self.todo_manager.get_current_snack_counts(), self.historical_pets)
            print("애플리케이션 종료 전 데이터 저장 완료.")
        else:
            print("저장할 데이터가 없어 저장을 건너뜁니다.")

    # --- GUI 이벤트 핸들러 (PetDoListGUI에서 호출될 실제 로직) ---
    def add_todo_logic(self, todo_text):
        if self.todo_manager.add_todo(todo_text): 
            self.gui.update_gui_with_pet_data()
            self.save_all_data() 
            return True
        return False

    def complete_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): 
            if self.todo_manager.get_current_date_todos()[index]['completed']: 
                messagebox.showinfo("알림", "이미 완료된 할 일입니다.", parent=self.master)
                return False

            snack_reward_count = self.todo_manager.complete_todo(index) 
            if snack_reward_count > 0:
                self.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE) 
                self.gui.update_gui_with_pet_data() 
                self.save_all_data() 
                return True
        messagebox.showerror("오류", "할 일 완료 처리에 실패했습니다.", parent=self.master)
        return False
            
    def remove_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): 
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master):
                self.todo_manager.remove_todo(index)
                self.gui.update_gui_with_pet_data()
                self.save_all_data() 
                return True
        return False

    def give_snack_to_pet(self, snack_name):
        effect = self.todo_manager.use_snack(snack_name)
        if effect:
            self.pet.give_snack(effect)
            self.gui.update_gui_with_pet_data() 
            self.save_all_data() 
            return True
        else:
            messagebox.showinfo("알림", f"'{snack_name}' 간식이 없거나 부족합니다.", parent=self.master)
            return False

    def change_date_logic(self, delta_days):
        """
        현재 표시되는 할 일의 날짜를 변경합니다.
        Args:
            delta_days (int): 현재 날짜로부터 이동할 일 수 (예: -1은 하루 전, 1은 하루 후).
        """
        current_display_date = self.todo_manager.get_current_date()
        new_display_date = current_display_date + datetime.timedelta(days=delta_days)
        self.todo_manager.set_current_date(new_display_date)
        self.gui.update_gui_with_pet_data() 
        print(f"날짜 변경: {current_display_date} -> {new_display_date}")


# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PetDoListApp(root)
    root.mainloop()
