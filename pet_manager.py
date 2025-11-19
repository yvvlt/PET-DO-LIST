# pet_manager.py

# 펫의 데이터(이름, 종, 레벨, 경험치, 행복도, 포만감 등)를 관리하고,
# 성장, 간식 섭취, 환생 등의 로직을 처리하는 모듈입니다.

import datetime # 날짜 객체 처리에 사용 (last_reset_date).
import random   # 펫 종류 선택 시 사용 (초기 종 선택).

# config.py에서 펫 관련 상수들을 임포트합니다.
from config import ( 
    INITIAL_PET_NAME, PET_SPECIES_LIST, MAX_PET_LEVEL,
    INITIAL_PET_LEVEL, INITIAL_PET_EXP, 
    EXP_PER_TODO_COMPLETE, EXP_REQUIRED_FOR_LEVEL_UP,
    
    INITIAL_PET_HAPPINESS, MAX_PET_HAPPINESS,
    INITIAL_PET_FULLNESS, MAX_PET_FULLNESS,
    PET_RESET_INTERVAL_DAYS, WEEKLY_RESET_DAY, RESET_TIME_HOUR
)

class Pet:
    """
    디지털 펫의 상태와 행동을 관리하는 클래스입니다.
    """
    def __init__(self, name=INITIAL_PET_NAME, species=None, level=INITIAL_PET_LEVEL, exp=INITIAL_PET_EXP, 
                 happiness=INITIAL_PET_HAPPINESS, fullness=INITIAL_PET_FULLNESS, last_reset_date=None):
        
        self.name = name # 펫 이름.
        # 펫 종류가 지정되지 않으면 PET_SPECIES_LIST에서 무작위 선택.
        self.species = species if species else random.choice(PET_SPECIES_LIST) 
        self.level = level     # 현재 레벨.
        self.exp = exp         # 현재 경험치.
        self.happiness = happiness # 현재 행복도.
        self.fullness = fullness   # 현재 포만감.
        
        self.image_path = self._get_image_path(self.species, self.level) # 펫 이미지 경로.
        
        self.max_happiness = MAX_PET_HAPPINESS # 최대 행복도.
        self.max_fullness = MAX_PET_FULLNESS   # 최대 포만감.
        
        # 마지막 리셋 날짜, 지정되지 않으면 오늘 날짜로 초기화.
        self.last_reset_date = last_reset_date if last_reset_date else datetime.date.today()

        # 게이지 만점 보상 지급 여부 추적 플래그. (False: 아직 보상 안 받음, True: 보상 받음)
        self.has_been_rewarded_for_full_gauges = False

    def _get_image_path(self, species, level):
        """펫 종류와 레벨에 따른 이미지 파일 경로 반환."""
        return f"resources/pet_images/{species}_level{level}.png" 

    def get_required_exp_for_level_up(self):
        """다음 레벨업에 필요한 경험치량 반환. 최대 레벨 시 매우 큰 값 반환."""
        return EXP_REQUIRED_FOR_LEVEL_UP.get(self.level + 1, 999999) 


    def give_snack(self, snack_effect):
        """
        펫에게 간식 효과를 적용하여 행복도와 포만감을 증가시킵니다.
        Args:
            snack_effect (dict): 간식 효과를 담은 딕셔너리 (예: {'happiness': 20, 'fullness': 20}).
        """
        # 행복도 증가 (최대 행복도를 초과하지 않도록 min 사용).
        self.happiness = min(self.max_happiness, self.happiness + snack_effect.get('happiness', 0)) 
        # 포만감 증가 (최대 포만도를 초과하지 않도록 min 사용).
        self.fullness = min(self.max_fullness, self.fullness + snack_effect.get('fullness', 0))   
        print(f"{self.name}이가 간식을 먹고 행복해했어요! 행복도: {self.happiness}, 포만감: {self.fullness}")
        self.has_been_rewarded_for_full_gauges = False # 간식으로 상태 변경 시 만점 보상 상태 플래그 리셋.

    def add_exp(self, amount=EXP_PER_TODO_COMPLETE): 
        """
        펫에게 경험치를 추가하고, 레벨업 여부를 확인하여 처리합니다.
        Args:
            amount (int): 추가할 경험치 양.
        Returns:
            bool: 레벨업 성공 여부.
        """
        self.exp += amount # 경험치 증가.
        print(f"{self.name}이가 경험치를 {amount} 얻었어요! 현재 경험치: {self.exp}/{self.get_required_exp_for_level_up()}")

        leveled_up = False
        # 최대 레벨 미만이고 현재 경험치가 다음 레벨업 필요 경험치보다 많거나 같을 때 레벨업 반복.
        while self.level < MAX_PET_LEVEL and self.exp >= self.get_required_exp_for_level_up():
            self.level += 1 # 레벨 증가.
            self.exp -= self.get_required_exp_for_level_up() # 경험치 차감 (초과분만 남김).
            if self.exp < 0: # 경험치가 음수가 될 경우 방지 (예외 처리).
                self.exp = 0 
            leveled_up = True # 레벨업이 발생했음을 표시.
            self.image_path = self._get_image_path(self.species, self.level) # 레벨업에 따른 이미지 경로 갱신.
            print(f"{self.name}이가 레벨업! 현재 레벨: {self.level}")
            
        return leveled_up # 레벨업 발생 여부 반환.

    def reset_for_rebirth(self, new_species=None, new_name=None):
        """
        펫을 환생시켜 초기 상태로 재설정합니다.
        Args:
            new_species (str, optional): 새 펫의 종류. 지정되지 않으면 랜덤 선택.
            new_name (str, optional): 새 펫의 이름. 지정되지 않으면 기존 이름 유지.
        """
        self.name = new_name if new_name else self.name # 이름 지정 시 새 이름 적용, 아니면 기존 이름 유지.
        self.species = new_species if new_species else random.choice(PET_SPECIES_LIST) # 종류 지정 시 새 종류 적용, 아니면 랜덤 선택.
        self.level = INITIAL_PET_LEVEL     # 레벨 초기화.
        self.exp = INITIAL_PET_EXP         # 경험치 초기화.
        self.happiness = INITIAL_PET_HAPPINESS # 행복도 초기화.
        self.fullness = INITIAL_PET_FULLNESS   # 포만감 초기화.
        self.last_reset_date = datetime.date.today() # 리셋 날짜를 오늘로 갱신.
        self.image_path = self._get_image_path(self.species, self.level) # 새 펫 종류와 레벨에 따른 이미지 경로 갱신.
        self.has_been_rewarded_for_full_gauges = False # 환생 시 만점 보상 플래그 초기화.
        print(f"{self.name}이가 새로운 모습으로 태어났어요!")