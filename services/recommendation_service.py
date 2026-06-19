"""
services/recommendation_service.py
────────────────────────────────────
ML + Heuristic hybrid recommendation engine.
Aligned with the clean dataset (generate_clean_dataset.py) and ForYou.jsx.
"""
import logging
import random
import pandas as pd
from sqlalchemy.orm import Session

import db.crud as crud
import db.schemas as schemas

logger = logging.getLogger(__name__)

# ─── EXACT MAPPINGS matching ForYou.jsx ───────────────────────────────────────
INTERET_TYPE_BONUS = {
    'Culture & Patrimoine':   ['Ville'],
    'Nature & Paysages':      ['Montagne', 'Plage'],
    'Plage & Détente':        ['Plage'],
    'Aventure & Désert':      ['Désert', 'Montagne'],
    'Gastronomie & Shopping': ['Ville'],
    'Sports & Loisirs':       ['Montagne', 'Plage', 'Désert', 'Ville'],
}

INTERET_TYPE_PENALTY = {
    'Culture & Patrimoine':   ['Désert'],
    'Nature & Paysages':      ['Ville'],
    'Plage & Détente':        ['Désert', 'Montagne'],
    'Aventure & Désert':      ['Ville'],
    'Gastronomie & Shopping': ['Désert', 'Montagne'],
    'Sports & Loisirs':       [],
}

CLIMAT_TYPE_BONUS = {
    'Chaud':      ['Plage', 'Désert'],
    'Désertique': ['Désert'],
    'Froid':      ['Montagne'],
    'Tempéré':    ['Ville', 'Montagne', 'Plage'],
}

SAISON_CLIMAT_MATCH = {
    ('Été', 'Chaud'):           10,
    ('Hiver', 'Froid'):         10,
    ('Hiver', 'Désertique'):    10,
    ('Automne', 'Désertique'):  10,
    ('Printemps', 'Tempéré'):   10,
    ('Automne', 'Tempéré'):     10,
    ('Printemps', 'Chaud'):      5,
}


def calculate_relevance_score(rec: schemas.RecommendationRequest, dest) -> float:
    """
    Computes a heuristic relevance score for a destination given user preferences.
    Scores are additive; higher = better match.
    """
    score = 0.0
    dt = dest.destination_type or ''  # Ville | Plage | Montagne | Désert

    # ── 1. Explicit hard filters (applied before this function is called,
    #       but we reinforce here with large bonuses/penalties) ─────────────────
    if rec.Type_Destination and rec.Type_Destination not in ('Mixte', ''):
        score += 60 if dt == rec.Type_Destination else -60

    if rec.Region and rec.Region not in ('Toutes', ''):
        score += 50 if rec.Region.lower() == (dest.continent or '').lower() else -50

    # ── 2. Intérêt → Type alignment ──────────────────────────────────────────
    bonus_types   = INTERET_TYPE_BONUS.get(rec.Interet, [])
    penalty_types = INTERET_TYPE_PENALTY.get(rec.Interet, [])
    if dt in bonus_types:
        score += 40
    elif dt in penalty_types:
        score -= 30

    # ── 3. Climat → Type alignment ────────────────────────────────────────────
    bonus_climate_types = CLIMAT_TYPE_BONUS.get(rec.Climat, [])
    if dt in bonus_climate_types:
        score += 20

    # ── 4. Saison + Climat coherence ─────────────────────────────────────────
    score += SAISON_CLIMAT_MATCH.get((rec.Saison, rec.Climat), 0)

    # ── 5. Budget fit ─────────────────────────────────────────────────────────
    est_daily  = (dest.cost_of_living or 2.0) * 350
    user_daily = rec.Budget / max(rec.Duree, 1)
    if user_daily >= est_daily * 1.4:
        score += 20   # Confortable budget
    elif user_daily >= est_daily * 0.75:
        score += 10   # Correct budget
    elif user_daily < est_daily * 0.4:
        score -= 25   # Budget too tight

    return score


