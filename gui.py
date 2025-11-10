# Tkinter GUI 관련 코드 (위젯 생성, 레이아웃 관리)

# gui.py

import tkinter as tk
from tkinter import ttk # ttk는 더 세련된 위젯을 제공합니다.
from PIL import Image, ImageTk # 이미지 처리를 위해 Pillow 라이브러리 필요 (pip install Pillow)
import os # 파일 경로 처리를 위해 추가

import config # 설정 값들을 가져오기 위해 config 모듈 임포트

class PetDoListGUI:
    def __init__(self, master, app_logic):
        self.master = master
        self.app_logic = app_logic # main.py의 PetDoListApp 인스턴스를 받아서 로직과 연결
        
        # 윈도우 기본 설정 (main.py에서 이미 설정했더라도, gui 클래스에서 윈도우 컨트롤 시 필요)
        master.title(config.APP_TITLE)
        master.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        master.resizable(False, False) # 창 크기 조절 방지
        master.configure(bg=config.BG_COLOR) # 배경색 설정

        self.pet_image_cache = {} # 펫 이미지 캐싱을 위한 딕셔너리
        
        self._create_widgets() # 위젯 생성 메서드 호출
        self._setup_layout()   # 레이아웃 설정 메서드 호출
        self.update_gui_with_pet_data() # GUI 초기 데이터 업데이트

    def _create_widgets(self):
        """GUI에 필요한 위젯들을 생성합니다."""
        
        # --- 1. 좌측 패널 (펫 정보 및 이미지) ---
        self.left_panel = tk.Frame(self.master, bg=config.PRIMARY_COLOR, bd=5, relief=tk.RIDGE)
        
        # 펫 이름
        self.pet_name_label = tk.Label(self.left_panel, text="이름: {펫 이름}", font=("Arial", 20, "bold"), bg=config.PRIMARY_COLOR, fg="white")
        
        # 펫 이미지 (Canvas를 사용하여 배경과 함께 배치하기 용이)
        self.pet_canvas = tk.Canvas(self.left_panel, width=300, height=300, bg=config.PRIMARY_COLOR, highlightthickness=0)
        self.pet_photo_label = tk.Label(self.pet_canvas, bg=config.PRIMARY_COLOR) # Canvas 위에 Label로 이미지 표시
        
        # 펫 종류/레벨
        self.pet_species_level_label = tk.Label(self.left_panel, text="종류: {펫 종류} / Lv. {펫 레벨}", font=("Arial", 14), bg=config.PRIMARY_COLOR, fg="white")
        
        # 펫 상태 (행복도, 포만감 - 프로그레스바)
        self.happiness_label = tk.Label(self.left_panel, text="행복도", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.happiness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        self.fullness_label = tk.Label(self.left_panel, text="포만감", font=("Arial", 12), bg=config.PRIMARY_COLOR, fg="white")
        self.fullness_bar = ttk.Progressbar(self.left_panel, orient="horizontal", length=250, mode="determinate")
        
        # 펫 상호작용 버튼
        self.snack_button = tk.Button(self.left_panel, text="간식 주기 (기본)", command=lambda: self.app_logic.give_snack_to_pet("기본 간식"), font=("Arial", 12, "bold"), bg=config.ACCENT_COLOR, fg="white")
        self.snack_premium_button = tk.Button(self.left_panel, text="간식 주기 (고급)", command=lambda: self.app_logic.give_snack_to_pet("고급 간식"), font=("Arial", 12, "bold"), bg=config.ACCENT_COLOR, fg="white")


        # --- 2. 우측 패널 (투두리스트 및 간식 인벤토리) ---
        self.right_panel = tk.Frame(self.master, bg=config.BG_COLOR, bd=5, relief=tk.RIDGE)
        
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
        self.pet_photo_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER) # Canvas 중앙에 이미지 배치
        self.pet_species_level_label.pack(pady=5)
        
        self.happiness_label.pack(pady=(10,0))
        self.happiness_bar.pack(pady=5)
        self.fullness_label.pack(pady=(5,0))
        self.fullness_bar.pack(pady=5)
        
        self.snack_button.pack(pady=(15, 5), ipadx=20, ipady=10)
        self.snack_premium_button.pack(pady=(5, 15), ipadx=20, ipady=10)


        # 우측 패널 배치 (투두리스트, 인벤토리)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, expand=True)
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


    def load_pet_image(self, image_path, size=(300, 300)):
        """펫 이미지를 로드하고 캐싱하여 성능을 최적화합니다."""
        if image_path not in self.pet_image_cache:
            try:
                full_path = os.path.join(config.RESOURCES_PATH, image_path)
                original_image = Image.open(full_path)
                resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
                self.pet_image_cache[image_path] = ImageTk.PhotoImage(resized_image)
            except FileNotFoundError:
                print(f"이미지 파일 '{full_path}'을 찾을 수 없습니다.")
                # 기본 에러 이미지 로드 또는 빈 이미지 처리
                return None
            except Exception as e:
                print(f"이미지 로드 중 오류 발생 ({image_path}): {e}")
                return None
        return self.pet_image_cache[image_path]

    def update_gui_with_pet_data(self):
        """app_logic (main.py)의 펫 데이터를 기반으로 GUI를 업데이트합니다."""
        pet = self.app_logic.pet
        if pet:
            # 펫 이름, 종류, 레벨 업데이트
            self.pet_name_label.config(text=f"이름: {pet.name}")
            self.pet_species_level_label.config(text=f"종류: {pet.species} / Lv. {pet.level}")

            # 펫 이미지 업데이트
            pet_image = self.load_pet_image(pet.image_path)
            if pet_image:
                self.pet_photo_label.config(image=pet_image)
                self.pet_photo_label.image = pet_image # GC 방지를 위해 참조 유지

            # 행복도, 포만감 프로그레스바 업데이트
            self.happiness_bar['value'] = pet.happiness
            self.happiness_bar['maximum'] = pet.max_happiness
            self.fullness_bar['value'] = pet.fullness
            self.fullness_bar['maximum'] = pet.max_fullness
        else:
            # 펫 데이터가 없는 경우 초기 상태 또는 플레이스홀더 표시
            self.pet_name_label.config(text="이름: ---")
            self.pet_species_level_label.config(text="종류: --- / Lv. --")
            self.pet_photo_label.config(image='') # 이미지 제거
            self.happiness_bar['value'] = 0
            self.fullness_bar['value'] = 0

        # 투두리스트 업데이트
        self.todo_listbox.delete(0, tk.END) # 기존 목록 삭제
        todos = self.app_logic.todo_manager.get_current_todos()
        for i, todo in enumerate(todos):
            display_text = f"[{'✅' if todo['completed'] else '☐'}] {todo['text']}"
            self.todo_listbox.insert(tk.END, display_text)
            if todo['completed']:
                self.todo_listbox.itemconfig(i, {'fg': 'gray'}) # 완료된 항목은 회색으로

        # 간식 인벤토리 업데이트
        snack_counts = self.app_logic.todo_manager.get_current_snack_counts()
        snack_text = ", ".join([f"{name}: {count}개" for name, count in snack_counts.items()])
        if not snack_text:
            snack_text = "보유 간식이 없습니다."
        self.snack_list_label.config(text=snack_text)
        
    # --- GUI 이벤트 핸들러 (main.py의 app_logic과 연결) ---
    def add_todo_from_entry(self):
        todo_text = self.todo_entry.get()
        if self.app_logic.todo_manager.add_todo(todo_text):
            self.todo_entry.delete(0, tk.END) # Entry 초기화
            self.update_gui_with_pet_data() # GUI 업데이트
        else:
            messagebox.showerror("입력 오류", "할 일 내용을 입력해주세요.", parent=self.master)

    def complete_selected_todo(self):
        selected_indices = self.todo_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if self.app_logic.todo_manager.get_current_todos()[index]['completed']:
                messagebox.showinfo("알림", "이미 완료된 할 일입니다.", parent=self.master)
                return

            snack_reward = self.app_logic.todo_manager.complete_todo(index)
            if snack_reward > 0:
                self.app_logic.pet.add_exp(amount=config.EXP_PER_TODO_COMPLETE)
                self.update_gui_with_pet_data() # GUI 업데이트
            else:
                messagebox.showerror("오류", "할 일 완료 처리에 실패했습니다.", parent=self.master)
        else:
            messagebox.showinfo("선택 오류", "완료할 할 일을 선택해주세요.", parent=self.master)

    def remove_selected_todo(self):
        selected_indices = self.todo_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            if messagebox.askyesno("삭제 확인", "선택된 할 일을 삭제하시겠습니까?", parent=self.master):
                self.app_logic.todo_manager.remove_todo(index)
                self.update_gui_with_pet_data() # GUI 업데이트
        else:
            messagebox.showinfo("선택 오류", "삭제할 할 일을 선택해주세요.", parent=self.master)


# 이 부분은 main.py에서 호출할 것이므로, gui.py 자체를 실행해도 아무것도 안 뜨게 합니다.
# if __name__ == "__main__":
#     root = tk.Tk()
#     # PetDoListApp의 임시 Mock 객체를 생성하거나, 최소한의 PetDoListApp을 구현해야 테스트 가능
#     # app_logic_mock = type('PetDoListAppMock', (), {'pet': None, 'todo_manager': TodoManager()})()
#     # gui = PetDoListGUI(root, app_logic_mock)
#     root.mainloop()
