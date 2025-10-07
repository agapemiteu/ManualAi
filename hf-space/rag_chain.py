from typing import Any, Dict, List, Optional, Set, Tuple
import re
import os

FALLBACK_MESSAGE = "I don't have that information in this manual. Could you rephrase your question or ask about something else?"

# LLM Configuration - Upgraded to Llama 3.1 8B for better intelligence!
USE_LLM = os.getenv("MANUAL_USE_LLM", "true").lower() == "true"
LLM_API_URL = os.getenv("MANUAL_LLM_API_URL", "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-8B-Instruct")
LLM_API_KEY = os.getenv("HUGGINGFACE_TOKEN", os.getenv("HF_TOKEN", ""))

# Common stop words to filter out for better keyword extraction
STOP_WORDS = {
    "the", "is", "at", "which", "on", "a", "an", "as", "are", "was", "were",
    "been", "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "should", "could", "may", "might", "must", "can", "this", "that", "these",
    "those", "i", "you", "he", "she", "it", "we", "they", "what", "when",
    "where", "why", "how", "my", "your", "his", "her", "its", "our", "their",
    "about", "into", "through", "during", "before", "after", "above", "below",
    "to", "from", "up", "down", "in", "out", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "all", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "but", "for", "with", "by"
}


class SimpleResponse:
    def __init__(self, content: str):
        self.content = content


class ConversationMemory:
    """Simple conversation memory to understand context across messages"""
    def __init__(self, max_history: int = 3):
        self.history: List[Tuple[str, str]] = []  # (question, answer)
        self.max_history = max_history
    
    def add(self, question: str, answer: str):
        """Add a QA pair to memory"""
        self.history.append((question, answer))
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def get_context(self) -> str:
        """Get recent conversation context"""
        if not self.history:
            return ""
        return " ".join([q for q, _ in self.history[-2:]])  # Last 2 questions
    
    def clear(self):
        """Clear conversation history"""
        self.history.clear()


def _call_llm_simple(prompt: str) -> str:
    """Call HuggingFace Inference API for simple text generation (fallback)"""
    if not USE_LLM:
        return ""
    
    try:
        import requests
        import json
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Add auth token if available
        if LLM_API_KEY:
            headers["Authorization"] = f"Bearer {LLM_API_KEY}"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "top_p": 0.9,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            LLM_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
        else:
            print(f"LLM API error: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        print(f"LLM call failed: {e}")
        return ""


def _post_process_text(text: str) -> Optional[str]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        lower = line.lower()
        if line.startswith('*') and 'subscription' in lower:
            continue
        if len(line) <= 3 and not any(ch.isalpha() for ch in line):
            continue
        lines.append(line)
    cleaned = "\n".join(lines).strip()
    if len(cleaned) < 50:
        return None
    return cleaned


def _neutralize_brand_references(text: str) -> str:
    """Remove or neutralize brand-specific references to make responses generic"""
    import re
    
    # Common car brands to neutralize
    brands = [
        "MG", "Lexus", "Toyota", "Honda", "Ford", "BMW", "Mercedes", "Audi", 
        "Volkswagen", "Nissan", "Mazda", "Hyundai", "Kia", "Subaru", "Volvo"
    ]
    
    # Replace brand-specific service center references with generic term
    for brand in brands:
        # "Contact an MG Authorised Repairer" -> "Contact an authorised service center"
        text = re.sub(
            rf'\b{brand}\s+(Authorised|Authorized)\s+(Repairer|Dealer|Service\s+Center)',
            'authorised service center',
            text,
            flags=re.IGNORECASE
        )
        # "MG dealer" -> "your dealer"
        text = re.sub(
            rf'\b{brand}\s+(dealer|dealership)',
            'your dealer',
            text,
            flags=re.IGNORECASE
        )
        # "MG service center" -> "service center"
        text = re.sub(
            rf'\b{brand}\s+(service|repair)\s+center',
            'service center',
            text,
            flags=re.IGNORECASE
        )
    
    return text


def _extract_keywords(text: str) -> Set[str]:
    """Extract meaningful keywords by filtering stop words and short tokens"""
    tokens = re.split(r"[^a-zA-Z0-9]+", text.lower())
    return {token for token in tokens if len(token) >= 3 and token not in STOP_WORDS}


def _calculate_relevance_score(question: str, answer: str) -> float:
    """Calculate semantic relevance between question and answer"""
    question_keywords = _extract_keywords(question)
    answer_keywords = _extract_keywords(answer)
    
    if not question_keywords:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = question_keywords.intersection(answer_keywords)
    union = question_keywords.union(answer_keywords)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)