def get_prediction(app_state, rec_request: schemas.RecommendationRequest, db: Session) -> str:
    """
    Hybrid ML + Heuristic recommendation:
    1. Apply hard user filters (Region, Type_Destination) to the destination pool.
    2. ML model scores all destinations by probability.
    3. Heuristic re-scores on top of ML probabilities.
    4. Return the best match.
    """
    all_destinations = crud.get_all_destinations(db)
    if not all_destinations:
        return "Marrakech"

    model         = app_state.model
    preprocessor  = app_state.preprocessor
    label_encoder = app_state.label_encoder
    zone_model    = getattr(app_state, "zone_model", None)
    zone_encoder  = getattr(app_state, "zone_encoder", None)

    # ── STEP 1: Hard Filters ────────────────────────────────────────────
    valid_dests = list(all_destinations)

    if rec_request.Region and rec_request.Region not in ('Toutes', ''):
        region_filtered = [d for d in valid_dests
                           if (d.continent or '').lower() == rec_request.Region.lower()]
        if region_filtered:
            valid_dests = region_filtered

    if rec_request.Type_Destination and rec_request.Type_Destination not in ('Mixte', ''):
        type_filtered = [d for d in valid_dests
                         if d.destination_type == rec_request.Type_Destination]
        if type_filtered:
            valid_dests = type_filtered

    valid_names = {d.name for d in valid_dests}
    logger.info(f"[FILTER] {len(valid_dests)} destinations after hard filters "
                f"(Region={rec_request.Region}, Type={rec_request.Type_Destination})")

    # ── STEP 2: ML Scoring ───────────────────────────────────────────────
    if model and preprocessor and label_encoder:
        try:
            # Build input DataFrame — exactly matching training feature columns
            input_df = pd.DataFrame([{
                'age':              rec_request.Age,
                'budget':           rec_request.Budget,
                'duree':            rec_request.Duree,
                'interet':          rec_request.Interet,
                'activite':         rec_request.activite,
                'climat':           rec_request.Climat,
                'saison':           rec_request.Saison,
                'region':           rec_request.Region,
                'type_voyage':      rec_request.Type_Voyage,
                'type_destination': rec_request.Type_Destination if rec_request.Type_Destination not in ('Mixte', '') else 'Ville',
            }])

            processed_input = preprocessor.transform(input_df)

            # Zone filtering (Stage 1)
            zone_filtered_names = valid_names
            if zone_model and zone_encoder:
                zone_probs = zone_model.predict_proba(processed_input)[0]
                # Use top-2 zones for more flexibility
                top_zone_idxs = zone_probs.argsort()[::-1][:2]
                top_zones = set(zone_encoder.inverse_transform(top_zone_idxs))
                logger.info(f"[STAGE 1] Top zones: {top_zones}")

                zone_filtered = [d for d in valid_dests
                                 if any(z.lower() in (d.continent or '').lower()
                                        for z in top_zones)]
                if zone_filtered:
                    zone_filtered_names = {d.name for d in zone_filtered}

            # City probabilities (Stage 2)
            probabilities = model.predict_proba(processed_input)[0]
            class_probs = [
                (label_encoder.inverse_transform([i])[0], prob)
                for i, prob in enumerate(probabilities)
            ]
            class_probs.sort(key=lambda x: x[1], reverse=True)

            # ── STEP 3: Hybrid Scoring ────────────────────────────────────────────────
            scored = []
            for dest_name, prob in class_probs[:100]:  # Top 100 by ML prob
                if dest_name not in zone_filtered_names:
                    continue
                dest_obj = next((d for d in valid_dests if d.name == dest_name), None)
                if not dest_obj:
                    continue
                heuristic = calculate_relevance_score(rec_request, dest_obj)
                # ML probability scaled 0→100, plus heuristic bonus/penalty
                final_score = (prob * 100) + heuristic
                scored.append({
                    'name':      dest_name,
                    'ml_prob':   prob,
                    'heuristic': heuristic,
                    'score':     final_score,
                })

            if scored:
                scored.sort(key=lambda x: x['score'], reverse=True)
                best = scored[0]
                logger.info(
                    f"[RESULT] {best['name']} | ML={best['ml_prob']*100:.1f}% | "
                    f"Heuristic={best['heuristic']:.0f} | Total={best['score']:.1f}"
                )
                return best['name']

        except Exception as e:
            logger.error(f"ML prediction error: {e}", exc_info=True)

    # ── STEP 4: Pure heuristic fallback ────────────────────────────────────────────────
    logger.warning("Falling back to pure heuristic scoring.")
    scored = []
    for dest in valid_dests:
        scored.append({'name': dest.name, 'score': calculate_relevance_score(rec_request, dest)})
    scored.sort(key=lambda x: x['score'], reverse=True)
    winner = scored[0] if scored else {'name': 'Marrakech'}
    logger.info(f"[FALLBACK] Chosen: {winner['name']} (score={winner['score']:.0f})")
    return winner['name']
