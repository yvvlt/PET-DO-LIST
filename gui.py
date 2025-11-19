# gui.py

# 애플리케이션의 사용자 인터페이스(GUI)를 구성하고 관리하는 모듈입니다.
# Tkinter 위젯을 사용하여 화면을 그리고, main.py의 PetDoListApp과 상호작용합니다.

import tkinter as tk      # Tkinter GUI 라이브러리.
from tkinter import ttk   # Tkinter의 테마 위젯 (예: Progressbar).
from tkinter import messagebox # 메시지 박스 팝업.
from PIL import Image, ImageTk # Pillow 라이브러리: 이미지 처리 및 Tkinter에 표시.
import os                 # 파일 시스템 경로 처리.
import datetime           # 날짜/시간 객체.

import config             # 애플리케이션 설정 값 임포트.

# === 펫 종류 선택 모달 다이얼로그 클래스 ===
# 펫을 생성하거나 환생할 때 사용자에게 펫 종류를 선택하도록 하는 팝업 창입니다.
class PetSpeciesSelectionDialog(tk.Toplevel):
    def __init__(self, parent, species_list, title="펫 종류 선택"):
        super().__init__(parent)
        self.transient(parent)   # 부모 창 위에 항상 표시.
        self.grab_set()          # 다이얼로그가 열려 있는 동안 다른 창 상호작용 방지.
        self.title(title)        # 다이얼로그 창 제목 설정.
        self.result = None       # 선택된 펫 종류를 저장할 변수.

        self.protocol("WM_DELETE_WINDOW", self._on_closing) # 창 닫기 버튼 클릭 시 이벤트 처리.

        # 다이얼로그 창 크기 및 위치 조정.
        self.update_idletasks() # 위젯 배치 전 창 정보 업데이트.
        dialog_width = 300
        dialog_height = 150 + (len(species_list) * 50) 
        parent_x, parent_y = parent.winfo_x(), parent.winfo_y()
        parent_width, parent_height = parent.winfo_width(), parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, False) # 창 크기 조절 불가.

        # "어떤 종류의 펫을 키우시겠어요?" 라벨 생성.
        tk.Label(self, text="어떤 종류의 펫을 키우시겠어요?", font=(config.MAIN_FONT_FAMILY, 14, "bold"), pady=10).pack()

        button_frame = tk.Frame(self) # 펫 종류 버튼들을 담을 프레임.
        button_frame.pack(pady=10)

        # 각 펫 종류별 버튼 생성.
        for species in species_list:
            btn = tk.Button(button_frame, text=species, width=15, height=2,
                            command=lambda s=species: self._on_select(s),
                            font=(config.MAIN_FONT_FAMILY, 12), bg=config.PRIMARY_COLOR, fg="white")
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            
        self.wait_window(self) # 다이얼로그가 닫힐 때까지 대기.

    def _on_select(self, species):
        # 펫 종류 선택 버튼 클릭 시 호출.
        self.result = species # 선택된 펫 종류 저장.
        self.destroy()       # 다이얼로그 파괴.

    def _on_closing(self):
        # 다이얼로그 창 닫기 버튼 클릭 시 호출.
        self.result = None # 결과값 초기화 (선택 취소).
        self.destroy()     # 다이얼로그 파괴.
        

