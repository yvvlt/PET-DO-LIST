# main.py

# 애플리케이션의 메인 진입점(Entry Point)이자 핵심 로직을 담당하는 파일입니다.
# GUI 생성 및 관리, 데이터 로드/저장, 펫 상태 및 할 일 관리, 사운드 재생 등
# 앱의 전반적인 흐름을 제어하고 각 모듈들을 연결하는 역할을 합니다.

import tkinter as tk            # Tkinter GUI 라이브러리.
from tkinter import simpledialog, messagebox # 사용자 입력 다이얼로그, 알림창.
import datetime                 # 날짜/시간 객체.
import random                   # (현재 코드에서 직접 사용되진 않음, 추후 확장용)
import os                       # 파일 시스템 경로 처리 (사운드 파일 경로 등).
import pygame.mixer as mixer    # 배경 음악(BGM) 및 효과음 재생 모듈 (playsound 대체).

import config                   # 애플리케이션 설정 값.
from pet_manager import Pet     # 펫 관리 로직 클래스.
from todo_manager import TodoManager # 할 일 관리 로직 클래스.
import data_manager             # 데이터 저장/로드 모듈.
from gui import PetDoListGUI    # GUI 인터페이스 클래스.

class PetDoListApp:
    """
    Pet-Do-List 애플리케이션의 메인 클래스.
    GUI, 펫 데이터, 할 일 데이터를 통합 관리하고 앱의 전체적인 동작을 제어합니다.
    """
    def __init__(self, master):
        self.master = master    # Tkinter 루트(메인) 창 객체.
        # 메인 창 설정.
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.resizable(False, False) # 창 크기 조절 불가.
        master.configure(bg=config.BG_COLOR)
        # 창 닫기 버튼 클릭 시 on_closing 메서드 호출.
        master.protocol("WM_DELETE_WINDOW", self.on_closing) 

        self.pet = None             # 현재 펫 객체.
        self.todo_manager = None    # 할 일 관리자 객체.
        self.historical_pets = []   # 과거 펫 기록 리스트.
        self.sfx_sounds = {}        # 로드된 효과음 객체들을 저장할 딕셔너리.

        self.gui = PetDoListGUI(master, self) # GUI 객체 생성 (main 앱 로직 전달).
        
        self._pre_gui_setup() # GUI 생성 전 초기 데이터 로드 및 설정.

        # --- BGM 초기화 및 재생 로직 ---
        mixer.init() # pygame 믹서 초기화 (모든 사운드 재생 전 필수).
        bgm_path = os.path.join(config.RESOURCES_PATH, config.SOUNDS_SUBFOLDER, config.BGM_FILE)
        if os.path.exists(bgm_path):
            try:
                mixer.music.load(bgm_path)        # BGM 파일 로드.
                mixer.music.set_volume(config.BGM_VOLUME) # BGM 볼륨 설정.
                mixer.music.play(loops=-1)        # BGM 무한 반복 재생.
                print(f"BGM '{config.BGM_FILE}' 재생 시작.")
            except Exception as e:
                print(f"BGM 재생 중 오류 발생: {e}")
        else:
            print(f"BGM 파일 '{bgm_path}'을 찾을 수 없어 재생할 수 없습니다. config.BGM_FILE과 파일 경로를 확인해주세요.")

        # 모든 효과음 파일 로드 및 볼륨 설정.
        self._load_sound_effects()

        self.gui.update_gui_with_pet_data() # GUI 화면 초기 데이터로 업데이트.

    def _load_sound_effects(self):
        """
        config에 정의된 모든 효과음 파일을 로드하고 볼륨을 설정하여
        self.sfx_sounds 딕셔너리에 저장합니다.
        """
        sfx_list = {
            "todo_complete": (config.SOUND_EFFECT_TODO_COMPLETE, config.SFX_VOLUME_TODO_COMPLETE),
            "snack_give": (config.SOUND_EFFECT_SNACK_GIVE, config.SFX_VOLUME_SNACK_GIVE),
            "pet_level_up": (config.SOUND_EFFECT_PET_LEVEL_UP, config.SFX_VOLUME_PET_LEVEL_UP),
            "pet_rebirth": (config.SOUND_EFFECT_PET_REBIRTH, config.SFX_VOLUME_PET_REBIRTH),
        }

        for key, (filename, volume) in sfx_list.items():
            sound_path = os.path.join(config.RESOURCES_PATH, config.SOUNDS_SUBFOLDER, filename)
            if os.path.exists(sound_path):
                try:
                    sound_obj = mixer.Sound(sound_path) # 효과음 파일 로드.
                    sound_obj.set_volume(volume)         # 효과음 볼륨 설정.
                    self.sfx_sounds[key] = sound_obj     # 딕셔너리에 저장.
                    print(f"효과음 '{filename}' 로드 완료. 볼륨: {volume}")
                except Exception as e:
                    print(f"효과음 '{filename}' 로드 중 오류 발생: {e}")
            else:
                print(f"효과음 파일 '{sound_path}'을 찾을 수 없어 로드할 수 없습니다.")

    def _pre_gui_setup(self):
        """
        GUI 위젯 생성 전에 필요한 데이터를 로드하고 펫을 초기화하며,
        주간 환생 로직을 체크합니다.
        """
        loaded_pet, loaded_daily_todos, loaded_snack_counts, loaded_historical_pets = data_manager.load_data() 

        if loaded_pet and loaded_daily_todos is not None and loaded_snack_counts and loaded_historical_pets is not None:
            # 기존 데이터가 존재하면 로드합니다.
            self.pet = loaded_pet
            self.todo_manager = TodoManager(initial_daily_todos=loaded_daily_todos, initial_snack_counts=loaded_snack_counts)
            self.historical_pets = loaded_historical_pets 
            print("기존 데이터를 성공적으로 로드했습니다.")
        else:
            # 데이터가 없거나 로드에 실패하면 새로운 펫과 데이터를 생성합니다.
            print("새로운 데이터를 초기화합니다.")
            self.create_initial_pet_and_data_via_dialog() 

        self.check_weekly_reset() # 주간 환생 조건 체크.

    def create_initial_pet_and_data_via_dialog(self):
        """
        사용자에게 펫 이름과 종류를 입력받아 새로운 펫 객체를 생성하고 데이터를 초기화합니다.
        """
        pet_name = simpledialog.askstring("펫 이름", "새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not pet_name or pet_name.strip() == "":
            pet_name = config.INITIAL_PET_NAME # 이름 미입력 시 기본값 사용.
        
        selected_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새 펫 종류 선택") # 펫 종류 선택 다이얼로그 표시.

        if selected_species is None: 
            selected_species = config.PET_SPECIES_LIST[0] # 선택 취소 시 기본 펫 종류 사용.
            messagebox.showinfo("알림", f"펫 종류를 선택하지 않아 '{selected_species}' 펫으로 시작합니다.", parent=self.master)

        self.pet = Pet(name=pet_name, species=selected_species) # 새로운 펫 객체 생성.
        self.todo_manager = TodoManager() # 새로운 할 일 관리자 객체 생성.
        messagebox.showinfo("펫 생성", f"'{self.pet.name}' ({self.pet.species}) 펫과 함께 Pet-Do-List를 시작합니다!", parent=self.master)
        print(f"새로운 펫 '{self.pet.name}' ({self.pet.species}) 생성 완료!")

    def check_weekly_reset(self):
        """
        매주 지정된 요일/시간에 펫의 환생 조건을 확인하고 필요 시 환생을 진행합니다.
        """
        today = datetime.date.today()
        if self.pet: 
            days_since_reset = (today - self.pet.last_reset_date).days # 마지막 리셋일로부터 지난 일수.
            is_reset_day_and_time = (today.weekday() == config.WEEKLY_RESET_DAY and datetime.datetime.now().hour >= config.RESET_TIME_HOUR)

            if today != self.pet.last_reset_date and is_reset_day_and_time: # 오늘 날짜가 마지막 리셋일과 다르고, 환생 요일/시간 조건 충족 시.
                if days_since_reset >= config.PET_RESET_INTERVAL_DAYS or self.pet.last_reset_date.weekday() != config.WEEKLY_RESET_DAY: # 환생 주기 또는 요일 조건 충족 시.
                        print("펫 환생 조건 충족!")
                        if messagebox.askyesno("펫 환생 알림", f"이번 주 ({self.pet.last_reset_date} ~ {today})의 여정이 끝났습니다!\n새로운 펫으로 환생하시겠어요?", parent=self.master):
                            self.perform_rebirth_via_dialog() # 사용자 동의 시 환생 진행.
                        else:
                            messagebox.showinfo("알림", "이번 주 펫과 계속 여정을 함께합니다!", parent=self.master)

    def _record_current_pet_history(self):
        """
        현재 펫의 최종 상태(종류, 레벨, 기간)를 과거 펫 기록 리스트에 추가합니다.
        """
        if self.pet:
            end_date = datetime.date.today()
            start_date = self.pet.last_reset_date
            
            pet_record = {
                'species': self.pet.species,
                'level': self.pet.level,
                'start_date': start_date,
                'end_date': end_date
            }
            self.historical_pets.append(pet_record) # 기록 추가.
            print(f"과거 펫 기록 추가: {pet_record}")

    def perform_rebirth_via_dialog(self):
        """
        펫을 환생시키는 전체 과정을 담당합니다.
        현재 펫 기록 저장, 새 펫 이름/종류 입력받기, 펫 상태 초기화 등을 수행합니다.
        """
        print("펫 환생을 시작합니다!")
        self._record_current_pet_history() # 현재 펫 기록 저장.

        new_pet_name = simpledialog.askstring("펫 환생!", f"이전 펫 '{self.pet.name}'이 환생했습니다! 새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not new_pet_name or new_pet_name.strip() == "":
            new_pet_name = config.INITIAL_PET_NAME # 이름 미입력 시 기본값 사용.
        
        selected_new_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새로운 펫 종류 선택") # 새 펫 종류 선택 다이얼로그.

        if selected_new_species is None: 
            selected_new_species = config.PET_SPECIES_LIST[0] # 선택 취소 시 기본 펫 종류 사용.
            messagebox.showinfo("알림", f"펫 종류를 선택하지 않아 '{selected_new_species}' 펫으로 다시 태어납니다.", parent=self.master)
            
        self.pet.name = new_pet_name # 새 펫 이름 적용.
        self.pet.reset_for_rebirth(new_species=selected_new_species) # 펫 객체 리셋.
        self.todo_manager = TodoManager() # 할 일 관리자 초기화 (모든 할 일 삭제).
        messagebox.showinfo("펫 환생 완료!", f"'{self.pet.name}' ({self.pet.species})으로 새롭게 태어났습니다! 환영해주세요!", parent=self.master)
        self.gui.update_gui_with_pet_data() # GUI 업데이트.
        self.save_all_data() # 데이터 저장.
        self.play_sound("pet_rebirth") # 환생 효과음 재생.

    def on_closing(self):
        """
        애플리케이션 종료 시 호출되는 콜백 함수.
        모든 데이터 저장 및 Tkinter, Pygame 리소스 해제를 담당합니다.
        """
        self.save_all_data()    # 데이터 저장.
        mixer.music.stop()       # BGM 정지.
        mixer.quit()             # Pygame 믹서 종료 (리소스 해제).
        self.master.destroy()    # Tkinter 메인 창 파괴 (앱 종료).

    def save_all_data(self):
        """
        현재 펫, 할 일, 간식, 과거 펫 기록 데이터를 파일에 저장합니다.
        """
        if self.pet and self.todo_manager: # 펫과 할 일 관리자 객체가 존재할 때만 저장.
            data_manager.save_data(self.pet, self.todo_manager.get_daily_todos_data(), self.todo_manager.get_current_snack_counts(), self.historical_pets)
            print("애플리케이션 종료 전 데이터 저장 완료.")
        else:
            print("저장할 데이터가 없어 저장을 건너뛰는 작업을 수행하고 있어요.")

    def play_sound(self, sound_key):
        """
        사전 로드된 효과음 객체를 재생합니다.
        Args:
            sound_key (str): _load_sound_effects에서 정의된 사운드 키 (예: "todo_complete").
        """
        sound_obj = self.sfx_sounds.get(sound_key) # 해당 키의 효과음 객체 가져오기.
        if sound_obj:
            try:
                sound_obj.play() # 효과음 재생.
            except Exception as e:
                print(f"효과음 '{sound_key}' 재생 중 오류 발생: {e}")
        else:
            print(f"효과음 키 '{sound_key}'에 해당하는 사운드 객체를 찾을 수 없습니다.")
            
    def _check_and_reward_full_gauges(self):
        """
        펫의 행복도와 포만감 게이지가 모두 최대일 경우 고급 간식을 지급합니다.
        게이지가 최대가 아닐 경우 보상 상태 플래그를 리셋합니다.
        """
        if not self.pet:
            return

        is_full_happiness = (self.pet.happiness >= self.pet.max_happiness)
        is_full_fullness = (self.pet.fullness >= self.pet.max_fullness)

        if is_full_happiness and is_full_fullness: # 행복도와 포만감이 모두 최대일 경우.
            if not self.pet.has_been_rewarded_for_full_gauges: # 아직 보상을 받지 않았을 경우.
                self.todo_manager.add_snack("고급 간식", 1) # 고급 간식 1개 추가.
                self.pet.has_been_rewarded_for_full_gauges = True # 보상 완료 플래그 설정.
                
                messagebox.showinfo("특별 보상!", f"'{self.pet.name}'(이)가 행복하고 포만감이 가득찼습니다!\n축하합니다! 고급 간식 1개를 획득했습니다!", parent=self.master)
                self.play_sound("pet_level_up") # 레벨업 효과음 재생 (보상 알림).
                self.gui.update_gui_with_pet_data() # GUI 업데이트.
                self.save_all_data() # 데이터 저장.
                print("고급 간식 1개 지급!")
        else:
            self.pet.has_been_rewarded_for_full_gauges = False # 게이지 만점 아닐 시 보상 플래그 리셋.
                
    # --- GUI 이벤트 핸들러 (PetDoListGUI에서 호출될 실제 로직) ---
    def add_todo_logic(self, todo_text):
        """
        새로운 할 일을 추가하는 로직.
        Args:
            todo_text (str): 추가할 할 일 내용.
        Returns:
            bool: 할 일 추가 성공 여부.
        """
        if self.todo_manager.add_todo(todo_text): 
            self.gui.update_gui_with_pet_data() # GUI 업데이트.
            self.save_all_data() # 데이터 저장.
            self._check_and_reward_full_gauges() # 만점 게이지 보상 체크.
            return True
        return False

    def complete_todo_logic(self, index):
        """
        선택된 할 일을 완료 처리하는 로직.
        Args:
            index (int): 완료할 할 일의 인덱스.
        Returns:
            bool: 할 일 완료 성공 여부.
        """
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): # 유효한 인덱스인지 확인.
            if self.todo_manager.get_current_date_todos()[index]['completed']: 
                messagebox.showinfo("알림", "이미 완료된 할 일입니다.", parent=self.master)
                return False

            snack_reward_count = self.todo_manager.complete_todo(index) # 할 일 완료 처리 및 간식 보상 개수 반환.
            if snack_reward_count > 0: # 보상된 간식이 있다면.
                leveled_up = self.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE) # 펫 경험치 추가.
                
                self.play_sound("todo_complete") # 할 일 완료 효과음 재생.

                if leveled_up: # 레벨업 했을 경우.
                    self.play_sound("pet_level_up") # 레벨업 효과음 재생.
                    messagebox.showinfo("레벨업!", f"'{self.pet.name}'이(가) 레벨 {self.pet.level}로 성장했습니다!", parent=self.master)

                self.gui.update_gui_with_pet_data() # GUI 업데이트.
                self.save_all_data() # 데이터 저장.
                self._check_and_reward_full_gauges() # 만점 게이지 보상 체크.
                return True
        messagebox.showerror("오류", "할 일 완료 처리에 실패했습니다.", parent=self.master) # 오류 메시지.
        return False
            
    def remove_todo_logic(self, index):
        """
        선택된 할 일을 삭제 처리하는 로직.
        Args:
            index (int): 삭제할 할 일의 인덱스.
        Returns:
            bool: 할 일 삭제 성공 여부.
        """
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): # 유효한 인덱스인지 확인.
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master): # 사용자 확인.
                self.todo_manager.remove_todo(index) # 할 일 삭제 처리.
                self.gui.update_gui_with_pet_data() # GUI 업데이트.
                self.save_all_data() # 데이터 저장.
                self._check_and_reward_full_gauges() # 만점 게이지 보상 체크.
                return True
            return False # 사용자 취소 시.
        messagebox.showerror("오류", "할 일 삭제 처리에 실패했습니다.", parent=self.master) # 오류 메시지.
        return False


    def give_snack_to_pet(self, snack_name):
        """
        펫에게 간식을 주는 로직.
        Args:
            snack_name (str): 줄 간식의 이름.
        Returns:
            bool: 간식 주기 성공 여부.
        """
        # 펫이 이미 행복도/포만감 만점일 경우 간식 주기 방지.
        if self.pet.happiness >= self.pet.max_happiness and self.pet.fullness >= self.pet.max_fullness:
            messagebox.showinfo("알림", f"'{self.pet.name}'(이)는 이미 행복하고 배불러서 더 이상 간식을 먹을 수 없어요! 조금 쉬게 해주세요 :)", parent=self.master)
            return False 

        effect = self.todo_manager.use_snack(snack_name) # 간식 사용 및 효과 반환.
        if effect: # 간식이 사용되었고 효과가 있다면.
            self.pet.give_snack(effect) # 펫에게 간식 효과 적용.
            self.play_sound("snack_give") # 간식 효과음 재생.
            self.gui.update_gui_with_pet_data() # GUI 업데이트.
            self.save_all_data() # 데이터 저장.
            self._check_and_reward_full_gauges() # 만점 게이지 보상 체크.
            return True
        else:
            messagebox.showinfo("알림", f"'{snack_name}' 간식이 없거나 부족합니다.", parent=self.master)
            return False

    def change_date_logic(self, delta_days):
        """
        표시 날짜를 변경하는 로직.
        Args:
            delta_days (int): 현재 날짜로부터 변경할 일수 (예: -1은 하루 전, 1은 하루 후).
        Returns:
            bool: 날짜 변경 성공 여부 (항상 True).
        """
        current_display_date = self.todo_manager.get_current_date()
        new_display_date = current_display_date + datetime.timedelta(days=delta_days) # 새 표시 날짜 계산.
        self.todo_manager.set_current_date(new_display_date) # 할 일 관리자의 현재 날짜 설정.
        self.gui.update_gui_with_pet_data() # GUI 업데이트.
        print(f"날짜 변경: {current_display_date} -> {new_display_date}")
        self._check_and_reward_full_gauges() # 만점 게이지 보상 체크 (날짜 변경 시 상태 확인).
        return True 
        
    def delete_historical_pet_record(self, index): 
        """
        과거 펫 기록을 삭제하는 로직.
        Args:
            index (int): 삭제할 기록의 인덱스.
        Returns:
            bool: 기록 삭제 성공 여부.
        """
        if 0 <= index < len(self.historical_pets): # 유효한 인덱스인지 확인.
            deleted_record = self.historical_pets.pop(index) # 리스트에서 기록 삭제.
            print(f"과거 펫 기록 삭제됨: {deleted_record}")
            self.save_all_data() # 데이터 저장.
            return True
        return False

# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()       # Tkinter 루트 창 생성.
    app = PetDoListApp(root) # PetDoListApp 인스턴스 생성.
    root.mainloop()      # Tkinter 이벤트 루프 시작 (앱 실행).