LOCKED = "locked"
AVAILABLE = "available"
IN_PROGRESS = "in_progress"
COMPLETED = "completed"


class MissionAccessPolicy:
    def can_play(self, order_index: int, completed_orders: set[int]) -> bool:
        if order_index <= 1:
            return True
        return (order_index - 1) in completed_orders


def resolve_status(
    order_index: int,
    status: str | None,
    attempts_count: int,
    completed_orders: set[int],
    policy: MissionAccessPolicy | None = None,
) -> str:
    access = policy or MissionAccessPolicy()
    if status == COMPLETED:
        return COMPLETED
    if not access.can_play(order_index, completed_orders):
        return LOCKED
    if status == IN_PROGRESS or attempts_count > 0:
        return IN_PROGRESS
    return AVAILABLE


def recommend_mission(missions: list):
    ordered = sorted(missions, key=lambda item: item.order_index)
    for item in ordered:
        if item.status == IN_PROGRESS:
            return item
    for item in ordered:
        if item.status == AVAILABLE:
            return item
    return None
