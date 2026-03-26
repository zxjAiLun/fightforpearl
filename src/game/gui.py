"""游戏 GUI 界面"""
import pygame
import os
import webbrowser
from typing import Optional, Callable

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

PANEL_WIDTH = 240
PANEL_HEIGHT = 160
MAX_ENEMIES = 5
MAX_CHARACTERS = 4

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (220, 80, 80)
GREEN = (80, 200, 80)
BLUE = (80, 120, 220)
YELLOW = (220, 200, 80)
PURPLE = (180, 100, 220)
CYAN = (100, 200, 200)
DARK_GREEN = (50, 150, 50)
ORANGE = (255, 165, 0)

ELEMENT_COLORS = {
    "PHYSICAL": (180, 160, 140),
    "WIND": (80, 200, 120),
    "THUNDER": (160, 140, 255),
    "FIRE": (255, 100, 80),
    "ICE": (120, 200, 255),
    "QUANTUM": (140, 80, 200),
    "IMAGINARY": (200, 160, 80),
}

shared_battle_points = 0
shared_battle_points_limit = 3


class GUIStyle:
    def __init__(self):
        self.font = None
        self.font_large = None
        self.font_small = None
        
    def init_fonts(self):
        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("microsoftyaheiui", 20)
            self.font_large = pygame.font.SysFont("microsoftyaheiui", 28)
            self.font_small = pygame.font.SysFont("microsoftyaheiui", 16)
        except:
            self.font = pygame.font.SysFont(None, 24)
            self.font_large = pygame.font.SysFont(None, 32)
            self.font_small = pygame.font.SysFont(None, 18)


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: tuple, hover_color: tuple = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or color
        self.is_hovered = False
        self.is_toggled = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_toggled = not self.is_toggled
                return True
        return False
    
    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        
        text_surface = style.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class SpeedSlider:
    def __init__(self, x: int, y: int, width: int, height: int, min_val: float, max_val: float, default_val: float):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.is_dragging = False
        
        self.handle_radius = 12
        self.handle_rect = pygame.Rect(x - self.handle_radius, y - self.handle_radius, 
                                       width + self.handle_radius * 2, height + self.handle_radius * 2)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.is_dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                rel_x = event.pos[0] - self.rect.x
                ratio = max(0, min(1, rel_x / self.rect.width))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
                return True
        return False
    
    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=4)
        
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * self.rect.width)
        handle_y = self.rect.y + self.rect.height // 2
        pygame.draw.circle(screen, GREEN, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(screen, WHITE, (handle_x, handle_y), self.handle_radius, 2)
        
        label = style.font_small.render(f"Speed: {self.value:.1f}x", True, WHITE)
        screen.blit(label, (self.rect.x, self.rect.y - 25))


def render_character_box_contents(panel, screen: pygame.Surface, style: GUIStyle, x: int, y: int) -> None:
    name_text = style.font_large.render(panel.name, True, panel.color)
    screen.blit(name_text, (x, y))

    hp_ratio = panel.hp / panel.max_hp if panel.max_hp > 0 else 0
    hp_bar_bg = pygame.Rect(x + 70, y + 2, 140, 18)
    pygame.draw.rect(screen, DARK_GRAY, hp_bar_bg, border_radius=4)
    hp_bar = pygame.Rect(x + 70, y + 2, int(140 * hp_ratio), 18)
    pygame.draw.rect(screen, GREEN if hp_ratio > 0.3 else RED, hp_bar, border_radius=4)
    y += 28

    
    hp_text = style.font.render(f"HP: {panel.hp}/{panel.max_hp}", True, WHITE)
    screen.blit(hp_text, (x, y))

    
    y += 28

    energy_text = style.font.render(f"Energy: {panel.energy}/{panel.energy_limit}", True, YELLOW)
    screen.blit(energy_text, (x, y))
    y += 24

    spd_text = style.font.render(f"SPD: {panel.spd}", True, GRAY)
    screen.blit(spd_text, (x, y))
    y += 24

    # av_text = style.font.render(f"AV: {panel.action_value:.2f}", True, PURPLE)
    # screen.blit(av_text, (x, y))


def render_enemy_box_contents(panel, screen: pygame.Surface, style: GUIStyle, x: int, y: int) -> None:
    name_text = style.font_large.render(panel.name, True, panel.color)
    screen.blit(name_text, (x, y))

    hp_ratio = panel.hp / panel.max_hp if panel.max_hp > 0 else 0
    hp_bar_bg = pygame.Rect(x + 70, y + 2, 140, 18)
    pygame.draw.rect(screen, DARK_GRAY, hp_bar_bg, border_radius=4)
    hp_bar = pygame.Rect(x + 70, y + 2, int(140 * hp_ratio), 18)
    pygame.draw.rect(screen, GREEN if hp_ratio > 0.3 else RED, hp_bar, border_radius=4)
    y += 28

    hp_text = style.font.render(f"HP: {panel.hp}/{panel.max_hp}", True, WHITE)
    screen.blit(hp_text, (x, y))
    
    y += 28

    weakness_text = style.font.render(f"Weakness: {panel.weakness}", True, ELEMENT_COLORS.get(panel.weakness, WHITE))
    screen.blit(weakness_text, (x, y))
    y += 28

    if panel.recent_buffs:
        buff_label = style.font.render("Buffs:", True, GRAY)
        screen.blit(buff_label, (x, y))
        x += 70
        for i, buff in enumerate(panel.recent_buffs):
            buff_text = style.font_small.render(str(buff), True, GREEN)
            screen.blit(buff_text, (x, y))
            x += 60


class CharacterPanel:
    def __init__(self, x: int, y: int, width: int, height: int, is_enemy: bool = False, index: int = 0):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_enemy = is_enemy
        self.index = index
        self.name = ""
        self.element = "PHYSICAL"
        self.hp = 0
        self.max_hp = 1
        self.energy = 0
        self.energy_limit = 120
        self.spd = 100
        self.action_value = 0
        self.toughness = 0
        self.max_toughness = 100
        self.color = WHITE
        self.is_selected = False
        self.weakness = "PHYSICAL"
        self.recent_buffs = []
        self.char_ref = None

    def set_character(self, char) -> None:
        self.char_ref = char
        self.name = char.name
        self.element = char.element.name
        self.hp = char.current_hp
        self.max_hp = char.stat.total_max_hp()
        self.energy = int(char.energy)
        self.energy_limit = char.energy_limit
        self.spd = char.stat.total_spd()
        self.action_value = getattr(char, 'action_value', 0)
        self.toughness = getattr(char, 'toughness', 0)
        self.max_toughness = 100
        self.color = ELEMENT_COLORS.get(self.element, WHITE)
        self.weakness = char.element.name
        self.recent_buffs = list(char.effects)[-2:] if hasattr(char, 'effects') and char.effects else []

    def handle_click(self, pos) -> bool:
        return self.rect.collidepoint(pos)

    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        if self.is_enemy:
            panel_color = (40, 40, 50)
        else:
            panel_color = (50, 50, 60)

        if self.is_selected:
            border_color = YELLOW
        else:
            border_color = self.color

        pygame.draw.rect(screen, panel_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=8)

        x = self.rect.x + 10
        y = self.rect.y + 10

        if self.is_enemy:
            render_enemy_box_contents(self, screen, style, x, y)
        else:
            render_character_box_contents(self, screen, style, x, y)


class EnemyDetailPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.target_enemy: Optional[CharacterPanel] = None
        self.battle_state = None

    def show(self, enemy_panel: CharacterPanel, battle_state=None) -> None:
        self.target_enemy = enemy_panel
        self.battle_state = battle_state
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self.target_enemy = None
        self.battle_state = None

    def handle_click(self, pos) -> bool:
        if not self.visible:
            return False
        if not self.rect.collidepoint(pos):
            self.hide()
            return True
        return False

    def draw(self, screen: pygame.Surface, style: GUIStyle, battle_state=None) -> None:
        if not self.visible or self.target_enemy is None:
            return

        pygame.draw.rect(screen, (30, 30, 40), self.rect, border_radius=8)
        pygame.draw.rect(screen, YELLOW, self.rect, 2, border_radius=8)

        char = self.target_enemy.char_ref
        if char is None:
            return

        x = self.rect.x + 15
        y = self.rect.y + 15

        name_text = style.font_large.render(char.name, True, WHITE)
        screen.blit(name_text, (x, y))
        y += 40

        weakness_color = ELEMENT_COLORS.get(char.element.name, WHITE)
        weakness_text = style.font.render(f"Weakness: {char.element.name}", True, weakness_color)
        screen.blit(weakness_text, (x, y))
        y += 28

        hp_ratio = char.current_hp / char.stat.total_max_hp() if char.stat.total_max_hp() > 0 else 0
        hp_text = style.font.render(f"HP: {char.current_hp}/{char.stat.total_max_hp()}", True, WHITE)
        screen.blit(hp_text, (x, y))

        bar_x = x + 80
        bar_width = 200
        bar_height = 18
        hp_bar_bg = pygame.Rect(bar_x, y + 2, bar_width, bar_height)
        pygame.draw.rect(screen, DARK_GRAY, hp_bar_bg, border_radius=4)
        hp_bar = pygame.Rect(bar_x, y + 2, int(bar_width * hp_ratio), bar_height)
        pygame.draw.rect(screen, GREEN if hp_ratio > 0.3 else RED, hp_bar, border_radius=4)
        y += 28

        toughness = getattr(char, 'toughness', 0)
        max_toughness = 100
        toughness_ratio = toughness / max_toughness if max_toughness > 0 else 0
        toughness_text = style.font.render(f"Toughness: {toughness}/{max_toughness}", True, WHITE)
        screen.blit(toughness_text, (x, y))

        bar_x = x + 100
        bar_width = 180
        t_bar_bg = pygame.Rect(bar_x, y + 2, bar_width, bar_height)
        pygame.draw.rect(screen, DARK_GRAY, t_bar_bg, border_radius=4)
        t_bar = pygame.Rect(bar_x, y + 2, int(bar_width * toughness_ratio), bar_height)
        pygame.draw.rect(screen, BLUE, t_bar, border_radius=4)
        y += 28

        spd = char.stat.total_spd()
        spd_text = style.font.render(f"SPD: {spd}", True, WHITE)
        screen.blit(spd_text, (x, y))
        y += 24

        atk = char.stat.total_atk()
        atk_text = style.font.render(f"ATK: {atk}", True, WHITE)
        screen.blit(atk_text, (x, y))
        y += 24

        defense = char.stat.total_def()
        def_text = style.font.render(f"DEF: {defense}", True, WHITE)
        screen.blit(def_text, (x, y))
        y += 28

        if hasattr(char, 'skills') and char.skills:
            skills_text = style.font.render("Skills:", True, YELLOW)
            screen.blit(skills_text, (x, y))
            y += 24
            for skill in char.skills:
                skill_name = skill.name if hasattr(skill, 'name') else str(skill)
                skill_text = style.font_small.render(f"  - {skill_name}", True, GRAY)
                screen.blit(skill_text, (x, y))
                y += 20
                if y > self.rect.bottom - 20:
                    break

        if hasattr(char, 'effects') and char.effects:
            y += 8
            effects_text = style.font.render("Effects:", True, PURPLE)
            screen.blit(effects_text, (x, y))
            y += 24
            for effect in char.effects:
                effect_name = effect.name if hasattr(effect, 'name') else str(effect)
                duration = getattr(effect, 'duration', 0)
                effect_str = f"{effect_name} ({duration} turns)"
                effect_text = style.font_small.render(effect_str, True, CYAN)
                screen.blit(effect_text, (x, y))
                y += 18
                if y > self.rect.bottom - 20:
                    effect_overflow = style.font_small.render("  ...", True, GRAY)
                    screen.blit(effect_overflow, (x, y))
                    break


class ActionBar:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.entries = []
        self.current_round = 1
        self.round_end_time = 150.0

    def update_entries(self, player_team, enemy_team, current_actor=None, current_time=0.0, round_end_time=150.0):
        self.entries = []
        all_chars = player_team + enemy_team
        self.current_round = round_end_time
        self.round_end_time = round_end_time

        for char in all_chars:
            av = getattr(char, 'action_value', 0)
            spd = char.stat.total_spd()
            is_enemy = getattr(char, 'is_enemy', False)

            distance_to_next = av - current_time
            is_current = char == current_actor
            self.entries.append({
                'name': char.name,
                'action_value': av,
                'distance_to_next': distance_to_next,
                'spd': spd,
                'is_enemy': is_enemy,
                'is_current': is_current,
                'is_round_marker': False
            })

        rm_distance = round_end_time - current_time
        self.entries.append({
            'name': f"round{1 if round_end_time <= 150 else 2}end",
            'action_value': round_end_time,
            'distance_to_next': rm_distance,
            'spd': 0,
            'is_enemy': False,
            'is_current': False,
            'is_round_marker': True
        })

        self.entries.sort(key=lambda e: e['distance_to_next'])

    def draw(self, screen: pygame.Surface, style: GUIStyle, current_round_turns=None, current_time=0.0, round_end_time=150.0) -> None:
        pygame.draw.rect(screen, (20, 20, 25), self.rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, self.rect, 1, border_radius=8)

        turn_text = f"Turn {current_round_turns}" if current_round_turns else "Action Order"
        title = style.font_small.render(turn_text, True, WHITE)
        screen.blit(title, (self.rect.x + 10, self.rect.y + 5))

        y = self.rect.y + 30
        bar_width = self.rect.width - 20
        bar_height = 24

        for entry in self.entries:
            if y > self.rect.bottom - 30:
                break

            distance = entry['distance_to_next']
            progress = max(0, min(1.0, distance / 100.0))

            bar_x = self.rect.x + 10
            bar_y = y

            if entry.get('is_round_marker', False):
                bg_color = (60, 50, 30)
                fill_color = YELLOW
            elif entry['is_current']:
                bg_color = ORANGE
                fill_color = GREEN if not entry['is_enemy'] else RED
            elif entry['is_enemy']:
                bg_color = (80, 40, 40)
                fill_color = RED
            else:
                bg_color = (40, 60, 80)
                fill_color = GREEN

            pygame.draw.rect(screen, bg_color, (bar_x, bar_y, bar_width, bar_height), border_radius=4)

            fill_width = int(bar_width * progress)
            if fill_width > 0:
                pygame.draw.rect(screen, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)

            name_text = style.font_small.render(entry['name'][:8], True, WHITE)
            screen.blit(name_text, (bar_x + 5, bar_y + 4))

            dist_text = f"{distance:.1f}"
            av_surface = style.font_small.render(dist_text, True, WHITE)
            screen.blit(av_surface, (bar_x + bar_width - 40, bar_y + 4))

            y += bar_height + 4


class BattleLogPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.messages = []
        self.max_display = 8
        self.scroll_offset = 0
        
    def add_message(self, message: str) -> None:
        self.messages.append(message)
        total_msgs = len(self.messages)
        if total_msgs > self.max_display:
            if self.scroll_offset >= total_msgs - self.max_display - 1:
                self.scroll_offset = max(0, total_msgs - self.max_display)
        else:
            self.scroll_offset = 0
        
    def handle_scroll(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_offset = max(0, self.scroll_offset - 3)
            else:
                self.scroll_offset = min(max(0, len(self.messages) - self.max_display), self.scroll_offset + 3)
            return True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 3)
                return True
            elif event.key == pygame.K_DOWN:
                self.scroll_offset = min(max(0, len(self.messages) - self.max_display), self.scroll_offset + 3)
                return True
        return False
            
    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        pygame.draw.rect(screen, (30, 30, 35), self.rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, self.rect, 1, border_radius=8)
        
        total_msgs = len(self.messages)
        if total_msgs > self.max_display:
            scrollbar_height = self.rect.height * self.max_display / total_msgs
            scrollbar_y = self.rect.y + (self.scroll_offset / max(1, total_msgs - self.max_display)) * (self.rect.height - scrollbar_height)
            pygame.draw.rect(screen, DARK_GRAY, (self.rect.right - 15, scrollbar_y, 10, scrollbar_height), border_radius=3)
        
        y = self.rect.y + 10
        visible_msgs = self.messages[self.scroll_offset:self.scroll_offset + self.max_display]
        
        for msg in visible_msgs:
            if y > self.rect.bottom - 15:
                break
            text = style.font_small.render(msg[:80], True, WHITE)
            screen.blit(text, (self.rect.x + 10, y))
            y += 20

    def clear(self) -> None:
        self.messages.clear()
        self.scroll_offset = 0


class BattlePointsDisplay:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.width = 120
        self.height = 40
        
    def draw(self, screen: pygame.Surface, style: GUIStyle, current: int, maximum: int) -> None:
        pygame.draw.rect(screen, (30, 30, 40), (self.x, self.y, self.width, self.height), border_radius=6)
        pygame.draw.rect(screen, CYAN, (self.x, self.y, self.width, self.height), 1, border_radius=6)
        text = style.font.render(f"战技点: {current}/{maximum}", True, CYAN)
        screen.blit(text, (self.x + 10, self.y + 10))


class StatDetailPanel:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.char_panel = None
        self.battle_state = None
        
    def set_character(self, char_panel, battle_state=None) -> None:
        self.char_panel = char_panel
        self.battle_state = battle_state
        self.visible = True
        
    def hide(self) -> None:
        self.visible = False
        self.char_panel = None


class SkillInfoPanel:
    """显示当前行动角色的技能信息面板"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        self.current_character = None
        self.battle_state = None
        
    def set_character(self, char, battle_state=None) -> None:
        self.current_character = char
        self.battle_state = battle_state
        self.visible = char is not None
        
    def hide(self) -> None:
        self.visible = False
        self.current_character = None
        
    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        if not self.visible or not self.current_character:
            return
            
        char = self.current_character
        
        # 半透明背景
        overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        overlay.fill((20, 20, 30, 230))
        screen.blit(overlay, (self.rect.x, self.rect.y))
        
        pygame.draw.rect(screen, CYAN, self.rect, 1, border_radius=8)
        
        x = self.rect.x + 15
        y = self.rect.y + 15
        
        # 标题
        title = style.font_large.render(f"{char.name} 的技能", True, CYAN)
        screen.blit(title, (x, y))
        y += 35
        
        # 显示能量和战绩点状态
        energy_text = f"能量: {int(char.energy)}/{char.energy_limit}"
        if hasattr(char, 'battle_points') and self.battle_state:
            bp = self.battle_state.shared_battle_points
            bp_limit = self.battle_state.shared_battle_points_limit
            energy_text += f"  |  战绩点: {bp}/{bp_limit}"
        energy_surface = style.font.render(energy_text, True, YELLOW)
        screen.blit(energy_surface, (x, y))
        y += 30
        
        # 技能列表
        if hasattr(char, 'skills') and char.skills:
            for skill in char.skills:
                skill_type = skill.type.name
                
                # 检查技能是否可用
                can_use = True
                cost_info = ""
                
                if skill.type.name == "SPECIAL":
                    if self.battle_state and self.battle_state.shared_battle_points < 1:
                        can_use = False
                        cost_info = " (战绩点不足)"
                    else:
                        cost_info = " (消耗1战绩点)"
                elif skill.type.name == "ULT":
                    if char.energy < char.energy_limit:
                        can_use = False
                        cost_info = " (能量不足)"
                
                color = GREEN if can_use else GRAY
                skill_text = f"• {skill.name}"
                if cost_info:
                    skill_text += cost_info
                    
                skill_surface = style.font.render(skill_text, True, color)
                screen.blit(skill_surface, (x, y))
                y += 25
        else:
            no_skill = style.font.render("无可用技能", True, GRAY)
            screen.blit(no_skill, (x, y))
        self.battle_state = None
        
    def draw(self, screen: pygame.Surface, style: GUIStyle) -> None:
        if not self.visible or self.char_panel is None:
            return
            
        pygame.draw.rect(screen, (30, 30, 40), self.rect, border_radius=8)
        pygame.draw.rect(screen, YELLOW, self.rect, 2, border_radius=8)
        
        x = self.rect.x + 15
        y = self.rect.y + 15
        
        title = style.font_large.render(f"{self.char_panel.name} Stats", True, WHITE)
        screen.blit(title, (x, y))
        y += 40
        
        stats_text = [
            f"HP: {self.char_panel.hp}/{self.char_panel.max_hp}",
            f"Energy: {self.char_panel.energy}/{self.char_panel.energy_limit}",
            f"SPD: {self.char_panel.spd}",
            f"Action Value: {self.char_panel.action_value:.2f}",
        ]
        
        for text in stats_text:
            text_surf = style.font.render(text, True, WHITE)
            screen.blit(text_surf, (x, y))
            y += 25


class BattleGUI:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Fight for Pearl - Battle Demo")
        self.clock = pygame.time.Clock()
        self.style = GUIStyle()
        self.style.init_fonts()
        
        self.player_panels: list[CharacterPanel] = []
        self.enemy_panels: list[CharacterPanel] = []
        self.action_bar = ActionBar(10, 10, 200, 400)
        self.log_panel = BattleLogPanel(10, 420, 200, 250)
        self.stat_panel = StatDetailPanel(320, 50, 300, 320)
        self.enemy_detail_panel = EnemyDetailPanel(400, 200, 400, 400)
        self.battle_points_display = BattlePointsDisplay(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 60)

        button_width = 100
        button_height = 40
        button_spacing = 15
        total_buttons_width = button_width * 4 + button_spacing * 3 + 200
        button_start_x = (SCREEN_WIDTH - total_buttons_width) // 2
        button_y = SCREEN_HEIGHT - 50

        self.play_button = Button(button_start_x, button_y, button_width, button_height, "Pause", GREEN, DARK_GREEN)
        self.step_button = Button(button_start_x + button_width + button_spacing, button_y, button_width, button_height, "Step", BLUE)
        self.step_back_button = Button(button_start_x + (button_width + button_spacing) * 2, button_y, button_width, button_height, "Back", PURPLE)
        self.restart_button = Button(button_start_x + (button_width + button_spacing) * 3, button_y, button_width, button_height, "Restart", RED)
        self.export_button = Button(button_start_x + (button_width + button_spacing) * 4, button_y, button_width, button_height, "Export", ORANGE)

        self.speed_slider = SpeedSlider(button_start_x + (button_width + button_spacing) * 5, button_y + 10, 200, 20, 0.5, 5.0, 1.0)
        
        self.on_action_callback: Optional[Callable] = None
        self.is_battle_over = False
        self.is_paused = True
        self.step_requested = False
        self.winner = None
        self.current_speed = 1.0
        self.current_turn = 1
        self.current_actor = None
        self.selected_panel = None
        self.current_time = 0.0
        self.round_end_time = 150.0
        self.battle_engine = None
        self.battle_state = None
        
        # 技能信息面板
        self.skill_info_panel = SkillInfoPanel(SCREEN_WIDTH - 220, 200, 200, 250)
        
        self._init_panels()
        
    def _init_panels(self) -> None:
        enemy_start_x = 220
        for i in range(MAX_ENEMIES):
            panel = CharacterPanel(enemy_start_x + i * (PANEL_WIDTH + 10), 10, PANEL_WIDTH, PANEL_HEIGHT, is_enemy=True, index=i)
            self.enemy_panels.append(panel)

        char_start_x = 220
        # char_start_x = (SCREEN_WIDTH - PANEL_WIDTH * MAX_CHARACTERS - 20) // 2 + 280
        char_y = SCREEN_HEIGHT - PANEL_HEIGHT - 10 - 40  # 向上移动一个button高度
        for i in range(MAX_CHARACTERS):
            panel = CharacterPanel(char_start_x + i * (PANEL_WIDTH + 10), char_y, PANEL_WIDTH, PANEL_HEIGHT, is_enemy=False, index=i)
            self.player_panels.append(panel)

    def update_characters(self, state) -> None:
        self.battle_state = state
        
        for i, char in enumerate(state.player_team):
            if i < len(self.player_panels):
                self.player_panels[i].set_character(char)

        for i, char in enumerate(state.enemy_team):
            if i < len(self.enemy_panels):
                self.enemy_panels[i].set_character(char)

        all_chars = state.player_team + state.enemy_team
        alive = [c for c in all_chars if c.is_alive()]
        alive.sort(key=lambda c: c.action_value)
        self.current_actor = alive[0] if alive else None

        global shared_battle_points, shared_battle_points_limit
        shared_battle_points = state.shared_battle_points
        shared_battle_points_limit = state.shared_battle_points_limit

        self.action_bar.update_entries(state.player_team, state.enemy_team, self.current_actor, self.current_time, self.round_end_time)
        
        # 更新技能信息面板（显示当前行动的角色）
        if self.current_actor and not self.current_actor.is_enemy:
            self.skill_info_panel.set_character(self.current_actor, self.battle_state)
        else:
            self.skill_info_panel.hide()

    def add_log(self, message: str) -> None:
        self.log_panel.add_message(message)

    def set_battle_over(self, winner: str) -> None:
        self.is_battle_over = True
        self.winner = winner
        self.play_button.text = "Play"
        self.play_button.color = GREEN

    def set_turn(self, turn: int) -> None:
        self.current_turn = turn

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_SPACE:
                    self.is_paused = not self.is_paused
                    self.play_button.text = "Pause" if not self.is_paused else "Play"
                    self.play_button.color = GREEN if not self.is_paused else RED
                    continue
                if event.key == pygame.K_s:
                    self.step_requested = True
                    continue
                if event.key == pygame.K_r and self.is_battle_over:
                    self.is_battle_over = False
                    self.log_panel.clear()
                    if self.on_action_callback:
                        self.on_action_callback("restart")
                    continue
                if event.key == pygame.K_e:
                    self._export_log()
                    continue
                    
            if self.log_panel.handle_scroll(event):
                continue
            
            self.play_button.handle_event(event)
            self.step_button.handle_event(event)
            self.step_back_button.handle_event(event)
            self.restart_button.handle_event(event)
            self.export_button.handle_event(event)
            self.speed_slider.handle_event(event)
            
            if self.play_button.is_toggled:
                self.play_button.is_toggled = False
                self.is_paused = not self.is_paused
                self.play_button.text = "Pause" if not self.is_paused else "Play"
                self.play_button.color = GREEN if not self.is_paused else RED
                
            if self.step_button.is_toggled:
                self.step_button.is_toggled = False
                self.step_requested = True
                
            if self.step_back_button.is_toggled:
                self.step_back_button.is_toggled = False
                if self.battle_engine and self.battle_engine.step_back():
                    self.add_log("[回退] 已回退到上一个行动")
                    self.update_characters(self.battle_state)
                else:
                    self.add_log("[回退] 无法回退")
                
            if self.restart_button.is_toggled:
                self.restart_button.is_toggled = False
                self.is_battle_over = False
                self.log_panel.clear()
                if self.on_action_callback:
                    self.on_action_callback("restart")
                    
            if self.export_button.is_toggled:
                self.export_button.is_toggled = False
                self._export_log()
                
            if event.type == pygame.MOUSEBUTTONDOWN and self.is_paused:
                if self.enemy_detail_panel.visible:
                    if self.enemy_detail_panel.handle_click(event.pos):
                        continue

                for i, panel in enumerate(self.player_panels):
                    if panel.handle_click(event.pos):
                        self.selected_panel = panel
                        panel.is_selected = True
                        for p in self.player_panels + self.enemy_panels:
                            if p != panel:
                                p.is_selected = False
                        self.stat_panel.set_character(panel)
                        self.enemy_detail_panel.hide()
                        break
                else:
                    for i, panel in enumerate(self.enemy_panels):
                        if panel.handle_click(event.pos):
                            self.selected_panel = panel
                            panel.is_selected = True
                            for p in self.player_panels + self.enemy_panels:
                                if p != panel:
                                    p.is_selected = False
                            self.enemy_detail_panel.show(panel, self.battle_state)
                            break
                    else:
                        for panel in self.player_panels + self.enemy_panels:
                            panel.is_selected = False
                        self.stat_panel.hide()
                        self.enemy_detail_panel.hide()
                        
        return True

    def _export_log(self) -> None:
        filepath = "battle_log.json"
        with open(filepath, "w", encoding="utf-8") as f:
            import json
            json.dump(self.log_panel.messages, f, ensure_ascii=False, indent=2)
        try:
            webbrowser.open(os.path.abspath(filepath))
        except:
            pass

    def draw(self) -> None:
        self.screen.fill((20, 20, 25))
        
        title = self.style.font_large.render(f"Fight for Pearl - Turn {self.current_turn}", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - 100, 10))
        
        if self.is_paused and not self.is_battle_over:
            pause_text = self.style.font.render("PAUSED - SPACE to play", True, YELLOW)
            self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - 120, 40))
        
        self.action_bar.draw(self.screen, self.style, self.current_turn, self.current_time, self.round_end_time)
        
        for panel in self.player_panels:
            panel.draw(self.screen, self.style)
            
        for panel in self.enemy_panels:
            panel.draw(self.screen, self.style)

        self.log_panel.draw(self.screen, self.style)
        self.stat_panel.draw(self.screen, self.style)
        self.enemy_detail_panel.draw(self.screen, self.style, self.battle_state)
        self.skill_info_panel.draw(self.screen, self.style)
        
        self.play_button.draw(self.screen, self.style)
        self.step_button.draw(self.screen, self.style)
        self.step_back_button.draw(self.screen, self.style)
        self.restart_button.draw(self.screen, self.style)
        self.export_button.draw(self.screen, self.style)
        self.speed_slider.draw(self.screen, self.style)
        
        hint_text = self.style.font_small.render("UP/DOWN: Scroll | E: Export Log", True, GRAY)
        self.screen.blit(hint_text, (self.log_panel.rect.x, self.log_panel.rect.y - 20))
        
        self.battle_points_display.draw(self.screen, self.style, shared_battle_points, shared_battle_points_limit)
        
        if self.is_battle_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            result_text = f"{self.winner} Victory!" if self.winner == "Player" else f"{self.winner} Defeat..."
            result_color = GREEN if self.winner == "Player" else RED
            result = self.style.font_large.render(result_text, True, result_color)
            self.screen.blit(result, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 30))
        
        pygame.display.flip()


def start_gui_battle(battle_state) -> 'BattleGUI':
    from .battle import BattleEngine
    import time

    gui = BattleGUI()
    engine = BattleEngine(battle_state)

    def on_restart(msg: str = None):
        gui.is_battle_over = False
        gui.log_panel.clear()
        gui.current_turn = 1
        for char in battle_state.player_team + battle_state.enemy_team:
            char.current_hp = char.stat.total_max_hp()
            char.action_value = char.calculate_init_action_value()
            char.energy = char.energy_limit / 2
        battle_state.shared_battle_points = 3
        engine.events.clear()
        engine._current_turn = 1
        engine._init_action_values()
        gui.current_time = 0.0
        gui.round_end_time = 150.0
        gui.update_characters(battle_state)
        gui.add_log(f"=== Battle Restart - Turn 1 ===")

    gui.battle_engine = engine
    gui.on_action_callback = on_restart

    def log_callback(event):
        if event.action in ["BASIC", "SPECIAL", "ULT", "FOLLOW_UP"]:
            detail = event.detail
            if "造成共计" in detail:
                parts = detail.split("攻击")
                if len(parts) >= 2:
                    actor_part = parts[0].replace("使用 普通攻击", "").replace("使用 战技", "").replace("使用 大招", "")
                    target_part = parts[1].split("，")[0].strip()
                    damage_part = detail.split("造成共计")[1].split("伤害")[0].strip()
                    simplified = f"{actor_part} 对 {target_part} 造成 {damage_part} 伤害"
                    gui.add_log(simplified)
                else:
                    gui.add_log(detail)
            elif "造成" in detail:
                parts = detail.split("攻击")
                if len(parts) >= 2:
                    actor_part = parts[0].replace("使用 普通攻击", "").replace("使用 战技", "").replace("使用 大招", "")
                    target_part = parts[1].split("，")[0].split("伤害")[0].strip()
                    damage = detail.split("造成")[1].split("伤害")[0].strip()
                    simplified = f"{actor_part} 对 {target_part} 造成 {damage} 伤害"
                    gui.add_log(simplified)
                else:
                    gui.add_log(detail)
            else:
                gui.add_log(detail)
        elif event.action in ["START", "ROUND_MARKER"]:
            gui.add_log(f"[{event.turn}] {event.detail}")
        elif event.action == "END":
            gui.add_log(f"[{event.turn}] {event.detail}")
        else:
            gui.add_log(detail)

        alive = [c for c in battle_state.player_team + battle_state.enemy_team if c.is_alive()]
        if alive:
            gui.current_time = min(c.action_value for c in alive)
        else:
            gui.current_time = 0.0
        gui.round_end_time = 150.0 if event.turn == 1 else 100.0

        gui.update_characters(battle_state)

        if event.action == "END":
            gui.set_battle_over("Player" if "Victory" in event.detail else "Enemy")
        if event.action == "ROUND_MARKER":
            gui.current_turn = event.turn + 1
            gui.round_end_time = 100.0
            gui.update_characters(battle_state)

    engine.set_logger(log_callback)
    gui.update_characters(battle_state)
    gui.speed_slider.value = 1.0
    gui.current_time = 0.0
    gui.round_end_time = 150.0
    gui.add_log("=== Battle Start - Turn 1 ===")

    last_step_time = 0
    step_interval = 0.5

    running = True
    while running:
        gui.current_speed = gui.speed_slider.value
        step_interval = 0.5 / gui.current_speed

        running = gui.handle_events()

        if not gui.is_battle_over and not gui.is_paused:
            current_time = time.time()
            if current_time - last_step_time >= step_interval:
                last_step_time = current_time

                result = engine._process_single_action()
                if result is None:
                    over, winner = battle_state.is_battle_over()
                    if over:
                        gui.set_battle_over("Player" if winner == "player" else "Enemy")
                else:
                    gui.update_characters(battle_state)
                    if "END" in result.action:
                        gui.set_battle_over("Player" if "Victory" in result.detail else "Enemy")
                    if result.action == "ROUND_MARKER":
                        gui.current_turn = result.turn + 1
                        gui.round_end_time = 100.0

        elif gui.step_requested and not gui.is_battle_over:
            gui.step_requested = False
            result = engine._process_single_action()
            if result is None:
                over, winner = battle_state.is_battle_over()
                if over:
                    gui.set_battle_over("Player" if winner == "player" else "Enemy")
                else:
                    gui.add_log("[DEBUG] Step: result=None but battle not over")
            else:
                gui.update_characters(battle_state)
                if "END" in result.action:
                    gui.set_battle_over("Player" if "Victory" in result.detail else "Enemy")
                if result.action == "ROUND_MARKER":
                    gui.current_turn = result.turn + 1
                    gui.round_end_time = 100.0

        gui.draw()
        gui.clock.tick(FPS)

    pygame.quit()
    return gui


def main():
    from .tui import create_player_team
    from .battle import BattleState, create_enemy
    from .models import Element
    
    player_team = create_player_team()
    
    enemy1 = create_enemy(
        name="Enemy1",
        weakness_elements=[Element.THUNDER, Element.FIRE],
        hp_units=10,
    )
    
    battle_state = BattleState(
        player_team=player_team,
        enemy_team=[enemy1],
        turn=1,
        shared_battle_points=3,
        shared_battle_points_limit=5,
    )
    
    start_gui_battle(battle_state)


if __name__ == "__main__":
    main()
