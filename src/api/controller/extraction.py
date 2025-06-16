import re
import time
import logging
from collections import Counter
from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

# Configure logging for better visibility during development/testing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Global model instance - using the absolute fastest model
_model = None

def get_model():
    """Load the fastest possible sentence transformer model"""
    global _model
    if _model is None:
        start_time = time.perf_counter()
        # This is the FASTEST model available - 14MB, extremely fast inference
        # Removed 'sentence-transformers/' prefix as it's often redundant for standard models
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        # Force CPU to avoid GPU overhead for small batches
        _model.max_seq_length = 128  # Limit sequence length for speed
        load_time = time.perf_counter() - start_time
        logger.info(f"Ultra-fast model loaded in {load_time:.3f}s")
    return _model

# Pre-compiled regex for speed
# Updated pattern: allow 2-character words if they are all uppercase (e.g., AI, ML, IT)
# or 3+ character words with letters, numbers, hyphens, underscores.
WORD_PATTERN = re.compile(r'\b(?:[A-Z]{2,}|[a-zA-Z][a-zA-Z0-9_-]{2,})\b')

# Minimal stop words for maximum speed
STOP_WORDS = frozenset([
    'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 
    'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 
    'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'will',
    'have', 'been', 'that', 'this', 'they', 'what', 'with', 'were', 'your', 'from', 'some',
    'come', 'them', 'said', 'very', 'well', 'just', 'like', 'good', 'much', 'more', 'want',
    'than', 'make', 'know', 'time', 'only', 'look', 'take', 'work', 'find', 'here', 'when',
    # Added common search stop words that might incorrectly be extracted
    'which', 'about', 'such', 'into', 'over', 'under', 'also', 'where', 'then', 'there',
    'would', 'could', 'should', 'must', 'might', 'must', 'even', 'every', 'always' ,"search" , "search:" , "search :"
])

def lightning_candidates(text: str, max_candidates: int = 30) -> List[str]:
    """
    Ultra-fast candidate extraction with improved handling for acronyms and phrases.
    Target under 10ms.
    """
    original_words = WORD_PATTERN.findall(text.lower())
    
    # Filter words and count frequency for potential candidates
    candidate_freq = Counter()
    for word in original_words:
        # Include words if they are not stop words AND
        # (they are long enough OR they are short and all uppercase - like 'AI', 'ML')
        if (word not in STOP_WORDS and len(word) > 2) or (word.isupper() and len(word) >= 2):
            candidate_freq[word] += 1
    
    candidates = []
    # Add top single words based on frequency
    candidates.extend([w for w, _ in candidate_freq.most_common(min(15, max_candidates))])
    
    # Generate strategic bigrams.
    # We iterate over a limited number of original words to keep it fast,
    # but still try to capture relevant phrases.
    
    # Use the original (unfiltered) words to generate bigrams, but then check if
    # the component words are potential candidates (i.e., not stop words, and pass length/acronym check)
    bigrams = Counter()
    
    # Iterate over a slightly larger portion of the text for bigrams, if available
    # to capture phrases that might not be in the very first few words.
    words_for_bigrams = original_words[:min(len(original_words), 50)] 
    
    for i in range(len(words_for_bigrams) - 1):
        w1, w2 = words_for_bigrams[i], words_for_bigrams[i+1]
        
        # Check if both words are "meaningful" (not stop words or common fillers)
        # Use lower() for comparison with STOP_WORDS
        is_w1_meaningful = (w1 not in STOP_WORDS and len(w1) > 2) or (w1.isupper() and len(w1) >= 2)
        is_w2_meaningful = (w2 not in STOP_WORDS and len(w2) > 2) or (w2.isupper() and len(w2) >= 2)
        
        if is_w1_meaningful and is_w2_meaningful:
            bigram = f"{w1} {w2}"
            bigrams[bigram] += 1

    # Add top bigrams (e.g., up to 10-15 bigrams if candidates allow)
    # Prioritize bigrams that appear more frequently
    candidates.extend([b for b, _ in bigrams.most_common(min(15, max_candidates - len(candidates)))])
    
    # Deduplicate and limit to max_candidates
    final_candidates = list(dict.fromkeys(candidates))[:max_candidates]
    
    return final_candidates

