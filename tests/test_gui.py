"""GUI测试"""
import pytest
from src.game.gui import (
    BattleLogPanel, CharacterPanel, ActionBar, StatDetailPanel, Button
)


class TestBattleLogPanel:
    def test_add_message(self):
        panel = BattleLogPanel(0, 0, 100, 100)
        panel.add_message("Test message 1")
        panel.add_message("Test message 2")
        assert len(panel.messages) == 2
        assert panel.scroll_offset == 0

    def test_scroll_reset_on_new_message(self):
        panel = BattleLogPanel(0, 0, 100, 100)
        panel.scroll_offset = 5
        panel.add_message("New message")
        assert panel.scroll_offset == 0


class TestCharacterPanel:
    def test_set_character(self):
        from src.game.character import create_character_from_preset
        from src.game.models import Element
        
        char = create_character_from_preset("星")
        panel = CharacterPanel(0, 0, 100, 100)
        panel.set_character(char)
        
        assert panel.name == "星"
        assert panel.element == "PHYSICAL"
        assert panel.hp > 0

    def test_handle_click(self):
        panel = CharacterPanel(10, 10, 100, 100)
        assert panel.handle_click((50, 50)) == True
        assert panel.handle_click((200, 200)) == False


class TestButton:
    def test_button_toggle_state(self):
        button = Button(0, 0, 50, 20, "Test", (255, 0, 0))
        assert button.is_toggled == False
        button.is_toggled = True
        assert button.is_toggled == True
        
    def test_button_hover(self):
        button = Button(0, 0, 50, 20, "Test", (255, 0, 0))
        assert button.is_hovered == False


class TestStatDetailPanel:
    def test_show_hide(self):
        panel = StatDetailPanel(0, 0, 100, 100)
        assert panel.visible == False
        
        panel.set_character(None)
        assert panel.visible == True
        
        panel.hide()
        assert panel.visible == False
