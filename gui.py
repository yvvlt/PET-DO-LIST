# Tkinter GUI 관련 코드 (위젯 생성, 레이아웃 관리)
# gui.py

import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox 
from PIL import Image, ImageTk 
import os 
import datetime # 날짜 형식을 지정하기 위해 추가

import config 

class PetDoListGUI:
    def __init__(self, master, app_logic):
        self.master = master
        self.app_logic = app_logic 
        
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.resizable(False, False) 
        master.configure(bg=config.BG_COLOR) 

        self.pet_image_cache = {} 
        
        self._create_widgets() 
        self._setup_layout()   
        self.update_gui_with_pet_data() 

    def _create_widgets(self):
        """GUI에 필요한 위젯들을 생성합니다."""
        
        # --- 1. 좌측 패널 (펫 정보 및 이미지) ---
        self.left_panel = tk.Frame(self.master, bg=config.PRIMARY_COLOR, bd=5, relief=tk.RIDGE)
        
        self.pet_name_label = tk.Label(self.left_panel, text="이름: {펫 이름}", font=("Arial", 20, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.pet_canvas = tk.Canvas(self.left_panel, width=300, height=300, bg=config.PRIMARY_COLOR, highlightthickness=0)
        self.pet_photo_label = tk.Label(self.pet_canvas, bg=config.PRIMARY_COLOR) 
        self.pet_species_level_label = tk.Label(self.left_panel, text="종류: {펫 종류} / Lv. {펫 레벨}", font=("Arial", 14), bg=config.PRIMARY_COLOR, fg="white")
        
        self.happiness_label = tk.Label(self.left_panel, text="행복도", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.happiness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        self.fullness_label = tk.Label(self.left_panel, text="포만감", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.fullness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        self.snack_button = tk.Button(self.left_panel, text="간식 주기 (기본)", command=lambda: self.app_logic.give_snack_to_pet("기본 간식"), font=("Arial", 12, "bold"), bg=config.ACCENT_COLOR, fg="white")
        self.snack_premium_button = tk.Button(self.left_panel, text="간식 주기 (고급)", command=lambda: self.app_logic.give_snack_to_pet("고급 간식"), font=("Arial", 12, "bold"), bg=config.ACCENT_COLOR, fg="white")
        
        # ✨ 여기에 '강제 환생 버튼' 생성 코드가 있습니다! ✨
        self.rebirth_button = tk.Button(self.left_panel, text="강제 환생 (테스트)", command=self.app_logic.perform_rebirth_via_dialog, font=("Arial", 10), bg="lightgray")


        # --- 2. 우측 패널 (투두리스트 및 간식 인벤토리) ---
        self.right_panel = tk.Frame(self.master, bg=config.BG_COLOR, bd=5, relief=tk.RIDGE)
        
        # 날짜 네비게이션 섹션 추가
        self.date_nav_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        self.prev_day_button = tk.Button(self.date_nav_frame, text="◀ 이전 날짜", command=lambda: self.app_logic.change_date_logic(-1), font=("Arial", 10), bg=config.PRIMARY_COLOR, fg="white")
        self.current_date_label = tk.Label(self.date_nav_frame, text="----년 --월 --일", font=("Arial", 14, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.next_day_button = tk.Button(self.date_nav_frame, text="다음 날짜 ▶", command=lambda: self.app_logic.change_date_logic(1), font=("Arial", 10), bg=config.PRIMARY_COLOR, fg="white")
        
        # 투두리스트 섹션
        self.todo_label = tk.Label(self.right_panel, text="오늘 할 일", font=("Arial", 18, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.todo_listbox = tk.Listbox(self.right_panel, height=10, font=("Arial", 12), selectmode=tk.SINGLE, bd=2, relief=tk.GROOVE)
        self.todo_scrollbar = tk.Scrollbar(self.right_panel, orient="vertical", command=self.todo_listbox.yview)
        self.todo_listbox.config(yscrollcommand=self.todo_scrollbar.set)
        
        self.todo_entry = tk.Entry(self.right_panel, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.add_todo_button = tk.Button(self.right_panel, text="할 일 추가", command=self.add_todo_from_entry, font=("Arial", 10, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.complete_todo_button = tk.Button(self.right_panel, text="할 일 완료", command=self.complete_selected_todo, font=("Arial", 10, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.remove_todo_button = tk.Button(self.right_panel, text="할 일 삭제", command=self.remove_selected_todo, font=("Arial", 10, "bold"), bg="red", fg="white")

        # 간식 인벤토리 섹션
        self.snack_inventory_label = tk.Label(self.right_panel, text="간식 인벤토리", font=("Arial", 18, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.snack_list_label = tk.Label(self.right_panel, text="기본 간식: {X}개, 고급 간식: {Y}개", font=("Arial", 12), bg=config.BG_COLOR)


    def _setup_layout(self):
        """생성된 위젯들을 화면에 배치합니다."""
        
        # 좌측 패널 배치 (펫 정보)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=False)
        self.pet_name_label.pack(pady=10)
        self.pet_canvas.pack(pady=5)
        self.pet_photo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) 
        self.pet_species_level_label.pack(pady=5)
        
        self.happiness_label.pack(pady=(10,0))
        self.happiness_bar.pack(pady=5)
        self.fullness_label.pack(pady=(5,0))
        self.fullness_bar.pack(pady=5)
        
        self.snack_button.pack(pady=(15, 5), ipadx=20, ipady=10)
        self.snack_premium_button.pack(pady=(5, 15), ipadx=20, ipady=10)
        
        # ✨ 여기에 '강제 환생 버튼' 배치 코드가 있습니다! ✨
        self.rebirth_button.pack(pady=(5, 15), ipadx=20, ipady=10)


        # 우측 패널 배치 (투두리스트, 인벤토리)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True)
        
        # 날짜 네비게이션 배치
        self.date_nav_frame.pack(fill=tk.X, pady=10)
        self.prev_day_button.pack(side=tk.LEFT, padx=5)
        self.current_date_label.pack(side=tk.LEFT, expand=True)
        self.next_day_button.pack(side=tk.RIGHT, padx=5)

        self.todo_label.pack(pady=10)
        self.todo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.todo_entry.pack(fill=tk.X, pady=5)
        
        todo_button_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        todo_button_frame.pack(fill=tk.X, pady=5)
        self.add_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.complete_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.remove_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.snack_inventory_label.pack(pady=(20, 10))
        self.snack_list_label.pack(pady=5)


    def load_pet_image(self, image_filename, size=(300, 300)):
        """펫 이미지를 로드하고 캐싱하여 성능을 최적화합니다."""
        image_path_key = f"{image_filename}_{size[0]}x{size[1]}" # 캐싱 키에 사이즈 포함
        
        if image_path_key not in self.pet_image_cache:
            try:
                full_path = os.path.join(config.RESOURCES_PATH, image_filename)
                original_image = Image.open(full_path)
                resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
                self.pet_image_cache[image_path_key] = ImageTk.PhotoImage(resized_image)
            except FileNotFoundError:
                print(f"이미지 파일 '{full_path}'을 찾을 수 없습니다.")
                # 에러 이미지 캐싱 (한번만 로드)
                if 'error_image' not in self.pet_image_cache:
                    # 'resources' 폴더 안에 'no_image.png' 파일을 미리 만들어두세요.
                    error_image_path = os.path.join(config.RESOURCES_PATH, "no_image.png") 
                    try:
                        error_img_orig = Image.open(error_image_path)
                        error_img_resized = error_img_orig.resize(size, Image.Resampling.LANCZOS)
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(error_img_resized)
                    except FileNotFoundError:
                        print(f"기본 에러 이미지 파일 '{error_image_path}'도 찾을 수 없습니다. 빈 이미지로 처리합니다.")
                        # 빈 이미지 캐싱
                        empty_img = Image.new('RGBA', size, (0, 0, 0, 0)) # 투명 이미지
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(empty_img)
                    except Exception as e:
                        print(f"에러 이미지 로드 중 오류 발생: {e}. 빈 이미지로 처리합니다.")
                        empty_img = Image.new('RGBA', size, (0, 0, 0, 0))
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(empty_img)
                return self.pet_image_cache['error_image']
            except Exception as e:
                print(f"이미지 로드 중 오류 발생 ({full_path}): {e}")
                return None
        return self.pet_image_cache[image_path_key]

    def update_gui_with_pet_data(self):
        """app_logic (main.py)의 펫 데이터를 기반으로 GUI를 업데이트합니다."""
        
        # --- 1. 펫 정보 업데이트 ---
        pet = self.app_logic.pet
        if pet:
            self.pet_name_label.config(text=f"이름: {pet.name}")
            self.pet_species_level_label.config(text=f"종류: {pet.species} / Lv. {pet.level}")

            image_filename = f"{pet.species}_level{pet.level}.png" 
            pet_image = self.load_pet_image(image_filename) 

            if pet_image:
                self.pet_photo_label.config(image=pet_image)
                self.pet_photo_label.image = pet_image 
            else:
                self.pet_photo_label.config(image='') # 이미지 없으면 제거

            self.happiness_bar['value'] = pet.happiness
            self.happiness_bar['maximum'] = pet.max_happiness
            self.fullness_bar['value'] = pet.fullness
            self.fullness_bar['maximum'] = pet.max_fullness
        else:
            self.pet_name_label.config(text="이름: ---")
            self.pet_species_level_label.config(text="종류: --- / Lv. --")
            self.pet_photo_label.config(image='') 
            self.happiness_bar['value'] = 0
            self.fullness_bar['value'] = 0

        # --- 2. 날짜 표시 업데이트 ---
        current_display_date = self.app_logic.todo_manager.get_current_date()
        self.current_date_label.config(text=current_display_date.strftime("%Y년 %m월 %d일"))
        
        # --- 3. 투두리스트 업데이트 ---
        self.todo_listbox.delete(0, tk.END) 
        todos = self.app_logic.todo_manager.get_current_date_todos() 
        for i, todo in enumerate(todos):
            display_text = f"[{'✅' if todo['completed'] else '☐'}] {todo['text']}"
            self.todo_listbox.insert(tk.END, display_text)
            if todo['completed']:
                self.todo_listbox.itemconfig(tk.END, {'fg': 'gray'}) 

        # --- 4. 간식 인벤토리 업데이트 ---
        snack_counts = self.app_logic.todo_manager.get_current_snack_counts()
        snack_text_parts = []
        for snack_name, count in snack_counts.items():
            if count > 0: 
                snack_text_parts.append(f"{snack_name}: {count}개")
        
        snack_text = ", ".join(snack_text_parts)
        if not snack_text:
            snack_text = "보유 간식이 없습니다."
        self.snack_list_label.config(text=snack_text)
        
    # --- GUI 이벤트 핸들러 (main.py의 app_logic과 연결) ---
    def add_todo_from_entry(self):
        todo_text = self.todo_entry.get()
        if self.app_logic.add_todo_logic(todo_text): 
            self.todo_entry.delete(0, tk.END) 
        else:
            messagebox.showerror("입력 오류", "할 일 내용을 입력해주세요.", parent=self.master)

    def complete_selected_todo(self):
        selected_indices = self.todo_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            self.app_logic.complete_todo_logic(index) 
        else:
            messagebox.showinfo("선택 오류", "완료할 할 일을 선택해주세요.", parent=self.master)

    def remove_selected_todo(self):
        selected_indices = self.todo_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master):
                self.app_logic.remove_todo_logic(index) 
        else:
            messagebox.showinfo("선택 오류", "삭제할 할 일을 선택해주세요.", parent=self.master)