def _is_procedural_question(question: str) -> bool:
    """Detect if question is asking for procedures or instructions"""
    lower = question.lower()
    procedural_words = [
        "how", "what do", "what can", "how do", "how to", "steps", "procedure",
        "fix", "repair", "solve", "reset", "change", "replace", "install"
    ]
    return any(word in lower for word in procedural_words)


def _is_warning_question(question: str) -> bool:
    """Detect if question is about warnings or error messages"""
    lower = question.lower()
    warning_words = [
        "warning", "light", "indicator", "message", "error", "fault", 
        "mean", "means", "blinking", "flashing", "dashboard"
    ]
    return any(word in lower for word in warning_words)


def _rank_by_relevance(question: str, contents: List[str]) -> List[Tuple[str, float]]:
    """Rank content by relevance to question"""
    scored = []
    for content in contents:
        score = _calculate_relevance_score(question, content)
        scored.append((content, score))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def _extract_context_from_question(question: str) -> Dict[str, Any]:
    """Extract contextual information from the question"""
    lower = question.lower()
    context = {
        "urgency": "normal",
        "safety_related": False,
        "requires_professional": False,
    }
    
    # Detect urgency
    urgent_words = ["emergency", "immediately", "urgent", "now", "asap", "critical"]
    if any(word in lower for word in urgent_words):
        context["urgency"] = "high"
    
    # Detect safety concerns
    safety_words = ["accident", "crash", "brake", "airbag", "fire", "smoke", "danger", "unsafe"]
    if any(word in lower for word in safety_words):
        context["safety_related"] = True
    
    # Detect if professional help is implied
    professional_words = ["broken", "damaged", "leaking", "won't start", "not working"]
    if any(word in lower for word in professional_words):
        context["requires_professional"] = True
    
    return context


