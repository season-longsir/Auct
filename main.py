"""Auct 主菜单与基地编辑页面入口。"""

import sys

import pygame

from building import Building
from constants import (
    BUILDING_NAMES,
    BACK_BUTTON_RECT,
    BASE_CELL_SIZE,
    BASE_GRID_COLUMNS,
    BASE_GRID_ORIGIN,
    BASE_GRID_ROWS,
    BUILDING_COLOR,
    BUILDING_HEALTH,
    BUILDING_INVALID_COLOR,
    BUILDING_PREVIEW_ALPHA,
    BUILDING_TYPES,
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
    EDIT_OPTION_GAP,
    EDIT_OPTION_HEIGHT,
    EDIT_PANEL_HEIGHT,
    EDIT_PANEL_PADDING,
    EDIT_PANEL_WIDTH,
    EDIT_PANEL_X,
    EDIT_PANEL_Y,
    FONT_TITLE,
    FONT_UI,
    FPS,
    GRID_AREA_COLOR,
    GRID_CELL_HOVER_COLOR,
    GRID_LINE_COLOR,
    SCREEN_SIZE,
    STATE_EDIT_BASE,
    STATE_MENU,
    SUBTITLE_FONT_SIZE,
    TITLE_FONT_SIZE,
    WINDOW_TITLE,
)


