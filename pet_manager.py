# 펫 관련 로직 (펫 상태 관리, 성장, 환생 로직)


import datetime
import random # 펫 종류 랜덤 선택을 위해 추가
from config import ( # config.py에서 필요한 상수들을 가져옵니다.
    INITIAL_PET_NAME, PET_SPECIES_LIST, MAX_PET_LEVEL,
    INITIAL_PET_LEVEL, INITIAL_PET_EXP, # 새로 추가한 상수들도 포함
    EXP_PER_TODO_COMPLETE, EXP_REQUIRED_FOR_LEVEL_UP,
    
    INITIAL_PET_HAPPINESS, MAX_PET_HAPPINESS,
    INITIAL_PET_FULLNESS, MAX_PET_FULLNESS,
    PET_RESET_INTERVAL_DAYS, WEEKLY_RESET_DAY, RESET_TIME_HOUR # 주간 리셋 상수도 임포트 확인
)

class Pet:
    def __init__(self, name=INITIAL_PET_NAME, species=None, level=INITIAL_PET_LEVEL, exp=INITIAL_PET_EXP, 
                 happiness=INITIAL_PET_HAPPINESS, fullness=INITIAL_PET_FULLNESS, last_reset_date=None):
        
        self.name = name # 사용자로부터 받은 이름을 사용
        self.species = species if species else random.choice(PET_SPECIES_LIST) # 종이 지정되지 않으면 랜덤 선택
        self.level = level
        self.exp = exp
        self.happiness = happiness
        self.fullness = fullness
        
        self.image_path = self._get_image_path(self.species, self.level) 
        
        self.max_happiness = MAX_PET_HAPPINESS # config 값 사용
        self.max_fullness = MAX_PET_FULLNESS   # config 값 사용
        
        self.last_reset_date = last_reset_date if last_reset_date else datetime.date.today()

    def _get_image_path(self, species, level):
        # 펫 종류와 레벨에 따라 이미지 경로를 반환하는 로직 (아직 리소스 폴더는 비어있으니, 임시 경로)
        # 실제 이미지 파일은 resources/pet_images/ 폴더에 존재해야 합니다.
        return f"resources/pet_images/{species}_level{level}.png" # 예: resources/pet_images/알_level1.png

    def get_required_exp_for_level_up(self):
        """현재 레벨에서 다음 레벨로 가기 위해 필요한 경험치를 반환"""
        return EXP_REQUIRED_FOR_LEVEL_UP.get(self.level, EXP_PER_TODO_COMPLETE)

    def give_snack(self, snack_effect):
        self.happiness = min(self.max_happiness, self.happiness + snack_effect['happiness'])
        self.fullness = min(self.max_fullness, self.fullness + snack_effect['fullness'])
        print(f"{self.name}이가 간식을 먹고 행복해했어요! 행복도: {self.happiness}, 포만감: {self.fullness}")

    def add_exp(self, amount=EXP_PER_TODO_COMPLETE): # 기본값으로 config의 경험치 사용
        self.exp += amount
        print(f"{self.name}이가 경험치를 {amount} 얻었어요! 현재 경험치: {self.exp}/{self.get_required_exp_for_level_up()}")
        if self.exp >= self.get_required_exp_for_level_up():
            self.level_up()

    def level_up(self):
        self.level += 1
        self.exp -= self.get_required_exp_for_level_up() # 남은 경험치는 다음 레벨로 이월
        if self.exp < 0: # 혹시 경험치 음수가 될까봐 방지
            self.exp = 0 
        
        self.image_path = self._get_image_path(self.species, self.level) # 레벨업 시 이미지 변경
        print(f"{self.name}이가 레벨업! 현재 레벨: {self.level}")

    def reset_for_rebirth(self, new_species=None):
        """펫을 환생시키면서 새로운 종이나 초기 상태로 리셋"""
        # 이름은 사용자가 새로 지을 수도 있으니, 기본 이름은 사용하지 않고 나중에 GUI에서 받음
        self.species = new_species if new_species else random.choice(PET_SPECIES_LIST) # 새로운 종 랜덤 선택
        self.level = INITIAL_PET_LEVEL
        self.exp = INITIAL_PET_EXP
        self.happiness = INITIAL_PET_HAPPINESS
        self.fullness = INITIAL_PET_FULLNESS
        self.last_reset_date = datetime.date.today()
        self.image_path = self._get_image_path(self.species, self.level)
        print(f"{self.name}이가 새로운 모습으로 태어났어요!")
