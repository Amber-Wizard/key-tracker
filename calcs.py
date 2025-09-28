

def calculate_winrate(wins, games, rounding=2, scale=True, include_font=False, exception='--', p1smooth=False):
    if games == 0:
        if include_font:
            return exception, "plain-italic-font"
        return exception
    else:
        if p1smooth:
            winrate = (1 + wins) / (2 + games)
        else:
            winrate = wins / games

        font_style = "hero-italic-font" if winrate >= 0.5 else "villain-italic-font"

        if scale:
            winrate *= 100
            winrate = round(winrate)
        else:
            winrate = round(winrate, rounding)

        if include_font:
            return winrate, font_style
        return winrate


def subtract_dicts(old_dict, new_dict):
    # Subtract values from the new dict based on the old dict
    result = {}
    for key, value in new_dict.items():
        if key in old_dict:
            difference = value - old_dict[key]
            if difference > 0:
                result[key] = difference
        else:
            result[key] = value
    return result