def _synthesize_answer(question: str, docs: List[Any]) -> Optional[str]:
    """Synthesize a comprehensive, context-aware answer from multiple documents"""
    all_content = []
    seen_content = set()
    
    # Extract context from question for smarter responses
    question_context = _extract_context_from_question(question)
    
    # Detect question type for smarter filtering
    is_procedural = _is_procedural_question(question)
    is_warning = _is_warning_question(question)
    
    for doc in docs:
        metadata: Dict[str, Any] = getattr(doc, "metadata", {}) or {}
        procedure = metadata.get("procedure")
        warning = metadata.get("warning")
        
        # Prioritize structured data (warnings/procedures) over general content
        if procedure:
            # Neutralize brand references in procedure
            procedure = _neutralize_brand_references(procedure)
            content_hash = hash(procedure.lower().strip())
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                if warning:
                    warning = _neutralize_brand_references(warning)
                    if warning.lower() not in procedure.lower():
                        all_content.append(f"{warning}: {procedure}")
                    else:
                        all_content.append(procedure)
                else:
                    all_content.append(procedure)
        else:
            content = getattr(doc, "page_content", "")
            cleaned = _post_process_text(content)
            if cleaned:
                # Neutralize brand references in content
                cleaned = _neutralize_brand_references(cleaned)
                content_hash = hash(cleaned.lower().strip()[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_content.append(cleaned)
    
    if not all_content:
        return None
    
    # Rank content by relevance
    ranked_content = _rank_by_relevance(question, all_content)
    
    # Filter by minimum confidence threshold
    MIN_CONFIDENCE = 0.15
    relevant_content = [(text, score) for text, score in ranked_content if score >= MIN_CONFIDENCE]
    
    if not relevant_content:
        # If nothing meets threshold, return best match with a caveat
        best_match = ranked_content[0][0] if ranked_content else all_content[0]
        return f"This may not be exactly what you're looking for, but here's related information:\n\n{best_match}"
    
    # For high-confidence single answer, enhance with LLM if enabled
    if len(relevant_content) == 1 or relevant_content[0][1] > 0.4:
        answer = relevant_content[0][0]
        
        # Try to enhance with LLM
        if USE_LLM:
            prompt = f"""Based on this car manual information, provide a clear, helpful answer to the user's question.

Question: {question}

Manual Information:
{answer}

Provide a concise, direct answer based ONLY on the information above. Do not add information not in the manual."""

            llm_answer = _call_llm_simple(prompt)
            if llm_answer and len(llm_answer) > 50:
                answer = llm_answer
        
        # Add safety context if relevant
        if question_context["safety_related"] and question_context["urgency"] == "high":
            answer = f"⚠️ SAFETY NOTE: If this is an emergency, please pull over safely and contact emergency services.\n\n{answer}"
        elif question_context["requires_professional"] and "service center" not in answer.lower():
            answer = f"{answer}\n\nNote: If the issue persists, consult a qualified technician."
        
        return answer
    
    # For procedural questions, combine multiple relevant steps
    if is_procedural and len(relevant_content) > 1:
        top_answers = [text for text, _ in relevant_content[:3]]
        combined = "\n\n".join(top_answers)
        
        # Add helpful closing note for procedures
        if question_context["requires_professional"]:
            combined += "\n\nIf these steps don't resolve the issue, professional assistance may be needed."
        
        return combined
    
    # For warning questions, return the most relevant single answer
    if is_warning:
        answer = relevant_content[0][0]
        
        # Add urgency note for safety-related warnings
        if question_context["safety_related"]:
            answer = f"⚠️ {answer}"
        
        return answer
    
    # For general questions, combine top 2 relevant answers if they're complementary
    if len(relevant_content) >= 2:
        top_two = [text for text, _ in relevant_content[:2]]
        # Check if they have different information (not too similar)
        similarity = _calculate_relevance_score(top_two[0], top_two[1])
        if similarity < 0.7:  # Not too similar
            return "\n\n".join(top_two)
    
    return relevant_content[0][0]


def _is_greeting_or_chitchat(question: str) -> bool:
    """Detect if the question is a greeting or casual chat"""
    lower = question.lower().strip()
    greetings = ["hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye"]
    return any(lower == greet or lower.startswith(f"{greet} ") for greet in greetings)


def _handle_chitchat(question: str) -> Optional[str]:
    """Handle greetings and chitchat naturally"""
    lower = question.lower().strip()
    if lower in ["hi", "hello", "hey"]:
        return "Hi! I'm here to help you understand your car manual. What would you like to know?"
    if "thank" in lower:
        return "You're welcome! Let me know if you need anything else."
    if lower in ["bye", "goodbye"]:
        return "Take care! Feel free to come back if you have more questions."
    return None


def _expand_query(question: str) -> List[str]:
    """Expand query with synonyms and related terms for better retrieval"""
    lower = question.lower()
    queries = [question]
    
    # Common automotive synonyms and expansions
    expansions = {
        "brake": ["braking system", "brake fluid", "brake warning"],
        "engine": ["motor", "engine warning", "check engine"],
        "light": ["indicator", "warning light", "dashboard light"],
        "warning": ["error", "fault", "alert", "message"],
        "fix": ["repair", "resolve", "solve"],
        "reset": ["clear", "turn off"],
        "tire": ["tyre", "wheel"],
        "fuel": ["gas", "petrol", "diesel"],
        "battery": ["electrical system", "power"],
        "abs": ["anti-lock braking", "antilock brake"],
        "airbag": ["srs", "supplemental restraint"],
        "ac": ["air conditioning", "climate control"],
        "oil": ["engine oil", "lubrication"],
    }
    
    # Add expanded queries based on keywords found
    for key, synonyms in expansions.items():
        if key in lower:
            for synonym in synonyms:
                if synonym not in lower:
                    # Create a variant query with the synonym
                    variant = question.replace(key, synonym)
                    if variant != question:
                        queries.append(variant)
    
    # Limit to top 3 queries to avoid over-fetching
    return queries[:3]


def _deduplicate_docs(docs: List[Any]) -> List[Any]:
    """Remove duplicate documents based on content similarity"""
    unique_docs = []
    seen_hashes = set()
    
    for doc in docs:
        # Create a hash based on content
        content = getattr(doc, "page_content", "")
        metadata = getattr(doc, "metadata", {}) or {}
        
        # Use procedure/warning if available for better dedup
        key_content = metadata.get("procedure", content)[:300]
        content_hash = hash(key_content.lower().strip())
        
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_docs.append(doc)
    
    return unique_docs


def _call_llm(question: str, context: str) -> Optional[str]:
    """Call HuggingFace Inference API with context-aware, intelligent synthesis"""
    if not USE_LLM or not LLM_API_KEY:
        return None
    
    try:
        import requests
        
        # MUCH BETTER PROMPT: Understand user intent and synthesize information
        full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an intelligent automotive assistant who helps users understand and use their car manual effectively.

YOUR APPROACH:
1. **Understand the User's Intent**: What are they really trying to do? Fix something? Learn how to use a feature? Troubleshoot an issue?
2. **Synthesize Information**: Don't just quote the manual - explain it in the context of what they're asking
3. **Be Practical**: Give actionable steps, tips, and warnings
4. **Explain WHY**: Help them understand the reasoning behind instructions
5. **Anticipate Follow-ups**: Address related concerns they might have
6. **Use Simple Language**: Translate technical jargon into plain English
7. **Be Contextual**: Consider what a real person asking this question would need to know

EXAMPLES OF GOOD ANSWERS:
❌ BAD: "The manual says to check tire pressure monthly."
✅ GOOD: "You should check your tire pressure at least once a month. This is important because properly inflated tires improve fuel efficiency, provide better handling, and last longer. The recommended pressure is usually on a sticker inside the driver's door. Check when tires are cold (haven't been driven for a few hours) for accurate readings."

❌ BAD: "Section 3.2 covers this."
✅ GOOD: "To change your tire, here's what you need to do: First, make sure you're on flat ground and the car is in park. Get your spare tire, jack, and lug wrench from the trunk. Loosen the lug nuts before jacking up the car, then..."

<|eot_id|><|start_header_id|>user<|end_header_id|>

RELEVANT MANUAL INFORMATION:
{context[:2500]}

USER'S QUESTION: {question}

INSTRUCTIONS:
1. First, understand what the user is REALLY asking (their intent and context)
2. Synthesize the manual information to directly address their need
3. Provide a complete, practical answer that makes sense in their situation
4. Explain concepts clearly without just quoting the manual
5. Include any relevant safety warnings or important tips

Provide your answer now:<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

        headers = {"Authorization": f"Bearer {LLM_API_KEY}"}
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 500,  # More space for comprehensive answers
                "temperature": 0.6,      # Slightly more creative for better synthesis
                "top_p": 0.92,
                "do_sample": True,
                "repetition_penalty": 1.15,  # Avoid repetition
                "presence_penalty": 0.1      # Encourage diverse vocabulary
            }
        }
        
        response = requests.post(LLM_API_URL, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "").strip()
                # Clean up the response
                if generated_text:
                    # Remove prompt artifacts
                    if "<|start_header_id|>assistant<|end_header_id|>" in generated_text:
                        generated_text = generated_text.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
                    generated_text = generated_text.replace("<|eot_id|>", "").strip()
                    generated_text = generated_text.replace("<|end_of_text|>", "").strip()
                    
                    # Only return if it's a substantial, helpful answer
                    if len(generated_text) > 30 and not generated_text.startswith("I don't"):
                        return generated_text
        
        return None
    except Exception as e:
        print(f"LLM call failed: {e}")
        return None