# === 과거 펫 기록 보기 다이얼로그 클래스 ===
# 사용자가 성장시켰던 과거 펫들의 기록을 보여주는 팝업 창입니다.
# 각 기록에 대한 이미지와 정보, 삭제 버튼을 포함합니다.
class HistoricalPetViewerDialog(tk.Toplevel):
    def __init__(self, parent, historical_pets, pet_image_loader_func, app_logic, title="펫 기록 보기"): 
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.pet_image_loader_func = pet_image_loader_func # 펫 이미지 로딩 함수.
        self.app_logic = app_logic                         # main.py의 앱 로직 인스턴스.

        # 다이얼로그 창 크기 및 위치 조정.
        dialog_width = 500
        dialog_height = 600
        parent_x, parent_y = parent.winfo_x(), parent.winfo_y()
        parent_width, parent_height = parent.winfo_width(), parent.winfo_height()
        x = parent_x + (parent_width // 2) - (dialog_width // 2)
        y = parent_y + (parent_height // 2) - (dialog_height // 2)
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        self.resizable(False, True) # 창 높이만 조절 가능.

        # "나의 펫 성장 기록" 제목 라벨.
        tk.Label(self, text="🌟 나의 펫 성장 기록 🌟", font=(config.MAIN_FONT_FAMILY, 18, "bold"), pady=10, fg=config.ACCENT_COLOR).pack()

        # 스크롤 가능한 영역 (Canvas와 Scrollbar 조합).
        self.canvas = tk.Canvas(self, borderwidth=0, background=config.BG_COLOR)
        self.record_frame = tk.Frame(self.canvas, background=config.BG_COLOR) # 기록 엔트리들이 배치될 프레임.
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) # 수직 스크롤바.
        self.canvas.configure(yscrollcommand=self.vsb.set) # Canvas에 스크롤바 연결.

        self.vsb.pack(side="right", fill="y")         # 스크롤바 배치.
        self.canvas.pack(side="left", fill="both", expand=True) # Canvas 배치.
        self.canvas.create_window((4,4), window=self.record_frame, anchor="nw", # Canvas 내에 record_frame 배치.
                                  tags="self.record_frame")

        # 스크롤 기능 바인딩.
        self.record_frame.bind("<Configure>", self.on_frame_configure) # record_frame 크기 변경 시 스크롤 영역 업데이트.
        self.canvas.bind('<Enter>', self._bound_to_mousewheel)         # 마우스 오버 시 휠 이벤트 바인딩.
        self.canvas.bind('<Leave>', self._unbound_to_mousewheel)       # 마우스 이탈 시 휠 이벤트 언바인딩.

        self._build_records_display() # 기록 화면 빌드.

        self.wait_window(self) # 다이얼로그가 닫힐 때까지 대기.

    def on_frame_configure(self, event):
        # Canvas의 스크롤 영역을 record_frame의 크기에 맞춰 조정.
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bound_to_mousewheel(self, event):
        # Canvas에서 마우스 휠 이벤트를 처리하도록 바인딩.
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        # Canvas에서 마우스 휠 이벤트 바인딩 해제.
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        # 마우스 휠 움직임에 따라 Canvas 스크롤.
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _build_records_display(self):
        # 과거 펫 기록들을 불러와 화면에 표시.
        for widget in self.record_frame.winfo_children(): # 기존 위젯 모두 제거.
            widget.destroy()

        historical_pets = self.app_logic.historical_pets # 앱 로직에서 최신 기록 리스트 가져오기.
        if not historical_pets: # 기록이 없을 경우.
            tk.Label(self.record_frame, text="아직 저장된 펫 기록이 없습니다.", font=(config.MAIN_FONT_FAMILY, 12), fg="gray", bg=config.BG_COLOR).pack(pady=20)
        else: # 기록이 있을 경우, 최신 기록부터 역순으로 표시.
            for i in range(len(historical_pets) -1, -1, -1):
                record = historical_pets[i]
                self._create_record_entry(record, i) # 각 기록 엔트리 생성.
        
        self.on_frame_configure(None) # 스크롤 영역 갱신.

    def _create_record_entry(self, record, index): 
        # 단일 과거 펫 기록 엔트리 위젯 생성.
        entry_frame = tk.Frame(self.record_frame, bd=2, relief=tk.GROOVE, padx=10, pady=10, bg="white")
        entry_frame.pack(fill=tk.X, padx=5, pady=5)

        image_size = (60, 60) 
        image_filename = f"{record['species']}_level{record['level']}.png"
        pet_img = self.pet_image_loader_func(image_filename, size=image_size) # 펫 이미지 로드.

        img_label = tk.Label(entry_frame, image=pet_img, bg="white") # 이미지 라벨.
        img_label.image = pet_img # 참조 유지.
        img_label.pack(side=tk.LEFT, padx=10)

        info_text = ( # 기록 정보 텍스트 생성.
            f"기간: {record['start_date'].strftime('%Y/%m/%d')} ~ {record['end_date'].strftime('%Y/%m/%d')}\n"
            f"펫 종류: {record['species']}\n"
            f"최종 레벨: Lv. {record['level']}"
        )
        info_label = tk.Label(entry_frame, text=info_text, justify=tk.LEFT, font=(config.MAIN_FONT_FAMILY, 10), bg="white")
        info_label.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

        # 기록 삭제 버튼.
        delete_button = tk.Button(entry_frame, text="삭제", 
                                  command=lambda idx=index: self._delete_record(idx), 
                                  font=(config.MAIN_FONT_FAMILY, 9), bg="red", fg="white")
        delete_button.pack(side=tk.RIGHT, padx=5, pady=5) 

    def _delete_record(self, index):
        # 기록 삭제 버튼 클릭 시 호출.
        if messagebox.askyesno("기록 삭제", "정말 이 펫의 기록을 삭제하시겠습니까?", parent=self): # 사용자 확인.
            if self.app_logic.delete_historical_pet_record(index): # app_logic을 통해 기록 삭제.
                self._build_records_display() # 화면 갱신.
            else:
                messagebox.showerror("오류", "기록 삭제에 실패했습니다.", parent=self)


# === 주 애플리케이션 GUI 클래스 ===
# Pet-Do-List 앱의 메인 GUI를 생성하고 관리하는 클래스입니다.
class PetDoListGUI:
    def __init__(self, master, app_logic):
        self.master = master     # Tkinter 루트(메인) 창.
        self.app_logic = app_logic # 메인 앱 로직(main.py) 인스턴스.
        
        self.pet_image_cache = {} # 펫 이미지 캐시 (성능 최적화).
        
        self._create_widgets() # 모든 GUI 위젯 생성.
        self._setup_layout()   # 생성된 위젯들을 화면에 배치.
        

    def _create_widgets(self):
        """애플리케이션에 필요한 모든 GUI 위젯들을 생성합니다."""
        
        # --- 1. 좌측 패널 (펫 정보 및 이미지) ---
        self.left_panel = tk.Frame(self.master, bg=config.PRIMARY_COLOR, bd=5, relief=tk.RIDGE)
        
        # 펫 이름 라벨.
        self.pet_name_label = tk.Label(self.left_panel, text="이름: {펫 이름}", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR)
        # 펫 이미지 표시 영역.
        self.pet_canvas = tk.Canvas(self.left_panel, width=300, height=300, bg=config.PRIMARY_COLOR, highlightthickness=0)
        self.pet_photo_label = tk.Label(self.pet_canvas, bg=config.PRIMARY_COLOR) # 펫 이미지를 담을 라벨 (Canvas 안에 배치).
        # 펫 종류/레벨 라벨.
        self.pet_species_level_label = tk.Label(self.left_panel, text="종류: {펫 종류} / Lv. {펫 레벨}", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_MEDIUM), bg=config.PRIMARY_COLOR, fg="white")
        # 경험치 라벨.
        self.exp_label = tk.Label(self.left_panel, text="EXP: --/--", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR)
        
        # 행복도 게이지.
        self.happiness_label = tk.Label(self.left_panel, text="행복도", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR, bd=0, highlightthickness=0)
        self.happiness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate") 

        # 포만감 게이지.
        self.fullness_label = tk.Label(self.left_panel, text="포만감", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.PRIMARY_COLOR, fg=config.SECONDARY_TEXT_COLOR, bd=0, highlightthickness=0)
        self.fullness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate") 
        
        self.spacer_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR) # 레이아웃을 위한 스페이서 프레임.
        # 간식 주기 버튼들을 담을 프레임.
        self.snack_buttons_row_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR, bd=0, highlightthickness=0)
        self.snack_button = tk.Button(self.snack_buttons_row_frame, text="간식 주기 (기본)", command=lambda: self.app_logic.give_snack_to_pet("기본 간식"), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white")
        self.snack_premium_button = tk.Button(self.snack_buttons_row_frame, text="간식 주기 (고급)", command=lambda: self.app_logic.give_snack_to_pet("고급 간식"), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white") 
        
        # 펫 기록/환생 버튼들을 담을 프레임.
        self.action_buttons_row_frame = tk.Frame(self.left_panel, bg=config.PRIMARY_COLOR, bd=0, highlightthickness=0) 
        self.view_history_button = tk.Button(self.action_buttons_row_frame, text="펫 기록 보기", command=self.show_pet_history, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.ACCENT_COLOR, fg="white")
        self.rebirth_button = tk.Button(self.action_buttons_row_frame, text="강제 환생 (초기화)", command=self.app_logic.perform_rebirth_via_dialog, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg="lightgray")


        # --- 2. 우측 패널 (투두리스트 및 간식 인벤토리) ---
        self.right_panel = tk.Frame(self.master, bg=config.BG_COLOR, bd=5, relief=tk.RIDGE)
        
        # 날짜 이동 버튼 및 현재 날짜 표시 프레임.
        self.date_nav_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        self.current_date_label = tk.Label(self.date_nav_frame, text="----년 --월 --일", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_MEDIUM, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR)
        self.prev_day_button = tk.Button(self.date_nav_frame, text="◀ 이전 날짜", command=lambda: self.app_logic.change_date_logic(-1), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg=config.PRIMARY_COLOR, fg="white")
        self.next_day_button = tk.Button(self.date_nav_frame, text="다음 날짜 ▶", command=lambda: self.app_logic.change_date_logic(1), font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE), bg=config.PRIMARY_COLOR, fg="white")
        
        # "오늘 할 일" 라벨.
        self.todo_label = tk.Label(self.right_panel, text="오늘 할 일", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR)
        # 할 일 목록을 표시할 리스트박스.
        self.todo_listbox = tk.Listbox(self.right_panel, height=10, font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), selectmode=tk.SINGLE, bd=2, relief=tk.GROOVE)
        self.todo_scrollbar = tk.Scrollbar(self.right_panel, orient="vertical", command=self.todo_listbox.yview) # 리스트박스 스크롤바.
        self.todo_listbox.config(yscrollcommand=self.todo_scrollbar.set)
        
        # 새 할 일 입력 엔트리.
        self.todo_entry = tk.Entry(self.right_panel, font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bd=2, relief=tk.GROOVE)
        # 할 일 추가/완료/삭제 버튼.
        self.add_todo_button = tk.Button(self.right_panel, text="할 일 추가", command=self.add_todo_from_entry, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.complete_todo_button = tk.Button(self.right_panel, text="할 일 완료", command=self.complete_selected_todo, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        self.remove_todo_button = tk.Button(self.right_panel, text="할 일 삭제", command=self.remove_selected_todo, font=(config.MAIN_FONT_FAMILY, config.BUTTON_FONT_SIZE, "bold"), bg="red", fg="white")

        # 간식 인벤토리 라벨.
        self.snack_inventory_label = tk.Label(self.right_panel, text="간식 인벤토리", font=(config.MAIN_FONT_FAMILY, config.HEADING_FONT_SIZE_LARGE, "bold"), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR)
        self.snack_list_label = tk.Label(self.right_panel, text="기본 간식: {X}개, 고급 간식: {Y}개", font=(config.MAIN_FONT_FAMILY, config.BODY_FONT_SIZE), bg=config.BG_COLOR, fg=config.SECONDARY_TEXT_COLOR)


    def _setup_layout(self):
        """생성된 위젯들을 화면에 배치(pack/grid)합니다."""
        
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10, expand=True) # 좌측 패널 배치.
        self.pet_name_label.pack(pady=10)
        self.pet_canvas.pack(pady=5)
        self.pet_photo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # 펫 이미지 라벨을 Canvas 중앙에 배치.
        self.pet_species_level_label.pack(pady=5)
        self.exp_label.pack(pady=5)
        
        self.happiness_label.pack(pady=(0,0)) 
        self.happiness_bar.pack(pady=(0,0))   
        
        self.fullness_label.pack(pady=(0,0)) 
        self.fullness_bar.pack(pady=(0,0))   
        
        self.spacer_frame.pack(side=tk.TOP, expand=True, fill=tk.Y)
        # 간식 버튼 프레임 배치 및 버튼들 grid 배치 (중앙 정렬).
        self.snack_buttons_row_frame.pack(side=tk.TOP, pady=(5, 5), fill=tk.X, expand=False)
        self.snack_buttons_row_frame.grid_columnconfigure(0, weight=1) # 좌측 여백 컬럼.
        self.snack_buttons_row_frame.grid_columnconfigure(1, weight=0) # 버튼 컬럼.
        self.snack_buttons_row_frame.grid_columnconfigure(2, weight=0) # 버튼 컬럼.
        self.snack_buttons_row_frame.grid_columnconfigure(3, weight=1) # 우측 여백 컬럼.
        self.snack_button.grid(row=0, column=1, padx=5, ipadx=10, ipady=5)
        self.snack_premium_button.grid(row=0, column=2, padx=5, ipadx=10, ipady=5)
        
        # 액션 버튼 프레임 배치 및 버튼들 grid 배치 (중앙 정렬).
        self.action_buttons_row_frame.pack(side=tk.TOP, pady=(5, 50), fill=tk.X, expand=False) 
        self.action_buttons_row_frame.grid_columnconfigure(0, weight=1)
        self.action_buttons_row_frame.grid_columnconfigure(1, weight=0)
        self.action_buttons_row_frame.grid_columnconfigure(2, weight=0)
        self.action_buttons_row_frame.grid_columnconfigure(3, weight=1)
        self.view_history_button.grid(row=0, column=1, padx=5, ipadx=10, ipady=5) 
        self.rebirth_button.grid(row=0, column=2, padx=5, ipadx=10, ipady=5) 

        # --- 우측 패널 (할 일 목록 및 간식 인벤토리) ---
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True) # 우측 패널 배치.
        self.date_nav_frame.pack(fill=tk.X, pady=10) # 날짜 네비게이션 프레임 배치.
        self.prev_day_button.pack(side=tk.LEFT, padx=5)   # 이전 날짜 버튼.
        self.current_date_label.pack(side=tk.LEFT, expand=True) # 현재 날짜 라벨.
        self.next_day_button.pack(side=tk.RIGHT, padx=5)   # 다음 날짜 버튼.

        self.todo_label.pack(pady=10)                     # 할 일 라벨.
        self.todo_scrollbar.pack(side=tk.RIGHT, fill=tk.Y) # 할 일 리스트 스크롤바.
        self.todo_listbox.pack(fill=tk.BOTH, expand=True, pady=5) # 할 일 리스트박스.
        
        self.todo_entry.pack(fill=tk.X, pady=5)           # 할 일 입력 엔트리.
        
        # 할 일 관련 버튼들을 담을 프레임 및 배치.
        todo_button_frame = tk.Frame(self.right_panel, bg=config.BG_COLOR)
        todo_button_frame.pack(fill=tk.X, pady=5)
        self.add_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.complete_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.remove_todo_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.snack_inventory_label.pack(pady=(20, 10)) # 간식 인벤토리 라벨.
        self.snack_list_label.pack(pady=5)             # 간식 목록 라벨.

    def load_pet_image(self, image_filename, size=(300, 300)):
        """
        펫 이미지를 로드하고 캐싱하여 반환합니다. 이미 로드된 이미지는 캐시에서 가져옵니다.
        Args:
            image_filename (str): 이미지 파일명.
            size (tuple): 이미지 리사이즈 크기 (너비, 높이).
        Returns:
            ImageTk.PhotoImage: 로드된/캐시된 이미지 객체.
        """
        image_path_key = f"{image_filename}_{size[0]}x{size[1]}" # 캐시 키 생성 (파일명 + 크기).
        
        if image_path_key not in self.pet_image_cache: # 캐시에 없는 이미지일 경우.
            full_path = ""
            try:
                # 이미지 파일의 전체 경로 생성 및 이미지 로드, 리사이즈.
                full_path = os.path.join(config.RESOURCES_PATH, config.PET_IMAGES_SUBFOLDER, image_filename)
                print(f"DEBUG: 이미지 로드 시도 경로: {full_path}") # 디버그 출력.
                original_image = Image.open(full_path)
                resized_image = original_image.resize(size, Image.Resampling.LANCZOS) # 고품질 리사이징.
                self.pet_image_cache[image_path_key] = ImageTk.PhotoImage(resized_image) # 캐시에 저장.
            except FileNotFoundError: # 이미지 파일을 찾을 수 없을 경우.
                print(f"이미지 파일 '{full_path}'을 찾을 수 없습니다.")
                if 'error_image' not in self.pet_image_cache: # 에러 이미지도 캐시.
                    error_image_path = os.path.join(config.RESOURCES_PATH, "no_image.png") # 기본 에러 이미지 경로.
                    try: # 에러 이미지 로드 시도.
                        error_img_orig = Image.open(error_image_path)
                        error_img_resized = error_img_orig.resize(size, Image.Resampling.LANCZOS)
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(error_img_resized)
                    except FileNotFoundError: # 에러 이미지조차 없는 경우 투명한 빈 이미지 생성.
                        print(f"기본 에러 이미지 파일 '{error_image_path}'도 찾을 수 없습니다. 빈 이미지로 처리합니다.")
                        empty_img = Image.new('RGBA', size, (0, 0, 0, 0)) # 투명한 이미지.
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(empty_img)
                    except Exception as e: # 에러 이미지 로드 중 다른 예외 발생.
                        print(f"에러 이미지 로드 중 오류 발생: {e}. 빈 이미지로 처리합니다.")
                        empty_img = Image.new('RGBA', size, (0, 0, 0, 0))
                        self.pet_image_cache['error_image'] = ImageTk.PhotoImage(empty_img)
                return self.pet_image_cache['error_image'] # 에러 이미지 반환.
            except Exception as e: # 이미지 로드 중 기타 예외 발생.
                print(f"이미지 로드 중 오류 발생 ({full_path}): {e}")
                return None # 이미지 로드 실패 시 None 반환.
        return self.pet_image_cache[image_path_key] # 캐시된 이미지 반환.

    def update_gui_with_pet_data(self):
        """main.py의 펫 데이터를 기반으로 GUI를 업데이트합니다."""

        pet = self.app_logic.pet # 현재 펫 객체 가져오기.
        if pet: # 펫 데이터가 존재할 경우.
            self.pet_name_label.config(text=f"이름: {pet.name}")
            self.pet_species_level_label.config(text=f"종류: {pet.species} / Lv. {pet.level}")
            
            # 펫 경험치 표시 업데이트.
            if pet.level >= config.MAX_PET_LEVEL: # 최대 레벨일 경우.
                exp_display_text = "EXP: MAX" 
            else: # 최대 레벨이 아닐 경우.
                required_exp = pet.get_required_exp_for_level_up()
                exp_display_text = f"EXP: {pet.exp}/{required_exp}"
            
            self.exp_label.config(text=exp_display_text) 

            # 펫 이미지 업데이트.
            image_filename = f"{pet.species}_level{pet.level}.png" 
            pet_image = self.load_pet_image(image_filename) 

            if pet_image:
                self.pet_photo_label.config(image=pet_image)
                self.pet_photo_label.image = pet_image # GC 방지용 참조.
            else:
                self.pet_photo_label.config(image='') # 이미지 없을 경우 공백.

            # 행복도, 포만감 게이지 업데이트.
            self.happiness_bar['value'] = pet.happiness
            self.happiness_bar['maximum'] = pet.max_happiness
            self.fullness_bar['value'] = pet.fullness
            self.fullness_bar['maximum'] = pet.max_fullness
        else: # 펫 데이터가 없을 경우 (초기 상태).
            self.pet_name_label.config(text="이름: ---")
            self.pet_species_level_label.config(text="종류: --- / Lv. --")
            self.exp_label.config(text="EXP: --/--") 
            self.pet_photo_label.config(image='') 
            self.happiness_bar['value'] = 0
            self.fullness_bar['value'] = 0

        # 현재 표시 날짜 업데이트.
        current_display_date = self.app_logic.todo_manager.get_current_date()
        self.current_date_label.config(text=current_display_date.strftime("%Y년 %m월 %d일"))
        
        # 할 일 목록 업데이트.
        self.todo_listbox.delete(0, tk.END) # 기존 목록 모두 삭제.
        todos = self.app_logic.todo_manager.get_current_date_todos() # 현재 날짜 할 일 가져오기.
        for i, todo in enumerate(todos): # 각 할 일 목록에 추가.
            display_text = f"[{'✅' if todo['completed'] else '☐'}] {todo['text']}" # 완료 여부에 따른 체크 표시.
            self.todo_listbox.insert(tk.END, display_text)
            if todo['completed']: # 완료된 할 일은 회색으로 표시.
                self.todo_listbox.itemconfig(tk.END, {'fg': 'gray'}) 

        # 간식 인벤토리 업데이트.
        snack_counts = self.app_logic.todo_manager.get_current_snack_counts() # 현재 간식 개수 가져오기.
        snack_text_parts = []
        for snack_name, count in snack_counts.items():
            if count > 0: # 0개 초과 간식만 표시.
                snack_text_parts.append(f"{snack_name}: {count}개")
        
        snack_text = ", ".join(snack_text_parts) # 간식 목록 문자열 생성.
        if not snack_text: # 간식이 하나도 없을 경우.
            snack_text = "보유 간식이 없습니다."
        self.snack_list_label.config(text=snack_text) # 간식 라벨 업데이트.
        
    def add_todo_from_entry(self):
        """엔트리에 입력된 할 일을 추가합니다."""
        todo_text = self.todo_entry.get() # 엔트리에서 텍스트 가져오기.
        if self.app_logic.add_todo_logic(todo_text): # app_logic을 통해 할 일 추가.
            self.todo_entry.delete(0, tk.END) # 성공 시 엔트리 초기화.
        else:
            messagebox.showerror("입력 오류", "할 일 내용을 입력해주세요.", parent=self.master)

    def complete_selected_todo(self):
        """선택된 할 일을 완료 처리합니다."""
        selected_indices = self.todo_listbox.curselection() # 리스트박스에서 선택된 인덱스.
        if selected_indices:
            index = selected_indices[0]
            self.app_logic.complete_todo_logic(index) # app_logic을 통해 할 일 완료 처리.
        else:
            messagebox.showinfo("선택 오류", "완료할 할 일을 선택해주세요.", parent=self.master)

    def remove_selected_todo(self):
        """선택된 할 일을 삭제 처리합니다."""
        selected_indices = self.todo_listbox.curselection() # 리스트박스에서 선택된 인덱스.
        if selected_indices:
            index = selected_indices[0]
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master): # 사용자 확인.
                self.app_logic.remove_todo_logic(index) # app_logic을 통해 할 일 삭제 처리.
        else:
            messagebox.showinfo("선택 오류", "삭제할 할 일을 선택해주세요.", parent=self.master)

    def show_pet_species_selection(self, species_list, dialog_title="펫 종류 선택"):
        """펫 종류 선택 다이얼로그를 표시하고 결과를 반환합니다."""
        dialog = PetSpeciesSelectionDialog(self.master, species_list, dialog_title)
        return dialog.result # 다이얼로그의 결과 (선택된 펫 종류) 반환.

    def show_pet_history(self):
        """펫 기록 보기 다이얼로그를 표시합니다."""
        # HistoricalPetViewerDialog를 생성하여 펫 기록을 보여줍니다.
        history_dialog = HistoricalPetViewerDialog(
            self.master, 
            self.app_logic.historical_pets, 
            self.load_pet_image,
            self.app_logic # 기록 삭제 등을 위해 app_logic 인스턴스 전달.
        )