# 初始化区：pygame、窗口、字体和状态机数据。
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(WINDOW_TITLE)
clock = pygame.time.Clock()
title_font = pygame.font.SysFont(FONT_TITLE, TITLE_FONT_SIZE, bold=True)
subtitle_font = pygame.font.SysFont(FONT_UI, SUBTITLE_FONT_SIZE)
button_font = pygame.font.SysFont(FONT_UI, BUTTON_FONT_SIZE)
small_font = pygame.font.SysFont(FONT_UI, 16)
menu_buttons = [
    pygame.Rect(
        BUTTON_CENTER_X - BUTTON_WIDTH // 2,
        BUTTON_TOP + index * (BUTTON_HEIGHT + BUTTON_GAP),
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    for index in range(len(BUTTON_LABELS))
]
back_button = pygame.Rect(BACK_BUTTON_RECT)
building_option_rects = [
    pygame.Rect(
        EDIT_PANEL_X + EDIT_PANEL_PADDING,
        EDIT_PANEL_Y + 90 + index * (EDIT_OPTION_HEIGHT + EDIT_OPTION_GAP),
        EDIT_PANEL_WIDTH - EDIT_PANEL_PADDING * 2,
        EDIT_OPTION_HEIGHT,
    )
    for index in range(len(BUILDING_TYPES))
]
state = STATE_MENU
cursor_visible = True
cursor_toggle_key = pygame.key.key_code(CURSOR_TOGGLE_KEY)
placed_buildings: list[Building] = []
selected_building_type: int | None = None
preview_building: Building | None = None


def draw_background(target):
    """使用pygame原生绘制低调的深蓝渐变背景。"""
    width, height = SCREEN_SIZE
    for y in range(height):
        blend = y / max(1, height - 1)
        color = tuple(
            round(top + (bottom - top) * blend)
            for top, bottom in zip(COLOR_BACKGROUND_TOP, COLOR_BACKGROUND_BOTTOM)
        )
        pygame.draw.line(target, color, (0, y), (width, y))
    pygame.draw.line(target, (30, 55, 74), (0, 112), (width, 112), 1)
    pygame.draw.line(target, (30, 55, 74), (0, height - 46), (width, height - 46), 1)


def draw_menu(target):
    """仅负责主菜单渲染。"""
    draw_background(target)
    title = title_font.render("Auct", True, COLOR_TEXT)
    target.blit(title, title.get_rect(center=(BUTTON_CENTER_X, 156)))
    subtitle = subtitle_font.render("嗷呜之战", True, COLOR_TEXT_MUTED)
    target.blit(subtitle, subtitle.get_rect(center=(BUTTON_CENTER_X, 219)))

    mouse_position = pygame.mouse.get_pos()
    for label, rect in zip(BUTTON_LABELS, menu_buttons):
        hovered = rect.collidepoint(mouse_position)
        fill = COLOR_BUTTON_HOVER if hovered else COLOR_BUTTON
        border = COLOR_BUTTON_BORDER_HOVER if hovered else COLOR_BUTTON_BORDER
        pygame.draw.rect(target, fill, rect, border_radius=8)
        pygame.draw.rect(target, border, rect, width=2, border_radius=8)
        text = button_font.render(label, True, COLOR_TEXT)
        target.blit(text, text.get_rect(center=rect.center))

    hint = small_font.render(
        f"CURSOR  [{CURSOR_TOGGLE_KEY.upper()}]  {'ON' if cursor_visible else 'OFF'}",
        True,
        COLOR_TEXT_MUTED,
    )
    target.blit(hint, (24, SCREEN_SIZE[1] - 33))


def grid_pixel_rect(grid_x: int, grid_y: int, width: int, height: int) -> pygame.Rect:
    """将网格坐标与格子尺寸转换成窗口像素矩形。"""
    return pygame.Rect(
        BASE_GRID_ORIGIN[0] + grid_x * BASE_CELL_SIZE,
        BASE_GRID_ORIGIN[1] + grid_y * BASE_CELL_SIZE,
        width * BASE_CELL_SIZE,
        height * BASE_CELL_SIZE,
    )


def mouse_to_grid(position: tuple[int, int]) -> tuple[int, int] | None:
    """将鼠标像素坐标映射到基地网格，网格外返回None。"""
    relative_x = position[0] - BASE_GRID_ORIGIN[0]
    relative_y = position[1] - BASE_GRID_ORIGIN[1]
    grid_x = relative_x // BASE_CELL_SIZE
    grid_y = relative_y // BASE_CELL_SIZE
    if 0 <= grid_x < BASE_GRID_COLUMNS and 0 <= grid_y < BASE_GRID_ROWS:
        return int(grid_x), int(grid_y)
    return None


def building_fits(building: Building) -> bool:
    """检查建筑是否完全位于基地网格范围内。"""
    return (
        building.grid_x >= 0
        and building.grid_y >= 0
        and building.grid_x + building.width <= BASE_GRID_COLUMNS
        and building.grid_y + building.height <= BASE_GRID_ROWS
    )


def draw_building(target, building: Building, alpha: int = 255, valid: bool = True):
    """在主程序中绘制简易原生建筑标记，building.py仅负责数据。"""
    rect = grid_pixel_rect(building.grid_x, building.grid_y, building.width, building.height)
    color = BUILDING_COLOR if valid else BUILDING_INVALID_COLOR
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    shape_rect = surface.get_rect().inflate(-4, -4)
    pygame.draw.rect(surface, (*color, alpha), shape_rect, border_radius=5)
    pygame.draw.rect(
        surface,
        (*COLOR_ACCENT, min(alpha, 200)),
        shape_rect,
        width=2,
        border_radius=5,
    )
    if rect.width >= BASE_CELL_SIZE * 2 and rect.height >= BASE_CELL_SIZE * 2:
        pygame.draw.circle(
            surface,
            (*COLOR_TEXT_MUTED, alpha),
            surface.get_rect().center,
            max(3, BASE_CELL_SIZE // 6),
            1,
        )
    target.blit(surface, rect.topleft)


def draw_base_grid(target):
    """绘制基地地块、浅灰网格与鼠标所在格子。"""
    grid_rect = pygame.Rect(
        BASE_GRID_ORIGIN[0],
        BASE_GRID_ORIGIN[1],
        BASE_GRID_COLUMNS * BASE_CELL_SIZE,
        BASE_GRID_ROWS * BASE_CELL_SIZE,
    )
    pygame.draw.rect(target, GRID_AREA_COLOR, grid_rect)
    grid_position = mouse_to_grid(pygame.mouse.get_pos())
    if grid_position is not None:
        hovered = grid_pixel_rect(grid_position[0], grid_position[1], 1, 1)
        pygame.draw.rect(target, GRID_CELL_HOVER_COLOR, hovered)

    for column in range(BASE_GRID_COLUMNS + 1):
        x = BASE_GRID_ORIGIN[0] + column * BASE_CELL_SIZE
        pygame.draw.line(target, GRID_LINE_COLOR, (x, grid_rect.top), (x, grid_rect.bottom), 1)
    for row in range(BASE_GRID_ROWS + 1):
        y = BASE_GRID_ORIGIN[1] + row * BASE_CELL_SIZE
        pygame.draw.line(target, GRID_LINE_COLOR, (grid_rect.left, y), (grid_rect.right, y), 1)
    pygame.draw.rect(target, COLOR_PANEL_BORDER, grid_rect, 2)


def draw_edit_base(target):
    """仅负责基地编辑页面渲染。"""
    draw_background(target)
    header = subtitle_font.render("基地编辑 // BASE CONSTRUCTION", True, COLOR_TEXT)
    target.blit(header, (EDIT_PANEL_X, 38))

    panel = pygame.Rect(EDIT_PANEL_X, EDIT_PANEL_Y, EDIT_PANEL_WIDTH, EDIT_PANEL_HEIGHT)
    pygame.draw.rect(target, COLOR_PANEL, panel, border_radius=10)
    pygame.draw.rect(target, COLOR_PANEL_BORDER, panel, 2, border_radius=10)
    panel_title = button_font.render("建筑列表", True, COLOR_TEXT)
    target.blit(panel_title, (panel.x + EDIT_PANEL_PADDING, panel.y + 22))
    pygame.draw.line(
        target,
        COLOR_PANEL_BORDER,
        (panel.x + EDIT_PANEL_PADDING, panel.y + 68),
        (panel.right - EDIT_PANEL_PADDING, panel.y + 68),
        1,
    )

    mouse_position = pygame.mouse.get_pos()
    for building_type, rect in zip(BUILDING_TYPES, building_option_rects):
        selected = building_type == selected_building_type
        hovered = rect.collidepoint(mouse_position)
        fill = COLOR_BUTTON_HOVER if selected or hovered else COLOR_BUTTON
        border = COLOR_BUTTON_BORDER_HOVER if selected else COLOR_BUTTON_BORDER
        pygame.draw.rect(target, fill, rect, border_radius=6)
        pygame.draw.rect(target, border, rect, 2 if selected else 1, border_radius=6)
        label = button_font.render(BUILDING_NAMES[building_type], True, COLOR_TEXT)
        target.blit(label, (rect.x + 12, rect.y + 9))

    draw_base_grid(target)
    for building in placed_buildings:
        draw_building(target, building)

    if preview_building is not None:
        draw_building(
            target,
            preview_building,
            alpha=BUILDING_PREVIEW_ALPHA,
            valid=building_fits(preview_building),
        )

    back_hovered = back_button.collidepoint(mouse_position)
    back_fill = COLOR_BUTTON_HOVER if back_hovered else COLOR_BUTTON
    pygame.draw.rect(target, back_fill, back_button, border_radius=8)
    pygame.draw.rect(
        target,
        COLOR_BUTTON_BORDER_HOVER if back_hovered else COLOR_BUTTON_BORDER,
        back_button,
        2,
        border_radius=8,
    )
    back_text = small_font.render("返回主菜单", True, COLOR_TEXT)
    target.blit(back_text, back_text.get_rect(center=back_button.center))

    help_text = small_font.render("左键放置   右键取消选择", True, COLOR_TEXT_MUTED)
    target.blit(help_text, (BASE_GRID_ORIGIN[0], BASE_GRID_ORIGIN[1] + BASE_GRID_ROWS * BASE_CELL_SIZE + 12))


def update_preview(mouse_position: tuple[int, int]):
    """随鼠标更新当前待放置建筑虚影。"""
    global preview_building
    if selected_building_type is None:
        preview_building = None
        return
    grid_position = mouse_to_grid(mouse_position)
    if grid_position is None:
        preview_building = None
        return
    preview_building = Building.for_type(
        selected_building_type,
        grid_x=grid_position[0],
        grid_y=grid_position[1],
        health=BUILDING_HEALTH[selected_building_type],
    )


def handle_menu_event(event):
    """主菜单状态事件处理；开始游戏切换至基地编辑状态。"""
    global state
    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return
    for index, rect in enumerate(menu_buttons):
        if rect.collidepoint(event.pos):
            if index == 0:
                state = STATE_EDIT_BASE
                return
            if index == 1:
                print("设置界面尚未接入。")
            elif index == 2:
                print("帮助界面尚未接入。")
            elif index == 3:
                pygame.quit()
                sys.exit()


def handle_edit_base_event(event):
    """基地编辑状态事件处理：选取、预览、放置、取消与返回。"""
    global state, selected_building_type, preview_building
    if event.type == pygame.MOUSEMOTION:
        update_preview(event.pos)
        return
    if event.type != pygame.MOUSEBUTTONDOWN:
        return

    if event.button == 3:
        selected_building_type = None
        preview_building = None
        return

    if event.button != 1:
        return
    if back_button.collidepoint(event.pos):
        state = STATE_MENU
        selected_building_type = None
        preview_building = None
        return

    for building_type, rect in zip(BUILDING_TYPES, building_option_rects):
        if rect.collidepoint(event.pos):
            selected_building_type = building_type
            update_preview(pygame.mouse.get_pos())
            return

    update_preview(event.pos)
    if preview_building is not None and building_fits(preview_building):
        # 当前阶段只做范围内放置；下一阶段加入占地冲突与建造规则校验。
        placed_buildings.append(preview_building)
        update_preview(event.pos)


# 状态机主循环：各状态分别调用自己的事件处理与渲染函数。
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == cursor_toggle_key:
            cursor_visible = not cursor_visible
            pygame.mouse.set_visible(cursor_visible)
        elif state == STATE_MENU:
            handle_menu_event(event)
        elif state == STATE_EDIT_BASE:
            handle_edit_base_event(event)

    if state == STATE_MENU:
        draw_menu(screen)
    elif state == STATE_EDIT_BASE:
        update_preview(pygame.mouse.get_pos())
        draw_edit_base(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
