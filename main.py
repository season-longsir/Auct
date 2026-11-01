"""Auct 科幻策略塔防游戏主菜单。"""

import sys

import pygame

from constants import (
    BUTTON_CENTER_X,
    BUTTON_FONT_SIZE,
    BUTTON_GAP,
    BUTTON_HEIGHT,
    BUTTON_LABELS,
    BUTTON_TOP,
    BUTTON_WIDTH,
    COLOR_ACCENT,
    COLOR_BACKGROUND_BOTTOM,
    COLOR_BACKGROUND_TOP,
    COLOR_BUTTON,
    COLOR_BUTTON_BORDER,
    COLOR_BUTTON_BORDER_HOVER,
    COLOR_BUTTON_HOVER,
    COLOR_PANEL,
    COLOR_PANEL_BORDER,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    CURSOR_TOGGLE_KEY,
    FONT_TITLE,
    FONT_UI,
    FPS,
    SCREEN_SIZE,
    SUBTITLE_FONT_SIZE,
    TITLE_FONT_SIZE,
    WINDOW_TITLE,
)


# 初始化区：pygame、窗口、字体与主菜单控件
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()

# 选择系统内置字体，避免依赖随项目分发的字体资源。
title_font = pygame.font.SysFont(FONT_TITLE, TITLE_FONT_SIZE, bold=True)
subtitle_font = pygame.font.SysFont(FONT_UI, SUBTITLE_FONT_SIZE)
button_font = pygame.font.SysFont(FONT_UI, BUTTON_FONT_SIZE)
small_font = pygame.font.SysFont(FONT_UI, 15)

buttons = [
    pygame.Rect(
        BUTTON_CENTER_X - BUTTON_WIDTH // 2,
        BUTTON_TOP + index * (BUTTON_HEIGHT + BUTTON_GAP),
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    for index in range(len(BUTTON_LABELS))
]
cursor_visible = True
cursor_toggle_key = pygame.key.key_code(CURSOR_TOGGLE_KEY)


def start_game():
    """开始游戏的预留接口：后续可在此切换到基地编辑界面。"""
    print("开始游戏：基地编辑界面尚未接入。")


def open_settings():
    """设置界面的预留接口。"""
    print("设置界面尚未接入。")


def open_help():
    """帮助界面的预留接口。"""
    print("帮助界面尚未接入。")


def draw_background(target):
    """使用pygame原生绘制低调的纵向深蓝渐变背景。"""
    width, height = SCREEN_SIZE
    for y in range(height):
        blend = y / max(1, height - 1)
        color = tuple(
            round(top + (bottom - top) * blend)
            for top, bottom in zip(COLOR_BACKGROUND_TOP, COLOR_BACKGROUND_BOTTOM)
        )
        pygame.draw.line(target, color, (0, y), (width, y))

    # 轻量科技装饰线与底部状态栏
    pygame.draw.line(target, (30, 55, 74), (0, 112), (width, 112), 1)
    pygame.draw.line(target, (30, 55, 74), (0, height - 46), (width, height - 46), 1)
    pygame.draw.line(target, COLOR_ACCENT, (72, 111), (184, 111), 2)
    pygame.draw.line(target, COLOR_ACCENT, (width - 184, 111), (width - 72, 111), 2)


def draw_menu(target):
    """绘制标题、按钮和辅助信息。"""
    draw_background(target)

    title = title_font.render("Auct", True, COLOR_TEXT)
    target.blit(title, title.get_rect(center=(BUTTON_CENTER_X, 156)))

    subtitle = subtitle_font.render("嗷呜之战", True, COLOR_TEXT_MUTED)
    target.blit(subtitle, subtitle.get_rect(center=(BUTTON_CENTER_X, 219)))

    pygame.draw.rect(target, COLOR_PANEL, (BUTTON_CENTER_X - 220, 265, 440, 1))
    pygame.draw.rect(target, COLOR_PANEL_BORDER, (BUTTON_CENTER_X - 220, 264, 440, 1))

    mouse_position = pygame.mouse.get_pos()
    for label, rect in zip(BUTTON_LABELS, buttons):
        hovered = rect.collidepoint(mouse_position)
        fill = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        border = COLOR_BUTTON_BORDER_HOVER if hovered else COLOR_BUTTON_BORDER
        pygame.draw.rect(target, fill, rect, border_radius=8)
        pygame.draw.rect(target, border, rect, width=2, border_radius=8)
        text = button_font.render(label, True, COLOR_TEXT)
        target.blit(text, text.get_rect(center=rect.center))
        if hovered:
            pygame.draw.rect(target, COLOR_ACCENT, (rect.left + 1, rect.top + 10, 3, rect.height - 20))

    hint = small_font.render(
        f"CURSOR  [{CURSOR_TOGGLE_KEY.upper()}]  {'ON' if cursor_visible else 'OFF'}",
        True,
        COLOR_TEXT_MUTED,
    )
    target.blit(hint, (24, SCREEN_SIZE[1] - 33))
    footer = small_font.render("AUCT // COMMAND INTERFACE", True, COLOR_TEXT_MUTED)
    target.blit(footer, footer.get_rect(bottomright=(SCREEN_SIZE[0] - 24, SCREEN_SIZE[1] - 17)))


def handle_button_click(index):
    """将菜单点击派发至对应的预留功能。"""
    actions = (start_game, open_settings, open_help, pygame.quit)
    if index == 3:
        actions[index]()
        sys.exit()
    actions[index]()


# 主循环区：处理退出、光标开关和按钮鼠标交互，限制为60FPS。
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == cursor_toggle_key:
            cursor_visible = not cursor_visible
            pygame.mouse.set_visible(cursor_visible)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for index, rect in enumerate(buttons):
                if rect.collidepoint(event.pos):
                    handle_button_click(index)
                    break

    draw_menu(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
