# pet_manager.py

import datetime
import random 
from config import ( 
    INITIAL_PET_NAME, PET_SPECIES_LIST, MAX_PET_LEVEL,
    INITIAL_PET_LEVEL, INITIAL_PET_EXP, 
    EXP_PER_TODO_COMPLETE, EXP_REQUIRED_FOR_LEVEL_UP,
    
    INITIAL_PET_HAPPINESS, MAX_PET_HAPPINESS,
    INITIAL_PET_FULLNESS, MAX_PET_FULLNESS,
    PET_RESET_INTERVAL_DAYS, WEEKLY_RESET_DAY, RESET_TIME_HOUR
)

class Pet:
    def __init__(self, name=INITIAL_PET_NAME, species=None, level=INITIAL_PET_LEVEL, exp=INITIAL_PET_EXP, 
                 happiness=INITIAL_PET_HAPPINESS, fullness=INITIAL_PET_FULLNESS, last_reset_date=None):
        
        self.name = name 
        self.species = species if species else random.choice(PET_SPECIES_LIST) 
        self.level = level
        self.exp = exp
        self.happiness = happiness
        self.fullness = fullness
        
        self.image_path = self._get_image_path(self.species, self.level) 
        
        self.max_happiness = MAX_PET_HAPPINESS 
        self.max_fullness = MAX_PET_FULLNESS   
        
        self.last_reset_date = last_reset_date if last_reset_date else datetime.date.today()

        # ⭐ 게이지 만점 보상 여부 추적용 속성 추가 ⭐
        self.has_been_rewarded_for_full_gauges = False

    def _get_image_path(self, species, level):
        return f"resources/pet_images/{species}_level{level}.png" 

    def get_required_exp_for_level_up(self):
        return EXP_REQUIRED_FOR_LEVEL_UP.get(self.level + 1, 999999) 


    def give_snack(self, snack_effect):
        self.happiness = min(self.max_happiness, self.happiness + snack_effect.get('happiness', 0)) 
        self.fullness = min(self.max_fullness, self.fullness + snack_effect.get('fullness', 0))   
        print(f"{self.name}이가 간식을 먹고 행복해했어요! 행복도: {self.happiness}, 포만감: {self.fullness}")
        # ⭐ 간식으로 펫 상태가 변경되었으므로 보상 상태 리셋 ⭐
        self.has_been_rewarded_for_full_gauges = False

    def add_exp(self, amount=EXP_PER_TODO_COMPLETE): 
        self.exp += amount
        print(f"{self.name}이가 경험치를 {amount} 얻었어요! 현재 경험치: {self.exp}/{self.get_required_exp_for_level_up()}")

        leveled_up = False
        while self.level < MAX_PET_LEVEL and self.exp >= self.get_required_exp_for_level_up():
            self.level += 1
            self.exp -= self.get_required_exp_for_level_up() 
            if self.exp < 0: 
                self.exp = 0 
            leveled_up = True
            self.image_path = self._get_image_path(self.species, self.level) 
            print(f"{self.name}이가 레벨업! 현재 레벨: {self.level}")
            
        return leveled_up 

    def reset_for_rebirth(self, new_species=None, new_name=None):
        self.name = new_name if new_name else self.name 
        self.species = new_species if new_species else random.choice(PET_SPECIES_LIST) 
        self.level = INITIAL_PET_LEVEL
        self.exp = INITIAL_PET_EXP
        self.happiness = INITIAL_PET_HAPPINESS
        self.fullness = INITIAL_PET_FULLNESS
        self.last_reset_date = datetime.date.today()
        self.image_path = self._get_image_path(self.species, self.level)
        # ⭐ 환생 시 보상 상태 플래그 초기화 ⭐
        self.has_been_rewarded_for_full_gauges = False
        print(f"{self.name}이가 새로운 모습으로 태어났어요!")