# gui.py

import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox 
from PIL import Image, ImageTk 
import os 
import datetime 

import config 

# === 펫 종류 선택 모달 다이얼로그 클래스 ===
class PetSpeciesSelectionDialog(tk.Toplevel):
    def __init__(self, parent, species_list, title="펫 종류 선택"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()        
        self.title(title)
        self.result = None     

        self.protocol("WM_DELETE_WINDOW", self._on_closing) 

        self.update_idletasks()
        dialog_width = 300
        dialog_height = 150 + (len(species_list) * 50) 
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, False)

        tk.Label(self, text="어떤 종류의 펫을 키우시겠어요?", font=(config.MAIN_FONT_FAMILY, 14, "bold"), pady=10).pack() # ⭐ 폰트 적용 ⭐

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        for species in species_list:
            btn = tk.Button(button_frame, text=species, width=15, height=2,
                            command=lambda s=species: self._on_select(s),
                            font=(config.MAIN_FONT_FAMILY, 12), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            
        self.wait_window(self)

    def _on_select(self, species):
        self.result = species
        self.destroy()

    def _on_closing(self):
        self.result = None
        self.destroy()
        

# === 과거 펫 기록 보기 다이얼로그 클래스 ===
class HistoricalPetViewerDialog(tk.Toplevel):
    def __init__(self, parent, historical_pets, pet_image_loader_func, app_logic, title="펫 기록 보기"): 
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.pet_image_loader_func = pet_image_loader_func 
        self.app_logic = app_logic 

        dialog_width = 500
        dialog_height = 600
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, True) 

        tk.Label(self, text="🌟 나의 펫 성장 기록 🌟", font=(config.MAIN_FONT_FAMILY, 18, "bold"), pady=10, fg=config.ACCENT_COLOR).pack() # ⭐ 폰트 적용 ⭐

        self.canvas = tk.Canvas(self, borderwidth=0, background=config.BG_COLOR)
        self.record_frame = tk.Frame(self.canvas, background=config.BG_COLOR)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.record_frame, anchor="nw", 
                                  tags="self.record_frame")

        self.record_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)

        self._build_records_display()

        self.wait_window(self)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _build_records_display(self):
        for widget in self.record_frame.winfo_children():
            widget.destroy()

        historical_pets = self.app_logic.historical_pets 
        if not historical_pets:
            tk.Label(self.record_frame, text="아직 저장된 펫 기록이 없습니다.", font=(config.MAIN_FONT_FAMILY, 12), fg="gray", bg=config.BG_COLOR).pack(pady=20) # ⭐ 폰트 적용 ⭐
        else:
            for i in range(len(historical_pets) -1, -1, -1):
                record = historical_pets[i]
                self._create_record_entry(record, i) 
        
        self.on_frame_configure(None) 

    def _create_record_entry(self, record, index): 
        entry_frame = tk.Frame(self.record_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10, bg="white")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        image_size = (60, 60) 
        image_filename = f"{record['species']}_level{record['level']}.png"
        pet_img = self.pet_image_loader_func(image_filename, size=image_size)

        img_label = tk.Label(entry_frame, image=pet_img, bg="white")
        img_label.image = pet_img 
        img_label.pack(side=tk.LEFT, padx=10)

        info_text = (
            f"기간: {record['start_date'].strftime('%Y/%m/%d')} ~ {record['end_date'].strftime('%Y/%m/%d')}\n"
            f"펫 종류: {record['species']}\n"
            f"최종 레벨: Lv. {record['level']}"
        )
        info_label = tk.Label(entry_frame, text=info_text, justify=tk.LEFT, font=(config.MAIN_FONT_FAMILY, 10), bg="white") # ⭐ 폰트 적용 ⭐
        info_label.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # ⭐ 삭제 버튼 추가 ⭐
        delete_button = tk.Button(entry_frame, text="삭제", 
                                  command=lambda idx=index: self._delete_record(idx), 
                                  font=(config.MAIN_FONT_FAMILY, 9), bg="red", fg="white") # ⭐ 폰트 적용 ⭐
        delete_button.pack(side=tk.RIGHT, padx=5, pady=5) 


    def _delete_record(self, index):
        if messagebox.askyesno("기록 삭제", "정말 이 펫의 기록을 삭제하시겠습니까?", parent=self):
            if self.app_logic.delete_historical_pet_record(index):
                self._build_records_display()
            else:
                messagebox.showerror("오류", "기록 삭제에 실패했습니다.", parent=self)


