# gui.py

import tkinter as tk
from tkinter import ttk 
from tkinter import messagebox 
from PIL import Image, ImageTk 
import os 
import datetime 

import config 

# === 펫 종류 선택 모달 다이얼로그 클래스 (이전 코드와 동일) ===
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

        tk.Label(self, text="어떤 종류의 펫을 키우시겠어요?", font=("Arial", 14, "bold"), pady=10).pack()

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        for species in species_list:
            btn = tk.Button(button_frame, text=species, width=15, height=2,
                            command=lambda s=species: self._on_select(s),
                            font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            
        self.wait_window(self)

    def _on_select(self, species):
        self.result = species
        self.destroy()

    def _on_closing(self):
        self.result = None
        self.destroy()
        

# === 과거 펫 기록 보기 다이얼로그 클래스 추가 시작 ===
class HistoricalPetViewerDialog(tk.Toplevel):
    def __init__(self, parent, historical_pets, pet_image_loader_func, title="펫 기록 보기"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.pet_image_loader_func = pet_image_loader_func # 이미지를 로드할 함수 (PetDoListGUI.load_pet_image)

        # 팝업 창의 크기와 위치를 부모 창에 맞게 조정 (임시, 나중에 중앙 배치)
        dialog_width = 500
        dialog_height = 600
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, True) # 높이만 조절 가능하도록

        tk.Label(self, text="🌟 나의 펫 성장 기록 🌟", font=("Arial", 18, "bold"), pady=10, fg=config.PRIMARY_COLOR).pack()

        # 스크롤 가능한 프레임 생성
        self.canvas = tk.Canvas(self, borderwidth=0, background=config.BG_COLOR)
        self.record_frame = tk.Frame(self.canvas, background=config.BG_COLOR)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.record_frame, anchor="nw", tags="self.record_frame")

        self.record_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)


        if not historical_pets:
            tk.Label(self.record_frame, text="아직 저장된 펫 기록이 없습니다.", font=("Arial", 12), fg="gray", bg=config.BG_COLOR).pack(pady=20)
        else:
            # 최신 기록이 위에 오도록 리스트 역순으로 표시
            for record in reversed(historical_pets):
                self._create_record_entry(record)

        self.wait_window(self)

    def on_frame_configure(self, event):
        """내부 프레임 크기가 변경될 때 캔버스 스크롤 영역을 업데이트합니다."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            

    def _create_record_entry(self, record):
        """각 펫 기록에 대한 위젯을 생성하고 record_frame에 배치합니다."""
        entry_frame = tk.Frame(self.record_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10, bg="white")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        # 이미지 로드 (load_pet_image 함수를 통해)
        image_size = (60, 60) # 기록 보기에서는 작게 표시
        image_filename = f"{record['species']}_level{record['level']}.png"
        pet_img = self.pet_image_loader_func(image_filename, size=image_size)

        img_label = tk.Label(entry_frame, image=pet_img, bg="white")
        img_label.image = pet_img # 참조 유지
        img_label.pack(side=tk.LEFT, padx=10)

        # 정보 표시
        info_text = (
            f"기간: {record['start_date'].strftime('%Y/%m/%d')} ~ {record['end_date'].strftime('%Y/%m/%d')}\n"
            f"펫 종류: {record['species']}\n"
            f"최종 레벨: Lv. {record['level']}"
        )
        info_label = tk.Label(entry_frame, text=info_text, justify=tk.LEFT, font=("Arial", 10), bg="white")
        info_label.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

# === 과거 펫 기록 보기 다이얼로그 클래스 추가 끝 ===


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
        self.exp_label = tk.Label(self.left_panel, text="EXP: --/--", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        
        self.happiness_label = tk.Label(self.left_panel, text="행복도", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.happiness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        self.fullness_label = tk.Label(self.left_panel, text="포만감", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.fullness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        self.snack_button_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR)
        self.snack_button = tk.Button(self.left_panel, text="간식 주기 (기본)", command=lambda: self.app_logic.give_snack_to_pet("기본 간식"), font=("Arial", 10, "bold"), bg=config.ACCENT_COLOR, fg="white")
        self.snack_premium_button = tk.Button(self.left_panel, text="간식 주기 (고급)", command=lambda: self.app_logic.give_snack_to_pet("고급 간식"), font=("Arial", 10, "bold"), bg=config.ACCENT_COLOR, fg="white")
        
        self.history_rebirth_button_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR)
        self.view_history_button = tk.Button(self.left_panel, text="펫 기록 보기", command=self.show_pet_history, font=("Arial", 10, "bold"), bg=config.ACCENT_COLOR, fg="white")

        self.rebirth_button = tk.Button(self.left_panel, text="강제 환생 (초기화)", command=self.app_logic.perform_rebirth_via_dialog, font=("Arial", 10), bg="lightgray")


        # --- 2. 우측 패널 (투두리스트 및 간식 인벤토리) ---
        self.right_panel = tk.Frame(self.master, bg=config.BG_COLOR, bd=5, relief=tk.RIDGE)
        
        self.date_nav_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        self.prev_day_button = tk.Button(self.date_nav_frame, text="◀ 이전 날짜", command=lambda: self.app_logic.change_date_logic(-1), font=("Arial", 10), bg=config.PRIMARY_COLOR, fg="white")
        self.current_date_label = tk.Label(self.date_nav_frame, text="----년 --월 --일", font=("Arial", 14, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.next_day_button = tk.Button(self.date_nav_frame, text="다음 날짜 ▶", command=lambda: self.app_logic.change_date_logic(1), font=("Arial", 10), bg=config.PRIMARY_COLOR, fg="white")
        
        self.todo_label = tk.Label(self.right_panel, text="오늘 할 일", font=("Arial", 18, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.todo_listbox = tk.Listbox(self.right_panel, height=10, font=("Arial", 12), selectmode=tk.SINGLE, bd=2, relief=tk.GROOVE)
        self.todo_scrollbar = tk.Scrollbar(self.right_panel, orient="vertical", command=self.todo_listbox.yview)
        self.todo_listbox.config(yscrollcommand=self.todo_scrollbar.set)
        
        self.todo_entry = tk.Entry(self.right_panel, font=("Arial", 12), bd=2, relief=tk.GROOVE)
        self.add_todo_button = tk.Button(self.right_panel, text="할 일 추가", command=self.add_todo_from_entry, font=("Arial", 10, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.complete_todo_button = tk.Button(self.right_panel, text="할 일 완료", command=self.complete_selected_todo, font=("Arial", 10, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.remove_todo_button = tk.Button(self.right_panel, text="할 일 삭제", command=self.remove_selected_todo, font=("Arial", 10, "bold"), bg="red", fg="white")

        self.snack_inventory_label = tk.Label(self.right_panel, text="간식 인벤토리", font=("Arial", 18, "bold"), bg=config.BG_COLOR, fg=config.PRIMARY_COLOR)
        self.snack_list_label = tk.Label(self.right_panel, text="기본 간식: {X}개, 고급 간식: {Y}개", font=("Arial", 12), bg=config.BG_COLOR)

    def _setup_layout(self):
        """생성된 위젯들을 화면에 배치합니다."""


        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=False)
        self.pet_name_label.pack(pady=10)
        self.pet_canvas.pack(pady=5)
        self.pet_photo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) 
        self.pet_species_level_label.pack(pady=5)
        self.exp_label.pack(pady=5)
        
        self.happiness_label.pack(pady=(10,0))
        self.happiness_bar.pack(pady=5)
        self.fullness_label.pack(pady=(5,0))
        self.fullness_bar.pack(pady=5)
        
        self.snack_button_frame.pack(pady=(15,5), fill=tk.X)
        self.snack_button.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        self.snack_premium_button.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5) # 펫 기록 보기 버튼 위에 배치
        
        self.history_rebirth_button_frame.pack(pady=(5,15), fill=tk.X)
        self.view_history_button.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

        self.rebirth_button.pack(side=tk.LEFT, padx=5, ipadx=20, ipady=10)

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
        """펫 이미지를 로드하고 캐싱하여 성능을 최적화합니다."""
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
        
        pet = self.app_logic.pet
        if pet:
            self.pet_name_label.config(text=f"이름: {pet.name}")
            self.pet_species_level_label.config(text=f"종류: {pet.species} / Lv. {pet.level}")
            
            required_exp = pet.get_required_exp_for_level_up()
            self.exp_label.config(text=f"EXP: {pet.exp}/{required_exp if pet.level < config.MAX_PET_LEVEL else 'MAX'}")

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
        """
        펫 종류를 버튼으로 선택하는 모달 다이얼로그를 표시합니다.
        Returns:
            str: 선택된 펫 종류 (사용자가 닫거나 선택하지 않으면 None).
        """
        dialog = PetSpeciesSelectionDialog(self.master, species_list, dialog_title)
        return dialog.result

    # ✨ 새로운 메서드 추가: 펫 기록 보기 다이얼로그 띄우기 ✨
    def show_pet_history(self):
        """과거 펫 기록을 보여주는 다이얼로그를 엽니다."""
        # app_logic(main.py)에서 historical_pets 리스트를 가져와서 전달
        history_dialog = HistoricalPetViewerDialog(
            self.master, 
            self.app_logic.historical_pets, 
            self.load_pet_image # 이미지를 로드할 때 PetDoListGUI의 load_pet_image 함수를 사용
        )