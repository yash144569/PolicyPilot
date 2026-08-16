
import langchain
import re
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_compressors import FlashrankRerank
import logging
import sys

# Uvicorn Log Setup
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    force=True,
    format="%(levelname)s: %(message)s"
)

CHROMA_PATH = "chroma_db"

# 1. Embeddings & DB — kept LOCAL (Ollama) for privacy. Policy PDFs often
# contain PII (name, address, policy number) — only the final generation
# call goes to the cloud (Groq); raw document chunks used for embeddings
# never leave the machine.
embedding_model = OllamaEmbeddings(model="nomic-embed-text")
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)

# 2. LLM — switched to Groq-hosted 70B model for generation.
# WHY: The local llama3.1:8b model repeatedly hallucinated digits when
# reformatting numbers, and confused unrelated clauses (e.g. answering a
# "total loss" question with a "third-party property damage" limit) despite
# strict prompt rules. Larger, better-instruction-tuned models are
# meaningfully more reliable at this kind of precise, low-hallucination
# reasoning task.
#
# SETUP:
#   pip install langchain-groq --break-system-packages
#   export GROQ_API_KEY="your-key-here"   (get one free at console.groq.com)
#
# PRIVACY NOTE: switching to Groq means policy document excerpts (the
# retrieved context) ARE sent to Groq's cloud API for the final answer
# generation step. If you're handling sensitive customer PII and this is a
# concern, keep using ChatOllama instead (see commented fallback below).
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

llm_primary = ChatGroq(
    model=GROQ_MODEL,
    temperature=0,
    max_tokens=1024,
    api_key=os.environ.get("GROQ_API_KEY"),
)

# FIX: Groq's free tier has a daily token cap (100k tokens/day) that gets
# hit fast since each question fires ~4 LLM calls (3 query variations +
# 1 final answer). Rather than the whole API returning a 500 and going
# down, automatically fall back to the local Ollama model so the app keeps
# working (with local-model quality) until the Groq quota resets.
llm_fallback = ChatOllama(
    model="llama3.1",
    temperature=0,
    repeat_penalty=1.3,
    num_predict=300,
)


class _LLMWithFallback:
    """Wraps llm.invoke(...) — tries Groq first, falls back to local Ollama
    on rate-limit (429) or any other Groq API failure, so the app degrades
    gracefully instead of returning a 500 to the user."""

    def invoke(self, prompt):
        try:
            return llm_primary.invoke(prompt)
        except Exception as e:
            print(f"⚠️ Groq call failed ({e}) — falling back to local Ollama model")
            return llm_fallback.invoke(prompt)


llm = _LLMWithFallback()

# Set to True while debugging retrieval issues, False in production
DEBUG_RETRIEVAL = True