class PetDoListGUI:
    def __init__(self, master, app_logic):
        self.master = master
        self.app_logic = app_logic 
        
        # main.py에서 이미 title, geometry 등을 설정했으므로 여기서 다시 설정하지 않음.
        # self.master.title(config.APP_TITLE)
        # self.master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        # self.master.resizable(False, False) 
        # self.master.configure(bg=config.BG_COLOR) 

        self.pet_image_cache = {} 
        
        self._create_widgets() 
        self._setup_layout()   
        

    def _create_widgets(self):
        """GUI에 필요한 위젯들을 생성합니다."""
        
        # --- 1. 좌측 패널 (펫 정보 및 이미지) ---
        self.left_panel = tk.Frame(self.master, bg=config.PRIMARY_COLOR, bd=5, relief=tk.RIDGE)
        
        self.pet_name_label = tk.Label(self.left_panel, text="이름: {펫 이름}", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐
        self.pet_canvas = tk.Canvas(self.left_panel, width=300, height=300, bg=config.PRIMARY_COLOR, highlightthickness=0)
        self.pet_photo_label = tk.Label(self.pet_canvas, bg=config.PRIMARY_COLOR) 
        self.pet_species_level_label = tk.Label(self.left_panel, text="종류: {펫 종류} / Lv. {펫 레벨}", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_MEDIUM), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.exp_label = tk.Label(self.left_panel, text="EXP: --/--", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐
        
        self.happiness_label = tk.Label(self.left_panel, text="행복도", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR, bd=0, highlightthickness=0) # ⭐ 폰트 적용 ⭐
        self.happiness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate") 

        self.fullness_label = tk.Label(self.left_panel, text="포만감", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR, bd=0, highlightthickness=0) # ⭐ 폰트 적용 ⭐
        self.fullness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate") 
        
        self.spacer_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR)
        self.snack_buttons_row_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR, bd=0, highlightthickness=0)
        self.snack_button = tk.Button(self.snack_buttons_row_frame, text="간식 주기 (기본)", command=lambda: self.app_logic.give_snack_to_pet("기본 간식"), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.snack_premium_button = tk.Button(self.snack_buttons_row_frame, text="간식 주기 (고급)", command=lambda: self.app_logic.give_snack_to_pet("고급 간식"), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        
        self.action_buttons_row_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR, bd=0, highlightthickness=0) 
        self.view_history_button = tk.Button(self.action_buttons_row_frame, text="펫 기록 보기", command=self.show_pet_history, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.rebirth_button = tk.Button(self.action_buttons_row_frame, text="강제 환생 (테스트)", command=self.app_logic.perform_rebirth_via_dialog, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg="lightgray") # ⭐ 폰트 적용 ⭐


        # --- 2. 우측 패널 (투두리스트 및 간식 인벤토리) ---
        self.right_panel = tk.Frame(self.master, bg=config.BG_COLOR, bd=5, relief=tk.RIDGE)
        
        self.date_nav_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        self.current_date_label = tk.Label(self.date_nav_frame, text="----년 --월 --일", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_MEDIUM, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐
        self.prev_day_button = tk.Button(self.date_nav_frame, text="◀ 이전 날짜", command=lambda: self.app_logic.change_date_logic(-1), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.next_day_button = tk.Button(self.date_nav_frame, text="다음 날짜 ▶", command=lambda: self.app_logic.change_date_logic(1), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        
        self.todo_label = tk.Label(self.right_panel, text="오늘 할 일", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐
        self.todo_listbox = tk.Listbox(self.right_panel, height=10, font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), selectmode=tk.SINGLE, bd=2, relief=tk.GROOVE) # ⭐ 폰트 적용 ⭐
        self.todo_scrollbar = tk.Scrollbar(self.right_panel, orient="vertical", command=self.todo_listbox.yview)
        self.todo_listbox.config(yscrollcommand=self.todo_scrollbar.set)
        
        self.todo_entry = tk.Entry(self.right_panel, font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bd=2, relief=tk.GROOVE) # ⭐ 폰트 적용 ⭐
        self.add_todo_button = tk.Button(self.right_panel, text="할 일 추가", command=self.add_todo_from_entry, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.complete_todo_button = tk.Button(self.right_panel, text="할 일 완료", command=self.complete_selected_todo, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.PRIMARY_COLOR, fg="white") # ⭐ 폰트 적용 ⭐
        self.remove_todo_button = tk.Button(self.right_panel, text="할 일 삭제", command=self.remove_selected_todo, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg="red", fg="white") # ⭐ 폰트 적용 ⭐

        self.snack_inventory_label = tk.Label(self.right_panel, text="간식 인벤토리", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐
        self.snack_list_label = tk.Label(self.right_panel, text="기본 간식: {X}개, 고급 간식: {Y}개", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR) # ⭐ 폰트 적용 ⭐


    def _setup_layout(self):
        """생성된 위젯들을 화면에 배치합니다."""
        
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True)
        self.pet_name_label.pack(pady=10)
        self.pet_canvas.pack(pady=5)
        self.pet_photo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) 
        self.pet_species_level_label.pack(pady=5)
        self.exp_label.pack(pady=5)
        
        self.happiness_label.pack(pady=(0,0)) 
        self.happiness_bar.pack(pady=(0,0))   
        
        self.fullness_label.pack(pady=(0,0)) 
        self.fullness_bar.pack(pady=(0,0))   
        
        self.spacer_frame.pack(side=tk.TOP, expand=True, fill=tk.Y)
        self.snack_buttons_row_frame.pack(side=tk.TOP, pady=(5, 5), fill=tk.X, expand=False)
        self.snack_buttons_row_frame.grid_columnconfigure(0, weight=1) 
        self.snack_buttons_row_frame.grid_columnconfigure(1, weight=0) 
        self.snack_buttons_row_frame.grid_columnconfigure(2, weight=0) 
        self.snack_buttons_row_frame.grid_columnconfigure(3, weight=1) 
        
        self.snack_button.grid(row=0, column=1, padx=5, ipadx=10, ipady=5)
        self.snack_premium_button.grid(row=0, column=2, padx=5, ipadx=10, ipady=5)
        
        self.action_buttons_row_frame.pack(side=tk.TOP, pady=(5, 50), fill=tk.X, expand=False) 
        self.action_buttons_row_frame.grid_columnconfigure(0, weight=1)
        self.action_buttons_row_frame.grid_columnconfigure(1, weight=0)
        self.action_buttons_row_frame.grid_columnconfigure(2, weight=0)
        self.action_buttons_row_frame.grid_columnconfigure(3, weight=1)

        self.view_history_button.grid(row=0, column=1, padx=5, ipadx=10, ipady=5) 
        self.rebirth_button.grid(row=0, column=2, padx=5, ipadx=10, ipady=5) 


        # --- 우측 패널 (pack으로 관리) ---
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True)
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
        image_path_key = f"{image_filename}_{size[0]}x{size[1]}" 
        
        if image_path_key not in self.pet_image_cache:
            try:
                full_path = os.path.join(config.RESOURCES_PATH, config.PET_IMAGES_SUBFOLDER, image_filename)
                print(f"DEBUG: 이미지 로드 시도 경로: {full_path}")
                original_image = Image.open(full_path)
                resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
                self.pet_image_cache[image_path_key] = ImageTk.PhotoImage(resized_image)
            except FileNotFoundError:
                print(f"이미지 파일 '{full_path}'을 찾을 수 없습니다.")
                if 'error_image' not in self.pet_image_cache:
                    error_image_path = os.path.join(config.RESOURCES_PATH, "no_image.png") 
                    try:
                        error_img_orig = Image.open(error_image_path)
                        error_img_resized = error_img_orig.resize(size, Image.Resampling.LANCZOS)
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(error_img_resized)
                    except FileNotFoundError:
                        print(f"기본 에러 이미지 파일 '{error_image_path}'도 찾을 수 없습니다. 빈 이미지로 처리합니다.")
                        empty_img = Image.new('RGBA', size, (0, 0, 0, 0))
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
        """app_logic (main.py)의 펫 데이터를 기반으로 GUI 업데이트"""

        pet = self.app_logic.pet
        if pet:
            self.pet_name_label.config(text=f"이름: {pet.name}")
            self.pet_species_level_label.config(text=f"종류: {pet.species} / Lv. {pet.level}")
            
            # ⭐ 경험치 라벨 업데이트 로직 재점검 ⭐
            if pet.level >= config.MAX_PET_LEVEL:
                exp_display_text = "EXP: MAX" 
            else:
                required_exp = pet.get_required_exp_for_level_up()
                exp_display_text = f"EXP: {pet.exp}/{required_exp}"
            
            self.exp_label.config(text=exp_display_text) 

            image_filename = f"{pet.species}_level{pet.level}.png" 
            pet_image = self.load_pet_image(image_filename) 

            if pet_image:
                self.pet_photo_label.config(image=pet_image)
                self.pet_photo_label.image = pet_image 
            else:
                self.pet_photo_label.config(image='') 

            self.happiness_bar['value'] = pet.happiness
            self.happiness_bar['maximum'] = pet.max_happiness
            self.fullness_bar['value'] = pet.fullness
            self.fullness_bar['maximum'] = pet.max_fullness
        else:
            self.pet_name_label.config(text="이름: ---")
            self.pet_species_level_label.config(text="종류: --- / Lv. --")
            self.exp_label.config(text="EXP: --/--") 
            self.pet_photo_label.config(image='') 
            self.happiness_bar['value'] = 0
            self.fullness_bar['value'] = 0

        current_display_date = self.app_logic.todo_manager.get_current_date()
        self.current_date_label.config(text=current_display_date.strftime("%Y년 %m월 %d일"))
        
        self.todo_listbox.delete(0, tk.END) 
        todos = self.app_logic.todo_manager.get_current_date_todos() 
        for i, todo in enumerate(todos):
            display_text = f"[{'✅' if todo['completed'] else '☐'}] {todo['text']}"
            self.todo_listbox.insert(tk.END, display_text)
            if todo['completed']:
                self.todo_listbox.itemconfig(tk.END, {'fg': 'gray'}) 

        snack_counts = self.app_logic.todo_manager.get_current_snack_counts()
        snack_text_parts = []
        for snack_name, count in snack_counts.items():
            if count > 0: 
                snack_text_parts.append(f"{snack_name}: {count}개")
        
        snack_text = ", ".join(snack_text_parts)
        if not snack_text:
            snack_text = "보유 간식이 없습니다."
        self.snack_list_label.config(text=snack_text)
        
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

    def show_pet_species_selection(self, species_list, dialog_title="펫 종류 선택"):
        dialog = PetSpeciesSelectionDialog(self.master, species_list, dialog_title)
        return dialog.result

    def show_pet_history(self):
        """펫 기록 보기 다이얼로그를 표시합니다."""
        history_dialog = HistoricalPetViewerDialog(
            self.master, 
            self.app_logic.historical_pets, 
            self.load_pet_image,
            self.app_logic 
        )