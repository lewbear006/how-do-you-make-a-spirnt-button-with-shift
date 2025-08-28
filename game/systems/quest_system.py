"""
Quest System for Rent Quest
Manages quests, objectives, and story progression
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from game.entities.player import Player

class QuestStatus(Enum):
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class QuestObjective:
    """A single quest objective"""
    
    def __init__(self, description: str, objective_type: str, target_value: int = 1):
        """Initialize quest objective"""
        self.description = description
        self.objective_type = objective_type  # kill_monsters, earn_money, survive_days, etc.
        self.target_value = target_value
        self.current_value = 0
        self.completed = False
        
    def update_progress(self, amount: int = 1):
        """Update objective progress"""
        self.current_value = min(self.target_value, self.current_value + amount)
        self.completed = self.current_value >= self.target_value
        
    def get_progress_text(self) -> str:
        """Get progress as text"""
        return f"{self.description} ({self.current_value}/{self.target_value})"

class Quest:
    """A single quest with objectives and rewards"""
    
    def __init__(self, quest_id: str, title: str, description: str, 
                 money_reward: int = 0, xp_reward: int = 0):
        """Initialize quest"""
        self.quest_id = quest_id
        self.title = title
        self.description = description
        self.money_reward = money_reward
        self.xp_reward = xp_reward
        self.status = QuestStatus.NOT_STARTED
        self.objectives: List[QuestObjective] = []
        
    def add_objective(self, objective: QuestObjective):
        """Add an objective to the quest"""
        self.objectives.append(objective)
        
    def update_objective(self, objective_type: str, amount: int = 1):
        """Update specific objective type"""
        for objective in self.objectives:
            if objective.objective_type == objective_type and not objective.completed:
                objective.update_progress(amount)
                
    def check_completion(self) -> bool:
        """Check if quest is completed"""
        if self.status == QuestStatus.ACTIVE:
            all_completed = all(obj.completed for obj in self.objectives)
            if all_completed:
                self.status = QuestStatus.COMPLETED
                return True
        return False
        
    def start(self):
        """Start the quest"""
        if self.status == QuestStatus.NOT_STARTED:
            self.status = QuestStatus.ACTIVE
            
    def complete(self, player: 'Player'):
        """Complete the quest and give rewards"""
        if self.status == QuestStatus.COMPLETED:
            player.add_money(self.money_reward)
            player.add_experience(self.xp_reward)
            print(f"Quest completed: {self.title}")
            print(f"Rewards: ${self.money_reward}, {self.xp_reward} XP")
            
    def get_info(self) -> Dict[str, Any]:
        """Get quest information"""
        return {
            "id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "objectives": [obj.get_progress_text() for obj in self.objectives],
            "rewards": f"${self.money_reward}, {self.xp_reward} XP"
        }

class QuestSystem:
    """Manages all quests in the game"""
    
    def __init__(self):
        """Initialize quest system"""
        self.quests: Dict[str, Quest] = {}
        self.active_quests: List[str] = []
        self.completed_quests: List[str] = []
        
        # Create default quests
        self._create_default_quests()
        
    def _create_default_quests(self):
        """Create the default quest line"""
        # Tutorial quest
        tutorial = Quest("tutorial", "First Day", 
                        "Learn the basics of survival and monster hunting.",
                        money_reward=50, xp_reward=25)
        tutorial.add_objective(QuestObjective("Kill 5 monsters", "kill_monsters", 5))
        tutorial.add_objective(QuestObjective("Earn $100", "earn_money", 100))
        self.quests["tutorial"] = tutorial
        
        # Rent preparation quest
        rent_prep = Quest("rent_prep", "Rent Day Approaches", 
                         "Prepare for your first rent payment.",
                         money_reward=100, xp_reward=50)
        rent_prep.add_objective(QuestObjective("Earn $500 for rent", "earn_money", 500))
        rent_prep.add_objective(QuestObjective("Survive 5 days", "survive_days", 5))
        self.quests["rent_prep"] = rent_prep
        
        # Weapon upgrade quest
        weapon_upgrade = Quest("weapon_upgrade", "Arm Yourself", 
                              "Upgrade your equipment to handle tougher monsters.",
                              money_reward=200, xp_reward=75)
        weapon_upgrade.add_objective(QuestObjective("Purchase a weapon upgrade", "buy_upgrade", 1))
        weapon_upgrade.add_objective(QuestObjective("Kill 20 monsters", "kill_monsters", 20))
        self.quests["weapon_upgrade"] = weapon_upgrade
        
        # Wave survival quest
        wave_survival = Quest("wave_survival", "Monster Waves", 
                             "Survive increasingly difficult monster waves.",
                             money_reward=300, xp_reward=100)
        wave_survival.add_objective(QuestObjective("Reach wave 5", "reach_wave", 5))
        wave_survival.add_objective(QuestObjective("Kill 50 monsters", "kill_monsters", 50))
        self.quests["wave_survival"] = wave_survival
        
        # Boss battle quest
        boss_battle = Quest("boss_battle", "Troll Hunter", 
                           "Face the mighty Boss Troll in combat.",
                           money_reward=500, xp_reward=200)
        boss_battle.add_objective(QuestObjective("Kill 1 Boss Troll", "kill_boss", 1))
        self.quests["boss_battle"] = boss_battle
        
        # Auto-start tutorial
        self.start_quest("tutorial")
        
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest"""
        if quest_id in self.quests and quest_id not in self.active_quests:
            quest = self.quests[quest_id]
            quest.start()
            self.active_quests.append(quest_id)
            print(f"New quest started: {quest.title}")
            return True
        return False
        
    def update_quest_progress(self, objective_type: str, amount: int = 1):
        """Update progress for all active quests"""
        for quest_id in self.active_quests[:]:  # Copy to avoid modification during iteration
            quest = self.quests[quest_id]
            quest.update_objective(objective_type, amount)
            
            if quest.check_completion():
                self._complete_quest(quest_id)
                
    def _complete_quest(self, quest_id: str):
        """Complete a quest and handle progression"""
        if quest_id in self.active_quests:
            quest = self.quests[quest_id]
            self.active_quests.remove(quest_id)
            self.completed_quests.append(quest_id)
            
            # Start next quest in chain
            self._check_quest_chains(quest_id)
            
    def _check_quest_chains(self, completed_quest_id: str):
        """Check and start follow-up quests"""
        quest_chains = {
            "tutorial": "rent_prep",
            "rent_prep": "weapon_upgrade",
            "weapon_upgrade": "wave_survival",
            "wave_survival": "boss_battle"
        }
        
        if completed_quest_id in quest_chains:
            next_quest = quest_chains[completed_quest_id]
            self.start_quest(next_quest)
            
    def give_quest_rewards(self, quest_id: str, player: 'Player'):
        """Give rewards for completed quest"""
        if quest_id in self.completed_quests:
            quest = self.quests[quest_id]
            quest.complete(player)
            
    def get_active_quests(self) -> List[Dict[str, Any]]:
        """Get information about active quests"""
        return [self.quests[quest_id].get_info() for quest_id in self.active_quests]
        
    def get_completed_quests(self) -> List[Dict[str, Any]]:
        """Get information about completed quests"""
        return [self.quests[quest_id].get_info() for quest_id in self.completed_quests]
        
    def has_active_quest(self, quest_id: str) -> bool:
        """Check if a quest is active"""
        return quest_id in self.active_quests
        
    def has_completed_quest(self, quest_id: str) -> bool:
        """Check if a quest is completed"""
        return quest_id in self.completed_quests