PROMPT_TEMPLATE = """<system_instructions>
You are PolicyPilot, an expert Insurance Policy Assistant and Legal Claim Analyst. 
Your sole objective is to answer the user's question using ONLY the provided policy excerpts. 
Explain complex insurance clauses in simple, easy-to-understand language.

STRICT OPERATIONAL RULES:
1. FINANCIAL LIMITS: If the query is about benefits/expenses, search for caps, sub-limits, or percentages. If none exist, explicitly state: "No specific financial cap is mentioned in these excerpts." When you state a percentage or amount, you MUST include its EXACT qualifiers word-for-word as given in the context (e.g. "1% of Sum Insured PER DAY, or actual expenses, WHICHEVER IS LESS" — not just "1% of SI"). If the context has both a short summary-table version and a longer detailed-clause version of the same figure, ALWAYS use the longer, more qualified version and cite that chunk's page.
2. EXCLUSIONS & PERMANENT EXCLUSIONS (CRITICAL): If a procedure, treatment, condition, or event (such as Maternity, Childbirth, Alcoholism, Infertility, etc.) appears under any "Exclusion" or "Permanent Exclusions" section, you MUST state clearly and upfront that it is PERMANENTLY EXCLUDED / NOT COVERED under the policy, instead of saying it is not mentioned.
3. MISSING INFORMATION & INDUSTRY STANDARD: If the exact scenario is not mentioned in the text, you MUST state: "This specific scenario is not explicitly mentioned in your uploaded policy document." Then, provide a brief general industry standard under: "**General Industry Standard (Not confirmed for your policy):**"
4. CITATIONS (CRITICAL): DO NOT guess or print section names. ONLY cite the exact Page Number like this: [Page: X]. The context excerpts below may contain "[Section: ...]" tags — these are INTERNAL markers to help you understand which clause a piece of text belongs to. NEVER reproduce a "[Section: ...]" tag in your answer, and NEVER write things like "Code – [Section: ...]". If you want to name the clause, describe it in plain words (e.g. "under the In-patient Hospitalisation Expenses Cover clause") and still cite only [Page: X].
5. TOPIC PURITY: Stay strictly on topic. If asked about Renewal, ignore medical lists. If asked about Claims, ignore exclusions unless relevant.
6. NO HALLUCINATION: Never invent clauses, numbers, or rules not present in the context.
7. COMPOUND OR MULTI-PART QUESTIONS (CRITICAL): If the user's question contains multiple parts or asks for multiple items (e.g., room rent AND ICU charges), you MUST break down your answer and explicitly address EVERY SINGLE part of the question. Do not skip any requested detail.
8. DO NOT CONFLATE DIFFERENT CLAUSES (CRITICAL): Insurance policies often have multiple, separately-coded, adjacent clauses on similar-sounding topics (e.g. "Pre-Existing Diseases - Excl01" vs "Specified Disease/Procedure Waiting Period - Excl02"). These are DIFFERENT clauses with DIFFERENT rules. Before answering, identify the EXACT clause/section whose title or exclusion code matches the user's question. If the context contains the exact matching clause with a specific number (e.g. "48 months"), you MUST use that number and MUST NOT say "no specific waiting period is mentioned" just because a nearby, differently-titled clause also discusses waiting periods. Never borrow numbers from one clause to answer a question about a different clause.
9. MANDATORY ANSWER FORMAT (CRITICAL): Your answer MUST start with a single line in this exact format, containing ONLY the number/fact that comes from the clause whose title/code most directly matches the question — nothing borrowed from a different clause:
   **Direct Answer:** <one short sentence with the specific figure and its clause code, e.g. "48 months (Code – Excl01)">
   After that line, you may add a "Details:" section with supporting explanation. CRITICAL: In the Details section, DO NOT type the numeric figure again — you already stated it correctly once in Direct Answer, and retyping it risks a transcription error. Instead refer back to it in words, e.g. "This amount is calculated as..." or "The figure stated above applies because...". Only type a NEW number in Details if it is genuinely a DIFFERENT figure not already given in Direct Answer (e.g. a different clause's different limit) — and even then, copy it character-for-character from the context. If a DIFFERENT clause (different code) is also relevant, introduce it explicitly by name and code — never merge its number into the Direct Answer line.
10. NEVER REFORMAT NUMBERS (CRITICAL): Copy every numeric figure EXACTLY character-for-character as it appears in the context — same digits, same commas, same position. Do NOT attempt to convert the number into a different comma-grouping style (e.g. Indian lakh/crore grouping) even if it seems more natural or reader-friendly — the ACT of attempting this conversion is what causes you to fabricate wrong digits. For example, if the context says "753,040", you must write "753,040" every time — writing "₹75,30,400" or "₹75,40,000" instead is a FABRICATION and a serious error, even though it looks similar. If you are not 100% certain of a converted format, do not convert at all — just repeat the original digit string as-is. If the same figure appears more than once in your answer, copy it fresh from the context each time rather than retyping from memory.
11. SCOPE CHECK BEFORE ANSWERING (CRITICAL): A retrieved excerpt matching a keyword from the question does NOT mean it actually answers the question. Different covers/perils that sound similar are often COMPLETELY DIFFERENT (e.g. "damage to THIRD PARTY property" is a liability limit for damage YOU cause to someone else — it is NOT the same as "damage to YOUR OWN vehicle" or "total loss/theft of your own vehicle", which is a different cover entirely). Before answering, explicitly check: does this excerpt describe the SAME party, SAME peril, and SAME scenario the user asked about? If the only match is a shared word (e.g. both mention "damage") but the actual subject is different, you MUST treat this as MISSING INFORMATION per Rule 3 — do NOT state an unrelated clause's number as if it answers the question.
</system_instructions>
</system_instructions>

<policy_context>
{context}
</policy_context>

<user_question>
{question}
</user_question>

<answer>
"""

