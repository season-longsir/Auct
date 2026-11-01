"""建筑数据模型：只保存类型、网格位置、尺寸和基础属性，不负责绘制。"""

from dataclasses import dataclass

from constants import BUILDING_SIZES, CCC, DEC, GM, OB, PG, RB, RFG, TREE


@dataclass
class Building:
    """已放置或待预览的建筑数据。"""

    type: int
    grid_x: int
    grid_y: int
    width: int
    height: int
    health: float = 100.0
    level: int = 1
    subtype: int | None = None

    @property
    def grid_position(self) -> tuple[int, int]:
        """建筑占地左上角的网格坐标。"""
        return self.grid_x, self.grid_y

    @classmethod
    def for_type(
        cls,
        building_type: int,
        grid_x: int = 0,
        grid_y: int = 0,
        health: float = 100.0,
        level: int = 1,
    ) -> "Building":
        """依据建筑类型常量创建数据实例。扩展阶段可在此添加属性/子类。"""
        width, height = BUILDING_SIZES[building_type]
        if building_type not in BUILDING_SIZES:
            raise ValueError(f"不支持的建筑类型: {building_type}")

        return cls(
            type=building_type,
            grid_x=grid_x,
            grid_y=grid_y,
            width=width,
            height=height,
            health=health,
            level=level,
            subtype=building_type,
        )

    @property
    def category(self) -> int:
        """建筑大类，具体可放置类型始终保存在type中。"""
        if self.type == CCC:
            return CCC
        if self.type == RFG:
            return OB
        if self.type in (PG, GM):
            return RB
        if self.type == TREE:
            return DEC
        raise ValueError(f"不支持的建筑类型: {self.type}")


# 下一阶段扩展点：建筑占地冲突、不可建造地块、升级和建筑专属属性。
