"""
services/recommendation_service.py
──────────────────────────────────
Contains the Machine Learning logic and the heuristic scoring logic
for the destination recommendation system.
"""
import logging
import random
import pandas as pd
from sqlalchemy.orm import Session

import db.crud as crud
import db.schemas as schemas

logger = logging.getLogger(__name__)


def calculate_relevance_score(rec_request: schemas.RecommendationRequest, destination) -> int:
    """
    Calcule un score de pertinence aligné avec les règles d'entraînement du modèle.
    """
    score = 0
    dest_type = destination.destination_type  # Désert | Montagne | Plage | Ville

    # 1. INTÉRÊT → TYPE DE DESTINATION (±30 points)
    INTERET_RULES = {
        'Culture & Patrimoine':   {'bonus': ['Historique', 'Ville'], 'penalty': ['Désert']},
        'Nature & Paysages':      {'bonus': ['Nature', 'Montagne'],  'penalty': ['Ville']},
        'Plage & Détente':        {'bonus': ['Plage', 'Nature'],     'penalty': ['Désert']},
        'Aventure & Désert':      {'bonus': ['Désert', 'Montagne'],  'penalty': ['Ville']},
        'Gastronomie & Shopping': {'bonus': ['Ville'],               'penalty': ['Désert', 'Montagne']},
        'Sports & Loisirs':       {'bonus': ['Sport', 'Montagne'],   'penalty': []},
    }
    rules = INTERET_RULES.get(rec_request.Interet, {})
    if dest_type in rules.get('bonus', []):
        score += 30
    elif dest_type in rules.get('penalty', []):
        score -= 20

    # 2. CLIMAT & SAISON alignment (±15 points)
    # Simple proxy: Desert is good in Winter/Autumn
    if rec_request.Climat in ['Chaud', 'Désertique'] and dest_type in ['Plage', 'Désert']:
        score += 15

    # 3. BUDGET (±25 points)
    # estimated_daily_cost = destination.cost_of_living * 250
    est_daily = (destination.cost_of_living or 2.5) * 250
    user_daily = rec_request.Budget / max(rec_request.Duree, 1)
    
    if user_daily >= est_daily * 1.5:
        score += 25 # High end traveler
    elif user_daily >= est_daily * 0.8:
        score += 15 # Healthy budget
    elif user_daily < est_daily * 0.5:
        score -= 30 # Insufficient

    # 4. RÉGION (±20 points)
    if rec_request.Region and rec_request.Region != "Toutes":
        # Check if requested region matches destination.continent (stores region name)
        if rec_request.Region.lower() in (destination.continent or "").lower():
            score += 20

    # 5. INTÉRÊT dans la description (±15 points)
    if rec_request.Interet and rec_request.Interet in (destination.description or ""):
         score += 15

    return score