# ---------------------------------------------------------------------
# Used by /api/summary in api.py to build an auto-generated overview.
# Add/adjust questions per policy type as needed.
# ---------------------------------------------------------------------
POLICY_QUESTIONS = {
    "Common": [
        ("Policy Type & Coverage", "What type of insurance policy is this and what does it cover?"),
        ("Sum Insured", "What is the sum insured / coverage amount under this policy?"),
        ("Premium & Renewal", "What are the premium payment terms and renewal conditions?"),
        ("Exclusions", "What are the major exclusions or permanent exclusions under this policy?"),
        ("Claim Process", "What is the process for filing a claim under this policy?"),
        ("Waiting Period", "What waiting periods apply under this policy?"),
    ],
    "Health": [
        ("Room Rent & ICU Limits", "What are the room rent and ICU charge sub-limits?"),
        ("Pre-existing Diseases", "How are pre-existing diseases covered and what is the waiting period?"),
        ("Maternity Coverage", "Is maternity or childbirth covered under this policy?"),
        ("Day Care Procedures", "Which day care procedures are covered?"),
    ],
    "Motor": [
        ("Own Damage Cover", "What does the own damage cover include?"),
        ("Third Party Liability", "What is the third party liability coverage?"),
        ("No Claim Bonus", "How does the no claim bonus (NCB) work under this policy?"),
        ("Depreciation & Add-ons", "How is depreciation handled and what add-on covers are available (zero depreciation, engine protect, etc.)?"),
    ],
    "Life": [
        ("Death Benefit", "What is the death benefit payable under this policy?"),
        ("Maturity Benefit", "What is the maturity benefit, if any?"),
        ("Surrender Value", "What is the surrender value and when can the policy be surrendered?"),
    ],
    "Unknown": [
        ("Key Benefits", "What are the key benefits offered under this policy?"),
        ("Key Exclusions", "What are the key exclusions under this policy?"),
    ],
}


def detect_policy_type() -> str:
    """
    Asks the LLM to classify the uploaded policy into one of the known
    categories, based on a quick similarity search against the DB.
    Falls back to 'Unknown' on any failure so /api/summary never crashes.
    """
    try:
        sample_docs = db.similarity_search(
            "policy type coverage benefits schedule", k=5
        )
        sample_text = "\n\n".join(d.page_content for d in sample_docs)

        prompt = f"""Based on the following excerpt from an insurance policy document,
classify it into EXACTLY ONE of these categories: Health, Motor, Life, Unknown.

Respond with ONLY the single category word, nothing else.

Excerpt:
{sample_text[:3000]}
"""
        response = llm.invoke(prompt)
        answer = response.content.strip().split()[0].strip(".,:;").title()

        if answer in ("Health", "Motor", "Life"):
            return answer
        return "Unknown"
    except Exception as e:
        print(f"⚠️ detect_policy_type failed, defaulting to Unknown: {e}")
        return "Unknown"


def generate_policy_queries(original_question: str) -> list:
    prompt = f"""You are an insurance AI assistant. Your job is to help search a policy document.
Generate 2 alternative search phrasings for the user's question, using formal insurance terminology (e.g., clauses, exclusions, procedures, limits).
Do NOT write general lifestyle or medical advice. Keep it strictly bound to insurance policy wording.

Original Question: {original_question}

Output format: Just provide the 2 alternative questions, one per line, nothing else.
"""
    try:
        response = llm.invoke(prompt)
        lines = [line.strip() for line in response.content.split('\n') if line.strip()]
        all_queries = [original_question] + lines[:2]
        print(f"📌 Multi-Queries generated: {all_queries}")
        return all_queries
    except Exception as e:
        print(f"⚠️ Query generation failed, falling back to original: {e}")
        return [original_question]


def _debug_dump(label: str, docs: list):
    if not DEBUG_RETRIEVAL:
        return
    print(f"\n=== {label} ({len(docs)} chunks) ===")
    for i, doc in enumerate(docs):
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:120].replace("\n", " ")
        print(f"[{i}] Page {page}: {preview}...")
    print(f"=== END {label} ===\n")


