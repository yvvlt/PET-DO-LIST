# main.py

import tkinter as tk
from tkinter import simpledialog, messagebox
import datetime
import random 
import os 
# from playsound import playsound # playsound는 더 이상 사용하지 않습니다.
import pygame.mixer as mixer 

import config
from pet_manager import Pet
from todo_manager import TodoManager
import data_manager
from gui import PetDoListGUI 

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
        self.historical_pets = [] 
        self.sfx_sounds = {} # ⭐ 효과음 객체를 저장할 딕셔너리 추가 ⭐

        self.gui = PetDoListGUI(master, self) 
        
        self._pre_gui_setup() 

        # ⭐ BGM 초기화 및 재생 로직 ⭐
        mixer.init() # Pygame 믹서 초기화 (한 번만 호출)
        bgm_path = os.path.join(config.RESOURCES_PATH, config.SOUNDS_SUBFOLDER, config.BGM_FILE)
        if os.path.exists(bgm_path):
            try:
                mixer.music.load(bgm_path) 
                mixer.music.set_volume(config.BGM_VOLUME) 
                mixer.music.play(loops=-1) 
                print(f"BGM '{config.BGM_FILE}' 재생 시작.")
            except Exception as e:
                print(f"BGM 재생 중 오류 발생: {e}")
        else:
            print(f"BGM 파일 '{bgm_path}'을 찾을 수 없어 재생할 수 없습니다. config.BGM_FILE과 파일 경로를 확인해주세요.")

        # ⭐ 모든 효과음 미리 로드 및 볼륨 설정 ⭐
        self._load_sound_effects()

        self.gui.update_gui_with_pet_data() 

    def _load_sound_effects(self):
        """모든 효과음 파일을 로드하고 볼륨을 설정하여 sfx_sounds 딕셔너리에 저장합니다."""
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
                    sound_obj = mixer.Sound(sound_path)
                    sound_obj.set_volume(volume)
                    self.sfx_sounds[key] = sound_obj
                    print(f"효과음 '{filename}' 로드 완료. 볼륨: {volume}")
                except Exception as e:
                    print(f"효과음 '{filename}' 로드 중 오류 발생: {e}")
            else:
                print(f"효과음 파일 '{sound_path}'을 찾을 수 없어 로드할 수 없습니다.")


    def _pre_gui_setup(self):
        """GUI를 생성하기 전에 데이터 로드, 펫 초기화, 환생 체크를 수행합니다."""
        loaded_pet, loaded_daily_todos, loaded_snack_counts, loaded_historical_pets = data_manager.load_data() 

        if loaded_pet and loaded_daily_todos is not None and loaded_snack_counts and loaded_historical_pets is not None:
            self.pet = loaded_pet
            self.todo_manager = TodoManager(initial_daily_todos=loaded_daily_todos, initial_snack_counts=loaded_snack_counts)
            self.historical_pets = loaded_historical_pets 
            print("기존 데이터를 성공적으로 로드했습니다.")
        else:
            print("새로운 데이터를 초기화합니다.")
            self.create_initial_pet_and_data_via_dialog() 

        self.check_weekly_reset()

    def create_initial_pet_and_data_via_dialog(self):
        """새로운 펫과 데이터를 생성하고 사용자에게 이름/종류를 팝업으로 입력받습니다."""
        pet_name = simpledialog.askstring("펫 이름", "새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not pet_name or pet_name.strip() == "":
            pet_name = config.INITIAL_PET_NAME 
        
        selected_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새 펫 종류 선택")

        if selected_species is None: 
            selected_species = config.PET_SPECIES_LIST[0] 
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
                if days_since_reset >= config.PET_RESET_INTERVAL_DAYS or self.pet.last_reset_date.weekday() != config.WEEKLY_RESET_DAY: 
                        print("펫 환생 조건 충족! 새로운 펫을 맞이합니다.")
                        if messagebox.askyesno("펫 환생 알림", f"이번 주 ({self.pet.last_reset_date} ~ {today})의 여정이 끝났습니다!\n새로운 펫으로 환생하시겠어요?", parent=self.master):
                            self.perform_rebirth_via_dialog()
                        else:
                            messagebox.showinfo("알림", "이번 주 펫과 계속 여정을 함께합니다!", parent=self.master)

    def _record_current_pet_history(self):
        """현재 펫의 최종 상태를 역사 기록에 추가합니다."""
        if self.pet:
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
        self._record_current_pet_history()

        new_pet_name = simpledialog.askstring("펫 환생!", f"이전 펫 '{self.pet.name}'이 환생했습니다! 새로운 펫의 이름을 지어주세요:", parent=self.master)
        if not new_pet_name or new_pet_name.strip() == "":
            new_pet_name = config.INITIAL_PET_NAME 
        
        selected_new_species = self.gui.show_pet_species_selection(config.PET_SPECIES_LIST, "새로운 펫 종류 선택")

        if selected_new_species is None: 
            selected_new_species = config.PET_SPECIES_LIST[0] 
            messagebox.showinfo("알림", f"펫 종류를 선택하지 않아 '{selected_new_species}' 펫으로 다시 태어납니다.", parent=self.master)
            
        self.pet.name = new_pet_name 
        self.pet.reset_for_rebirth(new_species=selected_new_species) 
        self.todo_manager = TodoManager() 
        messagebox.showinfo("펫 환생 완료!", f"'{self.pet.name}' ({self.pet.species})으로 새롭게 태어났습니다! 환영해주세요!", parent=self.master)
        self.gui.update_gui_with_pet_data() 
        self.save_all_data()
        self.play_sound("pet_rebirth") # ⭐ 재생할 효과음의 '키'를 전달 ⭐

    def on_closing(self):
        """애플리케이션 종료 시 데이터를 저장하고 윈도우를 닫습니다."""
        self.save_all_data()
        mixer.music.stop() 
        mixer.quit()       
        self.master.destroy()

    def save_all_data(self):
        """현재 모든 데이터를 저장합니다."""
        if self.pet and self.todo_manager:
            data_manager.save_data(self.pet, self.todo_manager.get_daily_todos_data(), self.todo_manager.get_current_snack_counts(), self.historical_pets)
            print("애플리케이션 종료 전 데이터 저장 완료.")
        else:
            print("저장할 데이터가 없어 저장을 건너뛰는 작업을 수행하고 있어요.")

    # ⭐ pygame.mixer.Sound 객체를 재생하도록 play_sound 함수 수정 ⭐
    def play_sound(self, sound_key):
        """
        미리 로드된 효과음 객체를 재생합니다.
        Args:
            sound_key (str): _load_sound_effects에 정의된 사운드 키.
        """
        sound_obj = self.sfx_sounds.get(sound_key)
        if sound_obj:
            try:
                sound_obj.play()
            except Exception as e:
                print(f"효과음 '{sound_key}' 재생 중 오류 발생: {e}")
        else:
            print(f"효과음 키 '{sound_key}'에 해당하는 사운드 객체를 찾을 수 없습니다.")
            
    def _check_and_reward_full_gauges(self):
        """
        펫의 행복도와 포만감 게이지가 모두 최대일 경우,
        아직 보상을 받지 않았다면 고급 간식을 지급합니다.
        게이지가 최대가 아닐 경우 보상 상태를 리셋합니다.
        """
        if not self.pet:
            return

        is_full_happiness = (self.pet.happiness >= self.pet.max_happiness)
        is_full_fullness = (self.pet.fullness >= self.pet.max_fullness)

        if is_full_happiness and is_full_fullness:
            if not self.pet.has_been_rewarded_for_full_gauges:
                self.todo_manager.add_snack("고급 간식", 1) 
                self.pet.has_been_rewarded_for_full_gauges = True 
                
                messagebox.showinfo("특별 보상!", f"'{self.pet.name}'(이)가 행복하고 포만감이 가득찼습니다!\n축하합니다! 고급 간식 1개를 획득했습니다!", parent=self.master)
                self.play_sound("pet_level_up") # ⭐ 재생할 효과음의 '키'를 전달 ⭐
                self.gui.update_gui_with_pet_data()
                self.save_all_data()
                print("고급 간식 1개 지급!")
        else:
            self.pet.has_been_rewarded_for_full_gauges = False
                
    # --- GUI 이벤트 핸들러 (PetDoListGUI에서 호출될 실제 로직) ---
    def add_todo_logic(self, todo_text):
        if self.todo_manager.add_todo(todo_text): 
            self.gui.update_gui_with_pet_data()
            self.save_all_data() 
            self._check_and_reward_full_gauges() 
            return True
        return False

    def complete_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): 
            if self.todo_manager.get_current_date_todos()[index]['completed']: 
                messagebox.showinfo("알림", "이미 완료된 할 일입니다.", parent=self.master)
                return False

            snack_reward_count = self.todo_manager.complete_todo(index) 
            if snack_reward_count > 0:
                leveled_up = self.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE) 
                
                self.play_sound("todo_complete") # ⭐ 재생할 효과음의 '키'를 전달 ⭐

                if leveled_up:
                    self.play_sound("pet_level_up") # ⭐ 재생할 효과음의 '키'를 전달 ⭐
                    messagebox.showinfo("레벨업!", f"'{self.pet.name}'이(가) 레벨 {self.pet.level}로 성장했습니다!", parent=self.master)

                self.gui.update_gui_with_pet_data() 
                self.save_all_data() 
                self._check_and_reward_full_gauges() 
                return True
        messagebox.showerror("오류", "할 일 완료 처리에 실패했습니다.", parent=self.master)
        return False
            
    def remove_todo_logic(self, index):
        if 0 <= index < len(self.todo_manager.get_current_date_todos()): 
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master):
                self.todo_manager.remove_todo(index)
                self.gui.update_gui_with_pet_data()
                self.save_all_data() 
                self._check_and_reward_full_gauges() 
                return True
            return False # 사용자 취소
        messagebox.showerror("오류", "할 일 삭제 처리에 실패했습니다.", parent=self.master) # 인덱스 오류 등
        return False


    def give_snack_to_pet(self, snack_name):
        if self.pet.happiness >= self.pet.max_happiness and self.pet.fullness >= self.pet.max_fullness:
            messagebox.showinfo("알림", f"'{self.pet.name}'(이)는 이미 행복하고 배불러서 더 이상 간식을 먹을 수 없어요! 조금 쉬게 해주세요 :)", parent=self.master)
            return False 

        effect = self.todo_manager.use_snack(snack_name)
        if effect:
            self.pet.give_snack(effect)
            self.play_sound("snack_give") # ⭐ 재생할 효과음의 '키'를 전달 ⭐
            self.gui.update_gui_with_pet_data() 
            self.save_all_data() 
            self._check_and_reward_full_gauges() 
            return True
        else:
            messagebox.showinfo("알림", f"'{snack_name}' 간식이 없거나 부족합니다.", parent=self.master)
            return False

    def change_date_logic(self, delta_days):
        current_display_date = self.todo_manager.get_current_date()
        new_display_date = current_display_date + datetime.timedelta(days=delta_days)
        self.todo_manager.set_current_date(new_display_date)
        self.gui.update_gui_with_pet_data() 
        print(f"날짜 변경: {current_display_date} -> {new_display_date}")
        self._check_and_reward_full_gauges() 
        return True 
        
    def delete_historical_pet_record(self, index): 
        if 0 <= index < len(self.historical_pets):
            deleted_record = self.historical_pets.pop(index)
            print(f"과거 펫 기록 삭제됨: {deleted_record}")
            self.save_all_data()
            return True
        return False

# --- 애플리케이션 실행 ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PetDoListApp(root)
    root.mainloop()