def ultra_fast_similarity(text: str, candidates: List[str], max_keywords: int = 20) -> List[str]:
    """
    Ultra-optimized model inference - target under 200ms.
    Improved scoring for better accuracy.
    """
    if not candidates:
        return []
    
    start_time = time.perf_counter()
    
    try:
        model = get_model()
        
        # Truncate text for speed (keep most relevant part)
        # For general keyword extraction from a query, the whole query is usually relevant.
        # But for longer document snippets, this helps.
        text_for_embedding = text[:200] if len(text) > 200 else text
        
        encode_start = time.perf_counter()
        
        # Single batch encoding - most efficient
        all_texts = [text_for_embedding] + candidates
        embeddings = model.encode(all_texts, 
                                show_progress_bar=False,
                                batch_size=32,  # Optimal batch size
                                normalize_embeddings=True)  # Pre-normalize for speed
        
        encode_time = time.perf_counter() - encode_start
        
        # Lightning-fast similarity (pre-normalized, so just dot product)
        text_emb = embeddings[0:1]
        candidate_embs = embeddings[1:]
        
        # Vectorized dot product (faster than cosine_similarity)
        similarities = np.dot(candidate_embs, text_emb.T).flatten()
        
        # Quick scoring with minimal overhead and improved bonuses
        scored: List[Tuple[str, float]] = []
        text_lower = text.lower() # Pre-compute for fast substring check
        
        for i, candidate in enumerate(candidates):
            score = similarities[i]
            
            # --- Improved Scoring Bonuses ---
            # 1. Exact match bonus: High bonus if the candidate is an exact substring of the original text
            # This is crucial for multi-word terms like "AI lesson"
            if candidate.lower() in text_lower:
                score *= 1.5 # Strong bonus for direct presence

            # 2. Bigram bonus (still useful for multi-word phrases even if not exact substring match)
            elif ' ' in candidate: 
                score *= 1.2 
            
            # 3. Acronym bonus: Give a small boost to all-uppercase candidates
            if candidate.isupper() and len(candidate) >= 2:
                score *= 1.1

            # Removed the `len(candidate) > 6` bonus as it can penalize important short terms (like 'AI')
            
            scored.append((candidate, score))
        
        # Fast sort and return
        scored.sort(key=lambda x: x[1], reverse=True)
        result = [candidate for candidate, _ in scored[:max_keywords]]
        
        total_time = time.perf_counter() - start_time
        logger.debug(f"Ultra-fast model inference: {total_time:.3f}s ({encode_time:.3f}s encoding)")
        
        return result
        
    except Exception as e:
        # Ultra-fast fallback: If model fails, return empty list to indicate no keywords found via model.
        # This is safer than falling back to frequency, which might not be relevant if similarity failed.
        logger.warning(f"Model failed during similarity calculation: {e}. Returning empty list.")
        return []

def extract_keywords(text: str, max_keywords: int = 8, previous_context: str = "", context_weight: float = 0.3) -> str:
    """
    Lightning-fast keyword extraction with model - target under 300ms total
    """
    overall_start = time.perf_counter()
    
    if not text.strip():
        return ""
    
    # Fast context check (heuristic, might need fine-tuning based on actual use-cases)
    # Added more triggers that suggest a need for context
    needs_context_triggers = [
        'there', 'that', 'those', 'them', 'it', 'this', 'these', 'place',
        'same', 'similar', 'related', 'mentioned', 'above', 'previous',
        'referring', 'about it', 'what about', 'on that', 'in relation to'
    ]
    needs_context = any(trigger in text.lower() for trigger in needs_context_triggers)
    
    # Increased max_candidates slightly for more options for the model
    DEFAULT_MAX_CANDIDATES = 35 
    
    if previous_context and needs_context and context_weight > 0:
        # Lightning context processing
        context_keywords_count = max(1, int(max_keywords * context_weight))
        main_keywords_count = max_keywords - context_keywords_count
        
        # Adjust candidate counts based on keyword counts
        main_candidates_count = min(DEFAULT_MAX_CANDIDATES, max_keywords * 3) # Give more main candidates
        context_candidates_count = min(DEFAULT_MAX_CANDIDATES // 2, context_keywords_count * 2) # Fewer context candidates
        
        # Parallel candidate extraction
        main_candidates = lightning_candidates(text, main_candidates_count)
        context_candidates = lightning_candidates(previous_context, context_candidates_count)
        
        # Fast model scoring
        main_result = ultra_fast_similarity(text, main_candidates, main_keywords_count)
        context_result = ultra_fast_similarity(previous_context, context_candidates, context_keywords_count)
        
        # Merge results, prioritize main results
        final_keywords = main_result + [kw for kw in context_result if kw not in main_result]
        final_keywords = list(dict.fromkeys(final_keywords))[:max_keywords]  # Dedupe and limit
        
    else:
        # Single text processing
        candidates = lightning_candidates(text, DEFAULT_MAX_CANDIDATES)
        final_keywords = ultra_fast_similarity(text, candidates, max_keywords)
    
    total_time = time.perf_counter() - overall_start
    result = ' '.join(final_keywords)
    
    logger.info(f"Lightning extraction: {total_time:.3f}s -> '{result}'")
    
    return result

def smart_message_processing(validated_messages: List) -> tuple[str, str]:
    """
    Ultra-fast message processing - under 5ms
    """
    if not validated_messages:
        return "", ""
    
    if len(validated_messages) <= 1:
        current_query = validated_messages[0].content if validated_messages else ""
        return current_query, ""
    
    # Lightning-fast processing
    current_query = validated_messages[-1].content
    
    # Get only user messages, limit to last 2 for speed
    user_messages = []
    # Iterate backwards from the second-to-last message
    for msg in reversed(validated_messages[:-1]):
        if msg.role == 'user':
            user_messages.append(msg.content)
            # Limit to 2 previous user messages for context
            if len(user_messages) >= 2:
                break
    
    # Join in chronological order (oldest first)
    recent_context = " ".join(reversed(user_messages)) if user_messages else ""
    
    return current_query, recent_context

# Alternative: If you need even faster, use this CPU-optimized version
# Note: For accuracy, 'all-MiniLM-L6-v2' is already quite small and fast.
# Reducing max_seq_length too much (e.g., to 64) can hurt performance for longer phrases.
def get_cpu_optimized_model():
    """Alternative ultra-fast CPU model"""
    global _model
    if _model is None:
        # Even smaller model - 5MB only - but potentially less accurate than MiniLM-L6-v2
        # 'all-MiniLM-L6-v2' is generally the sweet spot for speed/accuracy.
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu') 
        # Keep max_seq_length reasonable. 128 is a good balance.
        # _model.max_seq_length = 64  # Use with caution: can reduce accuracy for longer phrases
        # Optimize for CPU
        import torch
        # torch.set_num_threads(1)  # Good for very small batch sizes, but can be slower for 32 batch size.
                                  # Let PyTorch manage threads unless experiencing specific issues.
    return _model

