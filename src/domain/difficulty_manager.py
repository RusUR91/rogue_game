from dataclasses import dataclass, field
from typing import Dict, List
from enum import Enum
import math

class DifficultyLevel(Enum):
    VERY_EASY = 0
    EASY = 1
    NORMAL = 2
    HARD = 3
    VERY_HARD = 4

@dataclass
class PlayerStats:
    """Статистика игрока для анализа"""
    avg_damage_per_hit: float = 0
    avg_hits_received_per_kill: float = 0
    health_usage_ratio: float = 1.0  
    food_usage_frequency: float = 0
    potion_usage_frequency: float = 0
    scroll_usage_frequency: float = 0
    steps_per_level: float = 0
    enemies_killed_per_level: float = 0
    treasure_collected_per_level: float = 0
    death_count: int = 0
    levels_completed_streak: int = 0
    avg_health_remaining: float = 0.5

@dataclass
class DifficultyConfig:
    """Конфигурация сложности для уровня"""
    enemy_count_multiplier: float = 1.0
    enemy_hp_multiplier: float = 1.0
    enemy_strength_multiplier: float = 1.0
    enemy_agility_multiplier: float = 1.0
    treasure_multiplier: float = 1.0
    food_spawn_multiplier: float = 1.0
    potion_spawn_multiplier: float = 1.0
    scroll_spawn_multiplier: float = 1.0
    weapon_spawn_multiplier: float = 1.0
    door_count_multiplier: float = 1.0

