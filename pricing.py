def estimate_all_odds(
    horses, total_wins, sims, house_margin=0.10, alpha=1.0, clamp=(1.05, 50.0)
):
    # Laplace-smoothed fair probabilities
    k = len(horses)
    wins = {h.name: total_wins.get(h.name, 0) for h in horses}
    p_fair = {n: (w + alpha) / (sims + alpha * k) for n, w in wins.items()}
    # Overround to include the house margin
    z = sum(p_fair.values())
    p_mkt = {n: p * ((1.0 + house_margin) / z) for n, p in p_fair.items()}
    # Decimal odds, clamped for UX
    min_o, max_o = clamp
    return {n: max(min(1 / p, max_o), min_o) for n, p in p_mkt.items()}