def get_prediction(app_state, rec_request: schemas.RecommendationRequest, db: Session) -> str:
    """
    ML-Driven Recommendation:
    1. ML predicts probabilities for EVERY exact destination (344 classes).
    2. We get the ranked list of destinations from highest probability to lowest.
    3. We apply user's hard filters (Target Type, Target Region) to the DB destinations.
    4. We pick the #1 destination from the ML ranked list that actually exists in the filtered DB list.
    """
    all_destinations = crud.get_all_destinations(db)
    if not all_destinations:
        return "Marrakech"

    model = app_state.model
    preprocessor = app_state.preprocessor
    label_encoder = app_state.label_encoder
    zone_model = getattr(app_state, "zone_model", None)
    zone_encoder = getattr(app_state, "zone_encoder", None)

    # 1. Appliquer les filtres "durs" de l'utilisateur sur la liste des villes possibles
    valid_dests = all_destinations
    
    # Filtre de Région
    if rec_request.Region and rec_request.Region != "Toutes":
        valid_dests = [d for d in valid_dests if (d.continent or "").lower() == rec_request.Region.lower()]
        
    # Filtre de Type de Destination (si précisé et != "Mixte")
    if rec_request.Type_Destination and rec_request.Type_Destination != "Mixte":
        valid_dests = [d for d in valid_dests if d.destination_type == rec_request.Type_Destination]

    # Sécurité : si le filtre est trop strict et qu'aucune ville ne correspond, on annule les filtres
    if not valid_dests:
        logger.warning("Filtres trop stricts, aucune ville trouvée. Annulation des filtres.")
        valid_dests = all_destinations

    valid_names = {d.name for d in valid_dests}

    # 2. Utiliser le modèle ML pour trouver la meilleure ville
    if model and preprocessor and label_encoder:
        try:
            # Data preparation with exactly the same logic as training
            # FeatureCreator in transformers.py will handle the derived features (signature, luxury)
            input_df = pd.DataFrame([{
                'age':              rec_request.Age,
                'budget':           rec_request.Budget,
                'interet':          rec_request.Interet,
                'activite':         rec_request.activite,
                'duree':            rec_request.Duree,
                'climat':           rec_request.Climat,
                'saison':           rec_request.Saison,
                'type_voyage':      rec_request.Type_Voyage,
                'type_destination': rec_request.Type_Destination,
                'region':           rec_request.Region,
            }])
            
            # The preprocessor pipeline includes FeatureCreator which expects these 10 columns
            processed_input = preprocessor.transform(input_df)
            
            forced_valid_names = valid_names
            
            # --- STAGE 1: Prédire la Zone (Région) ---
            if zone_model and zone_encoder:
                zone_probs = zone_model.predict_proba(processed_input)[0]
                best_zone_idx = zone_probs.argmax()
                predicted_zone = zone_encoder.inverse_transform([best_zone_idx])[0]
                logger.info(f"[STAGE 1] Zone Prédite: {predicted_zone} (Confiance: {zone_probs[best_zone_idx]*100:.1f}%)")
                
                # Filtrer les destinations par la zone prédite (continent en base de donnees correspond a zone)
                zone_filtered_dests = [d for d in valid_dests if (d.continent or "").lower() == predicted_zone.lower()]
                if zone_filtered_dests:
                    forced_valid_names = {d.name for d in zone_filtered_dests}
                else:
                    logger.warning(f"Aucune ville en BDD pour la zone {predicted_zone}. On garde toutes les villes.")
            
            # --- STAGE 2: Prédire la Ville ---
            # Obtenir les probabilités (Single-target model returns a single array)
            probabilities = model.predict_proba(processed_input)[0]
            
            # Associer les probabilités aux noms des classes
            class_probs = [
                (label_encoder.inverse_transform([i])[0], prob) 
                for i, prob in enumerate(probabilities)
            ]
            
            # Trier par probabilité décroissante
            class_probs.sort(key=lambda x: x[1], reverse=True)
            
            # 3. Trouver la ville la plus probable qui respecte les filtres de la BDD et le ML Stage 1
            # HYBRID SCORING: On combine la probabilité du ML avec l'heuristique (logique métier)
            scored_dests = []
            for dest_name, prob in class_probs:
                if dest_name in forced_valid_names:
                    dest_obj = next((d for d in valid_dests if d.name == dest_name), None)
                    if dest_obj:
                        heuristic_score = calculate_relevance_score(rec_request, dest_obj)
                        # prob est entre 0 et 1. On le met sur 100, et on ajoute l'heuristique (-50 à +90)
                        final_score = (prob * 100) + heuristic_score
                        scored_dests.append({
                            'name': dest_name, 
                            'prob': prob, 
                            'heuristic': heuristic_score, 
                            'score': final_score
                        })
            
            if scored_dests:
                # Trier par le score hybride final
                scored_dests.sort(key=lambda x: x['score'], reverse=True)
                best_match = scored_dests[0]
                logger.info(f"[HYBRID RESULT] Choisi: {best_match['name']} (ML Confiance: {best_match['prob']*100:.1f}%, Bonus Logique: {best_match['heuristic']})")
                return best_match['name']
                    
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")

    # 4. Fallback si le ML échoue (utilise l'ancienne heuristique simplifiée sur les valid_names)
    logger.warning("Falling back to heuristic scoring.")
    scored = []
    for dest in valid_dests:
        scored.append({'name': dest.name, 'score': calculate_relevance_score(rec_request, dest)})
    
    if not scored:
        return "Marrakech"
        
    scored.sort(key=lambda x: x['score'], reverse=True)
    winner = random.choice(scored[:3])
    logger.info(f"[FALLBACK RESULT] Choisi: {winner['name']}")
    return winner['name']