def _verify_numbers_against_context(answer_text: str, context: str) -> list:
    """
    FIX: Prompt rules alone weren't reliably stopping this model from
    fabricating digits when it tries to reformat a number (e.g. context has
    "753,040" and the model outputs "75,30,400" or "75,40,000" — an extra
    digit gets hallucinated in the attempt to convert to Indian lakh-style
    grouping). This scans every numeric token in the model's answer and
    checks whether its digit sequence (commas stripped) appears anywhere in
    the retrieved context. Returns a list of suspicious (unverified) numbers
    for logging — this is a monitoring safety net, not an auto-fix, since
    blindly rewriting text is riskier than flagging it.
    """
    context_digit_strings = set(
        re.sub(r"[^\d]", "", tok) for tok in re.findall(r"\d[\d,]*\d|\d", context)
    )
    context_digit_strings = {d for d in context_digit_strings if len(d) >= 3}

    answer_numbers = re.findall(r"\d[\d,]*\d|\d{3,}", answer_text)
    suspicious = []
    for num in answer_numbers:
        digits = re.sub(r"[^\d]", "", num)
        if len(digits) < 3:
            continue  # skip small numbers (page refs, list indices, percentages like "48")
        if digits not in context_digit_strings:
            suspicious.append(num)
    return suspicious


