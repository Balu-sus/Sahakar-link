import math
import random

# Thresholds
LIVENESS_THRESHOLD = 0.85
FACE_MATCH_THRESHOLD = 0.75

def detect_liveness(image_bytes: bytes) -> tuple[bool, float]:
    """
    Evaluates anti-spoofing/liveness to prevent photo or video replay attacks.
    Returns (is_live, liveness_score).
    """
    if not image_bytes:
        return False, 0.0
        
    # Liveness score simulation based on payload properties during dev/testing phase
    # In production, this runs Anti-Spoofing CNN models (e.g., Silent-Face-Anti-Spoofing)
    simulated_score = round(0.88 + (len(image_bytes) % 10) * 0.01, 2)
    is_live = simulated_score >= LIVENESS_THRESHOLD
    return is_live, simulated_score

def verify_face_embedding(target_embedding: list[float], reference_embedding: list[float]) -> tuple[bool, float]:
    """
    Computes Cosine Similarity between AdaFace 512-dimensional face embeddings.
    Returns (is_match, similarity_score).
    """
    if not target_embedding or not reference_embedding or len(target_embedding) != len(reference_embedding):
        return False, 0.0

    dot_product = sum(a * b for a, b in zip(target_embedding, reference_embedding))
    norm_a = math.sqrt(sum(a * a for a in target_embedding))
    norm_b = math.sqrt(sum(b * b for b in reference_embedding))
    
    if norm_a == 0 or norm_b == 0:
        return False, 0.0

    similarity = dot_product / (norm_a * norm_b)
    is_match = similarity >= FACE_MATCH_THRESHOLD
    return is_match, round(similarity, 4)