class DifficultyManager:
    def __init__(self):
        self.current_difficulty = DifficultyLevel.NORMAL
        self.player_stats = PlayerStats()
        self.recent_performance = []  
        self.difficulty_history = []
        
        
        self.thresholds = {
            DifficultyLevel.VERY_EASY: {"max_health_loss": 0.1, "min_kills": 0, "max_damage_taken": 5},
            DifficultyLevel.EASY: {"max_health_loss": 0.25, "min_kills": 1, "max_damage_taken": 15},
            DifficultyLevel.NORMAL: {"max_health_loss": 0.5, "min_kills": 3, "max_damage_taken": 30},
            DifficultyLevel.HARD: {"max_health_loss": 0.75, "min_kills": 5, "max_damage_taken": 50},
            DifficultyLevel.VERY_HARD: {"max_health_loss": 1.0, "min_kills": 7, "max_damage_taken": 100}
        }
        
        
        self.difficulty_modifiers = {
            DifficultyLevel.VERY_EASY: DifficultyConfig(
                enemy_count_multiplier=0.3,
                enemy_hp_multiplier=0.5,
                enemy_strength_multiplier=0.5,
                enemy_agility_multiplier=0.5,
                treasure_multiplier=0.5,
                food_spawn_multiplier=2.0,
                potion_spawn_multiplier=2.0,
                scroll_spawn_multiplier=1.5,
                weapon_spawn_multiplier=1.5,
                door_count_multiplier=0.3
            ),
            DifficultyLevel.EASY: DifficultyConfig(
                enemy_count_multiplier=0.6,
                enemy_hp_multiplier=0.7,
                enemy_strength_multiplier=0.7,
                enemy_agility_multiplier=0.7,
                treasure_multiplier=0.7,
                food_spawn_multiplier=1.5,
                potion_spawn_multiplier=1.5,
                scroll_spawn_multiplier=1.2,
                weapon_spawn_multiplier=1.2,
                door_count_multiplier=0.6
            ),
            DifficultyLevel.NORMAL: DifficultyConfig(
                enemy_count_multiplier=1.0,
                enemy_hp_multiplier=1.0,
                enemy_strength_multiplier=1.0,
                enemy_agility_multiplier=1.0,
                treasure_multiplier=1.0,
                food_spawn_multiplier=1.0,
                potion_spawn_multiplier=1.0,
                scroll_spawn_multiplier=1.0,
                weapon_spawn_multiplier=1.0,
                door_count_multiplier=1.0
            ),
            DifficultyLevel.HARD: DifficultyConfig(
                enemy_count_multiplier=1.5,
                enemy_hp_multiplier=1.3,
                enemy_strength_multiplier=1.3,
                enemy_agility_multiplier=1.2,
                treasure_multiplier=1.3,
                food_spawn_multiplier=0.7,
                potion_spawn_multiplier=0.7,
                scroll_spawn_multiplier=0.8,
                weapon_spawn_multiplier=0.8,
                door_count_multiplier=1.3
            ),
            DifficultyLevel.VERY_HARD: DifficultyConfig(
                enemy_count_multiplier=2.0,
                enemy_hp_multiplier=1.5,
                enemy_strength_multiplier=1.5,
                enemy_agility_multiplier=1.3,
                treasure_multiplier=1.5,
                food_spawn_multiplier=0.5,
                potion_spawn_multiplier=0.5,
                scroll_spawn_multiplier=0.6,
                weapon_spawn_multiplier=0.6,
                door_count_multiplier=1.5
            )
        }
    
    def update_stats(self, level_number: int, level_stats: Dict, player, level_completed: bool):
        """Обновляет статистику игрока после прохождения уровня"""
        if level_completed:
            self.player_stats.levels_completed_streak += 1
        else:
            self.player_stats.levels_completed_streak = 0
            self.player_stats.death_count += 1
        
        health_loss_ratio = 1 - (player.hp / player.max_hp) if level_completed else 1.0
        
        performance = {
            "level": level_number,
            "health_loss": health_loss_ratio,
            "enemies_killed": level_stats.get("enemies_killed", 0),
            "damage_taken": level_stats.get("damage_taken", 0),
            "food_used": level_stats.get("food_used", 0),
            "potions_used": level_stats.get("potions_used", 0),
            "scrolls_used": level_stats.get("scrolls_used", 0),
            "steps": level_stats.get("steps", 0),
            "treasure": level_stats.get("treasure", 0),
            "completed": level_completed
        }
        
        self.recent_performance.append(performance)
        if len(self.recent_performance) > 5:
            self.recent_performance.pop(0)
        
        if self.recent_performance:
            recent = self.recent_performance[-3:]  
            self.player_stats.avg_health_remaining = 1 - sum(p["health_loss"] for p in recent) / len(recent)
            self.player_stats.enemies_killed_per_level = sum(p["enemies_killed"] for p in recent) / len(recent)
            self.player_stats.food_usage_frequency = sum(p["food_used"] for p in recent) / len(recent)
            self.player_stats.potion_usage_frequency = sum(p["potions_used"] for p in recent) / len(recent)
            self.player_stats.scroll_usage_frequency = sum(p["scrolls_used"] for p in recent) / len(recent)
            self.player_stats.steps_per_level = sum(p["steps"] for p in recent) / len(recent)
    
    def calculate_difficulty(self) -> DifficultyLevel:
        """Рассчитывает текущую сложность на основе статистики игрока"""
        if not self.recent_performance:
            return DifficultyLevel.NORMAL
        
        score = 0
        recent = self.recent_performance[-3:]
        
        # Фактор 1: Потеря здоровья (0-40 баллов)
        avg_health_loss = sum(p["health_loss"] for p in recent) / len(recent)
        if avg_health_loss < 0.2:
            score -= 20  # Игроку слишком легко
        elif avg_health_loss > 0.7:
            score += 20  # Игроку тяжело
        
        # Фактор 2: Убийства врагов (0-30 баллов)
        avg_kills = sum(p["enemies_killed"] for p in recent) / len(recent)
        expected_kills = 3 + self.player_stats.levels_completed_streak * 0.5
        if avg_kills > expected_kills + 2:
            score -= 15  # Легко убивает врагов
        elif avg_kills < expected_kills - 2:
            score += 15  # Трудно убивает врагов
        
        # Фактор 3: Использование предметов (0-20 баллов)
        avg_item_usage = (sum(p["food_used"] for p in recent) + 
                         sum(p["potions_used"] for p in recent) * 2 +
                         sum(p["scrolls_used"] for p in recent)) / len(recent)
        if avg_item_usage > 3:
            score += 15  # Много использует предметы - тяжело
        elif avg_item_usage < 1:
            score -= 10  # Мало использует предметы - легко
        
        # Фактор 4: Серия побед (0-20 баллов)
        if self.player_stats.levels_completed_streak >= 3:
            score -= 15  # Легко, если выигрывает подряд
        elif self.player_stats.death_count > 0 and self.player_stats.levels_completed_streak == 0:
            score += 15  # Тяжело, если только что умер
        
        # Фактор 5: Скорость прохождения (0-10 баллов)
        avg_steps = sum(p["steps"] for p in recent) / len(recent)
        if avg_steps < 300:
            score -= 10  # Быстро проходит - легко
        elif avg_steps > 800:
            score += 10  # Медленно - тяжело
        
        # Определяем уровень сложности
        if score <= -40:
            return DifficultyLevel.VERY_EASY
        elif score <= -15:
            return DifficultyLevel.EASY
        elif score <= 15:
            return DifficultyLevel.NORMAL
        elif score <= 40:
            return DifficultyLevel.HARD
        else:
            return DifficultyLevel.VERY_HARD
    
    def get_difficulty_config(self) -> DifficultyConfig:
        """Возвращает конфигурацию для текущего уровня сложности"""
        self.current_difficulty = self.calculate_difficulty()
        self.difficulty_history.append(self.current_difficulty)
        return self.difficulty_modifiers[self.current_difficulty]
    
    def get_difficulty_name(self) -> str:
        """Возвращает название текущей сложности"""
        names = {
            DifficultyLevel.VERY_EASY: "ОЧЕНЬ ЛЕГКО",
            DifficultyLevel.EASY: "ЛЕГКО",
            DifficultyLevel.NORMAL: "НОРМАЛЬНО",
            DifficultyLevel.HARD: "СЛОЖНО",
            DifficultyLevel.VERY_HARD: "ОЧЕНЬ СЛОЖНО"
        }
        return names.get(self.current_difficulty, "НОРМАЛЬНО")
    
    def should_spawn_extra_health(self) -> bool:
        """Проверяет, нужно ли добавить дополнительное здоровье"""
        return self.player_stats.avg_health_remaining < 0.3
    
    def get_health_boost_multiplier(self) -> float:
        """Возвращает множитель для здоровья в предметах"""
        if self.player_stats.avg_health_remaining < 0.2:
            return 2.0
        elif self.player_stats.avg_health_remaining < 0.4:
            return 1.5
        return 1.0