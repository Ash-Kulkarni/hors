def estimate_decimal_odds(
    win_counts: dict[str, int],
    sims: int,
    house_margin=0.10,
    alpha=1.0,
    clamp=(1.05, 50.0),
):
    k = len(win_counts) or 1
    p_fair = {n: (w + alpha) / (sims + alpha * k) for n, w in win_counts.items()}
    z = sum(p_fair.values()) or 1.0
    p_mkt = {n: p * ((1.0 + house_margin) / z) for n, p in p_fair.items()}
    lo, hi = clamp
    return {n: max(min(1 / p, hi), lo) for n, p in p_mkt.items()}
