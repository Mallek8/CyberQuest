XP_PER_LEVEL = 150


def level_for_xp(xp: int) -> int:
    if xp < 0:
        return 1
    return 1 + (xp // XP_PER_LEVEL)


def xp_into_level(xp: int) -> int:
    if xp < 0:
        return 0
    return xp % XP_PER_LEVEL


def potential_xp(xp_reward: int, score: int, max_score: int) -> int:
    if max_score <= 0:
        return 0
    return (xp_reward * score) // max_score