def make_rag_chain(retriever):
    class Chain:
        def __init__(self, retriever):
            self.retriever = retriever

        def invoke(self, question: str):
            # Handle chitchat naturally
            chitchat_response = _handle_chitchat(question)
            if chitchat_response:
                return SimpleResponse(chitchat_response)
            
            # Clean and normalize the question
            question = question.strip()
            
            # Expand query with synonyms for better retrieval
            expanded_queries = _expand_query(question)
            
            # Retrieve documents using multiple query variations for better context
            all_docs = []
            for query in expanded_queries:
                docs = list(self.retriever.invoke(query))[:6]
                all_docs.extend(docs)
            
            # Remove duplicates
            unique_docs = _deduplicate_docs(all_docs)
            
            # Get more context for LLM to understand better
            final_docs = unique_docs[:10]
            
            if not final_docs:
                return SimpleResponse(FALLBACK_MESSAGE)

            # Try LLM-based answer with RICH CONTEXT for intelligent synthesis
            print(f"[DEBUG] USE_LLM={USE_LLM}, has_key={bool(LLM_API_KEY)}")
            if USE_LLM and LLM_API_KEY:
                print("[DEBUG] Using intelligent LLM path")
                # Provide MORE context so LLM can understand and synthesize better
                # Include full chunks, not truncated
                context_chunks = []
                total_length = 0
                for doc in final_docs[:5]:  # Top 5 most relevant chunks
                    content = getattr(doc, "page_content", "")
                    # Include full content up to reasonable limit
                    if total_length + len(content) < 2500:
                        context_chunks.append(content)
                        total_length += len(content)
                    else:
                        # Add partial if we have room
                        remaining = 2500 - total_length
                        if remaining > 100:
                            context_chunks.append(content[:remaining])
                        break
                
                context = "\n\n---\n\n".join(context_chunks)
                
                try:
                    llm_answer = _call_llm(question, context)
                    
                    # Accept answer if it's substantial and helpful
                    if llm_answer and len(llm_answer) > 30:
                        return SimpleResponse(llm_answer)
                except Exception as e:
                    print(f"[ERROR] LLM call failed: {e}")
                    # Fall through to rule-based synthesis

            # Fallback to rule-based synthesis only if LLM fails
            synthesized = _synthesize_answer(question, final_docs)
            if synthesized:
                return SimpleResponse(synthesized)

            return SimpleResponse(FALLBACK_MESSAGE)

    return Chain(retriever)