def ask_policy(question: str):
    print(f"\n[AI Processing] Multi-Query + Reranker pipeline started for: '{question}'...")

    # Step 1: Query Variations generate karna
    queries = generate_policy_queries(question)

    # Step 2: Har query ke liye SIMILARITY search chalana
    # (MMR ki jagah similarity — MMR diversity ke liye chunks hata deta tha,
    #  jisse best-matching clause hi drop ho jata tha)
    all_docs = []
    seen_content = set()

    base_retriever = db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 20}
    )

    for q in queries:
        docs = base_retriever.invoke(q)
        for doc in docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                all_docs.append(doc)

    _debug_dump("RAW RETRIEVAL", all_docs)

    if len(all_docs) == 0:
        return "I couldn't find this information in the provided policy.", []

    # Step 3: Flashrank Reranker (Lazy Loaded inside function to avoid startup crashes)
    try:
        print(f"🔄 Reranking {len(all_docs)} retrieved chunks...")
        compressor = FlashrankRerank(top_n=10)
        reranked_docs = compressor.compress_documents(all_docs, question)
        unique_docs = reranked_docs[:10]
    except Exception as e:
        print(f"⚠️ Reranking failed, falling back to raw docs: {e}")
        unique_docs = all_docs[:10]

    # ------------------------------------------------------------------
    # FIX: FlashRank's default model can rank a chunk with matching
    # SECTION HEADING keywords (e.g. "Pre-Existing Diseases") lower than
    # tangential chunks, and LLMs pay less attention to the MIDDLE of a
    # long context ("lost in the middle" effect). Rather than trust
    # FlashRank's order blindly, do a cheap keyword-overlap boost: any
    # chunk whose [Section: ...] heading shares meaningful words with the
    # question gets moved to the FRONT of the context, regardless of its
    # FlashRank score. This is a safety net, not a replacement for
    # reranking — it only re-orders, never drops, chunks.
    # ------------------------------------------------------------------
    STOPWORDS = {
        "what", "is", "the", "for", "under", "this", "policy", "are",
        "of", "a", "an", "does", "do", "in", "on", "to", "and", "or",
        "with", "will", "can", "i", "my", "your", "you",
    }
    raw_words = [w.strip(".,()?").lower() for w in question.split()]
    question_words = {w for w in raw_words if w not in STOPWORDS and len(w) > 2}
    # Consecutive-word phrases (bigrams) from the question, e.g. "pre-existing diseases",
    # "waiting period". A section heading matching a full PHRASE (not just scattered
    # single words) is a much stronger, more specific signal than any single word match.
    question_bigrams = [
        f"{raw_words[i]} {raw_words[i+1]}"
        for i in range(len(raw_words) - 1)
        if raw_words[i] not in STOPWORDS and raw_words[i + 1] not in STOPWORDS
        and len(raw_words[i]) > 2 and len(raw_words[i + 1]) > 2
    ]

    # ------------------------------------------------------------------
    # FIX: Exact word matching missed cases where the question uses a
    # different grammatical FORM than the document (e.g. question says
    # "renewING", document heading says "renewAL Of Policy" — completely
    # different strings, same underlying word). This caused the correct
    # "16. Renewal Of Policy" clause to get ZERO boost, while an unrelated
    # "Discount" clause (which happened to contain the literal word
    # "renewals") won instead. A cheap poor-man's stemmer — comparing the
    # first 5 characters of words — catches most English suffix variants
    # (renew/renewing/renewal/renewed all share "renew") without needing a
    # real NLP stemming library.
    # ------------------------------------------------------------------
    def stem(word: str) -> str:
        return word[:5] if len(word) >= 5 else word

    question_stems = {stem(w) for w in question_words}

    def section_match_score(doc) -> int:
        section = doc.metadata.get("section", "")
        section_lower = section.lower()
        section_words = {w.strip(".,()–-") for w in section_lower.split()}
        word_overlap = len(question_words & section_words)
        # Stemmed overlap catches grammatical variants (renewing vs renewal)
        # that exact matching misses. Weighted lower than exact match since
        # it's a fuzzier signal.
        section_stems = {stem(w) for w in section_words}
        stem_overlap = len(question_stems & section_stems)
        # Big bonus if a whole phrase from the question appears contiguously
        # in the heading — this is what actually distinguishes "1. Pre-Existing
        # Diseases" from "3. Underwriting Loading for Pre-existing Conditions",
        # which only shares the single word "pre-existing".
        phrase_bonus = sum(5 for bg in question_bigrams if bg in section_lower)

        # FIX: Some clauses have a GENERIC parent heading (e.g. "1. In-patient
        # Hospitalisation Expenses Cover" for the Room Rent / ICU sub-limit),
        # so heading-only matching misses them entirely. Also check the
        # chunk's own BODY text for question keywords — weighted lower than
        # a heading match (which is a stronger, more specific signal) but
        # still enough to pull a genuinely relevant chunk above irrelevant
        # ones (which won't contain "room"/"rent"/"icu" at all).
        body_lower = doc.page_content.lower()
        body_words = set(re.findall(r"[a-z0-9%]+", body_lower))
        body_overlap = len(question_words & body_words)
        body_stems = {stem(w) for w in body_words}
        body_stem_overlap = len(question_stems & body_stems)

        return (
            (word_overlap * 3)
            + (stem_overlap * 2)
            + phrase_bonus
            + body_overlap
            + (body_stem_overlap * 0.5)
        )

    # Stable sort: ties keep FlashRank's original relative order, but any
    # chunk with a real keyword/phrase match to the question is pulled ahead
    # of chunks with zero match, and stronger (phrase-level) matches are
    # pulled ahead of weaker (single incidental word) matches.
    unique_docs = sorted(unique_docs, key=section_match_score, reverse=True)

    _debug_dump("AFTER RERANK", unique_docs)

    context = "\n\n".join(
        f"[Page: {doc.metadata.get('page', 'Unknown')}]\n{doc.page_content}"
        for doc in unique_docs
    )

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    response = llm.invoke(prompt)

    # ------------------------------------------------------------------
    # FIX: Prompt-only instructions were NOT reliable enough to stop this
    # model from fabricating digits when restating a number a second time
    # (e.g. "753,040" in Direct Answer becoming "75,30,400" in Details).
    # Since we can't fully trust the model's own numbers, mechanically
    # verify every numeric token against the retrieved context and REDACT
    # (not just log) anything that doesn't match — a wrong number is worse
    # than no number for an insurance answer.
    # ------------------------------------------------------------------
    final_answer = response.content
    suspicious_numbers = _verify_numbers_against_context(final_answer, context)
    if suspicious_numbers:
        print(
            f"⚠️ NUMBER HALLUCINATION WARNING: these numbers in the answer "
            f"were NOT found in the retrieved context and will be redacted: "
            f"{suspicious_numbers}"
        )
        for bad_num in set(suspicious_numbers):
            final_answer = final_answer.replace(
                bad_num, "[figure could not be verified — see amount stated above]"
            )

    sources = []
    seen_sources = set()
    for doc in unique_docs:
        source = doc.metadata.get("source", "Unknown File")
        page = doc.metadata.get("page", "Unknown")
        key = (source, page)
        if key not in seen_sources:
            seen_sources.add(key)
            sources.append(key)

    return final_answer, sources