
# import os
# import re
# import shutil
# import time
# import stat
# from collections import defaultdict

# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings
# from langchain_core.documents import Document

# DATA_PATH = "docs"
# CHROMA_PATH = "chroma_db"

# # Ollama Embedding Model
# embedding_model = OllamaEmbeddings(
#     model="nomic-embed-text"
# )

# def load_documents():
#     loader = DirectoryLoader(
#         DATA_PATH,
#         glob="**/*.pdf",
#         loader_cls=PyPDFLoader,
#         show_progress=True,
#     )
#     return loader.load()

# # Updated with Critical Insurance Keywords
# HEADING_KEYWORDS = [
#     # Health Insurance
#     "exclusions", "definitions", "benefits covered", "general terms",
#     "other terms and conditions", "policy terms and conditions",
#     "claim procedure", "grievance", "what is not covered", 
#     "scope of cover", "special conditions", "waiting period", 
#     "maternity benefits", "eligibility", "coverage", "insuring clause"

#     # Motor / Vehicle Insurance (Car & Bike)
#     "insured declared value", "idv", "third party liability", "third-party",
#     "no claim bonus", "ncb", "depreciation", "own damage", "vehicle damage",
#     "personal accident cover", "towing charges",
    
#     # Term / Life Insurance
#     "death benefit", "nominee", "survival benefit", "grace period", 
#     "lapse", "surrender value", "premium payment", "free look period"
# ]

# def _looks_like_heading(line):
#     # Normalize whitespace first - real PDF extraction often has irregular
#     # spacing (double spaces, stray tabs) that breaks strict pattern matching.
#     stripped = " ".join(line.split())
#     if not stripped or len(stripped) > 80:
#         return False
#     lowered = stripped.lower()
#     if len(stripped.split()) <= 10 and any(kw in lowered for kw in HEADING_KEYWORDS):
#         return True
#     if re.match(r'^[A-Z][.\d]{0,4}\s+[A-Z][A-Za-z &]{2,60}$', stripped):
#         return True
#     return False

# def merge_pages_by_source(documents):
#     grouped = defaultdict(list)
#     for doc in documents:
#         grouped[doc.metadata["source"]].append(doc)

#     merged_docs = []
#     for source, pages in grouped.items():
#         pages.sort(key=lambda d: d.metadata.get("page", 0))

#         full_text = ""
#         page_offsets = []
#         section_offsets = []
#         current_section = "General"
#         section_start = 0
#         detected_headings = []

#         for p in pages:
#             page_start = len(full_text)

#             for line in p.page_content.splitlines():
#                 if _looks_like_heading(line):
#                     section_offsets.append((section_start, len(full_text), current_section))
#                     current_section = " ".join(line.split())
#                     section_start = len(full_text)
#                     detected_headings.append(current_section)
#                 full_text += line + "\n"

#             full_text += "\n"
#             page_end = len(full_text)
#             page_offsets.append((page_start, page_end, p.metadata.get("page", 0) + 1))

#         section_offsets.append((section_start, len(full_text), current_section))

#         print(f"\n[{source}] Detected {len(detected_headings)} section headings:")
#         for h in detected_headings:
#             print(f"   - {h}")

#         merged_docs.append(Document(
#             page_content=full_text,
#             metadata={
#                 "source": source,
#                 "page_offsets": page_offsets,
#                 "section_offsets": section_offsets,
#             },
#         ))

#     return merged_docs


# def _resolve_span(start_index, offsets, fallback):
#     for start, end, label in offsets:
#         if start <= start_index < end:
#             return label
#     return offsets[-1][2] if offsets else fallback


# def split_documents(documents):
#     # Tuned for Insurance Legal Clauses: Slightly smaller chunk with larger overlap
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=300,
#         add_start_index=True,
#     )

#     merged = merge_pages_by_source(documents)
#     chunks = splitter.split_documents(merged)

#     for chunk in chunks:
#         start_index = chunk.metadata.get("start_index", 0)
#         page_offsets = chunk.metadata.pop("page_offsets", [])
#         section_offsets = chunk.metadata.pop("section_offsets", [])
#         chunk.metadata["page"] = _resolve_span(start_index, page_offsets, "Unknown")
#         chunk.metadata["section"] = _resolve_span(start_index, section_offsets, "General")

#     return chunks


# # --- HELPER FUNCTION: Read-Only लॉक को जबरदस्ती हटाने के लिए ---
# def _remove_readonly(func, path, _):
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except Exception as e:
#         print(f"Warning: could not force delete {path}: {e}")


# # --- UPDATED FUNCTION: Safe Delete + Re-create ChromaDB ---
# def create_vector_store(chunks):
#     if os.path.exists(CHROMA_PATH):
#         try:
#             # onerror=_remove_readonly किसी भी रीड-ओनली फाइल लॉक को तोड़ देगा
#             shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
#             time.sleep(1.5)  # SQLite को फाइल का कनेक्शन छोड़ने का पूरा समय दें
#         except Exception as e:
#             print(f"Warning: Could not delete old DB folder: {e}")

#     print("Creating Chroma DB...")

#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )

#     print("Vector DB created successfully!")


# def main():
#     print("Loading PDFs...")
#     documents = load_documents()

#     print(f"Pages loaded : {len(documents)}")

#     chunks = split_documents(documents)

#     print(f"Chunks created : {len(chunks)}")

#     create_vector_store(chunks)


# if __name__ == "__main__":
#     main()

# import os
# import re
# import shutil
# import time
# import stat

# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings

# DATA_PATH = "docs"
# CHROMA_PATH = "chroma_db"

# # Ollama Embedding Model
# embedding_model = OllamaEmbeddings(
#     model="nomic-embed-text"
# )

# def load_and_split_documents():
#     print("Loading PDFs page by page...")
#     loader = DirectoryLoader(
#         DATA_PATH,
#         glob="**/*.pdf",
#         loader_cls=PyPDFLoader,
#         show_progress=True,
#     )
#     pages = loader.load()
#     print(f"Total pages loaded: {len(pages)}")

#     # ⚡ पेज-वाइज स्प्लिटिंग ताकि हर पेज का स्ट्रक्चर और टेबल सुरक्षित रहे ⚡
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=400,
#         add_start_index=True,
#     )
    
#     chunks = splitter.split_documents(pages)
    
#     # LangChain PyPDFLoader ऑटोमैटिक 'page' इंडेक्स (0-based) देता है, उसे 1-based कर देते हैं
#     for chunk in chunks:
#         if "page" in chunk.metadata:
#             chunk.metadata["page"] = int(chunk.metadata["page"]) + 1
#         else:
#             chunk.metadata["page"] = "Unknown"
            
#     print(f"Total chunks created: {len(chunks)}")
#     return chunks

# # --- Read-Only लॉक हटाने का फंक्शन ---
# def _remove_readonly(func, path, _):
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except Exception as e:
#         print(f"Warning: could not force delete {path}: {e}")

# def create_vector_store(chunks):
#     if os.path.exists(CHROMA_PATH):
#         try:
#             shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Warning: Could not delete old DB folder: {e}")

#     print("Creating Chroma DB...")
#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )
#     print("Vector DB created successfully!")

# def main():
#     chunks = load_and_split_documents()
#     create_vector_store(chunks)

# if __name__ == "__main__":
#     main()


# import os
# import shutil
# import time
# import stat
# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings
# from langchain_core.documents import Document

# DATA_PATH = "docs"
# CHROMA_PATH = "chroma_db"

# # Ollama Embedding Model
# embedding_model = OllamaEmbeddings(model="nomic-embed-text")


# def load_and_split_documents():
#     print("Loading PDFs page by page...")
#     loader = DirectoryLoader(
#         DATA_PATH,
#         glob="**/*.pdf",
#         loader_cls=PyPDFLoader,
#         show_progress=True,
#     )
#     pages = loader.load()
#     print(f"Total pages loaded: {len(pages)}")

#     # ------------------------------------------------------------------
#     # FIX: PyPDFLoader gives ONE Document per page. If we split each page
#     # separately, a clause/table that spans the bottom of page N into the
#     # top of page N+1 gets cut in half and neither half matches queries
#     # well. Instead we merge consecutive pages of the SAME source file
#     # into one long text (with a page marker per page), then split that.
#     # We keep the page marker in the text itself so each resulting chunk
#     # can be reliably mapped back to a page number.
#     # ------------------------------------------------------------------
#     pages_by_source = {}
#     for p in pages:
#         src = p.metadata.get("source", "unknown")
#         pages_by_source.setdefault(src, []).append(p)

#     merged_docs = []
#     for src, src_pages in pages_by_source.items():
#         # sort by original page order just in case
#         src_pages.sort(key=lambda d: d.metadata.get("page", 0))

#         combined_text = ""
#         page_marker_offsets = []  # (char_offset_in_combined_text, page_number_1_based)

#         for p in src_pages:
#             page_num = int(p.metadata.get("page", 0)) + 1  # 1-based
#             page_marker_offsets.append((len(combined_text), page_num))
#             combined_text += p.page_content + "\n"

#         merged_docs.append(
#             Document(
#                 page_content=combined_text,
#                 metadata={"source": src, "page_offsets": page_marker_offsets},
#             )
#         )

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=200,
#         add_start_index=True,
#     )

#     chunks = splitter.split_documents(merged_docs)

#     # Map each chunk's start_index back to the correct page number using
#     # the page_offsets table we built above.
#     for chunk in chunks:
#         offsets = chunk.metadata.pop("page_offsets", [])
#         start = chunk.metadata.get("start_index", 0)
#         page_num = "Unknown"
#         for offset, pnum in offsets:
#             if offset <= start:
#                 page_num = pnum
#             else:
#                 break
#         chunk.metadata["page"] = page_num

#     print(f"Total chunks created: {len(chunks)}")
#     return chunks


# def _remove_readonly(func, path, _):
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except Exception as e:
#         print(f"Warning: could not force delete {path}: {e}")


# def create_vector_store(chunks):
#     if os.path.exists(CHROMA_PATH):
#         try:
#             shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Warning: Could not delete old DB folder: {e}")

#     print("Creating Chroma DB...")
#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )
#     print("Vector DB created successfully!")


# def main():
#     chunks = load_and_split_documents()
#     create_vector_store(chunks)


# if __name__ == "__main__":
#     main()

# import os
# import re
# import shutil
# import time
# import stat
# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings
# from langchain_core.documents import Document

# DATA_PATH = "docs"
# CHROMA_PATH = "chroma_db"

# # Ollama Embedding Model
# embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# # ------------------------------------------------------------------
# # Matches short, title-like lines such as:
# #   "1. Pre-Existing Diseases (Code – Excl01)"
# #   "2. Specified Disease/Procedure Waiting Period (Code – Excl02)"
# #   "A. Waiting Periods (Only Applicable for Gold & Senior Citizen Plans)"
# #   "9. What Policy Does Not Cover"
# # Used to find the nearest parent heading for any chunk, so short chunks
# # that get cut mid-clause (e.g. "the expiry of 48 months...") still carry
# # their topic ("Pre-Existing Diseases") in the text that gets embedded.
# # ------------------------------------------------------------------
# HEADING_PATTERN = re.compile(
#     r"(?m)^((?:[A-Z]\.|\d{1,2}\.)\s+[A-Z][A-Za-z0-9 /\-\u2013\u2014\(\)&,\.']{3,90})\s*$"
# )


# def load_and_split_documents():
#     print("Loading PDFs page by page...")
#     loader = DirectoryLoader(
#         DATA_PATH,
#         glob="**/*.pdf",
#         loader_cls=PyPDFLoader,
#         show_progress=True,
#     )
#     pages = loader.load()
#     print(f"Total pages loaded: {len(pages)}")

#     # ------------------------------------------------------------------
#     # FIX: PyPDFLoader gives ONE Document per page. If we split each page
#     # separately, a clause/table that spans the bottom of page N into the
#     # top of page N+1 gets cut in half and neither half matches queries
#     # well. Instead we merge consecutive pages of the SAME source file
#     # into one long text (with a page marker per page), then split that.
#     # We keep the page marker in the text itself so each resulting chunk
#     # can be reliably mapped back to a page number.
#     # ------------------------------------------------------------------
#     pages_by_source = {}
#     for p in pages:
#         src = p.metadata.get("source", "unknown")
#         pages_by_source.setdefault(src, []).append(p)

#     merged_docs = []
#     for src, src_pages in pages_by_source.items():
#         # sort by original page order just in case
#         src_pages.sort(key=lambda d: d.metadata.get("page", 0))

#         combined_text = ""
#         page_marker_offsets = []  # (char_offset_in_combined_text, page_number_1_based)

#         for p in src_pages:
#             page_num = int(p.metadata.get("page", 0)) + 1  # 1-based
#             page_marker_offsets.append((len(combined_text), page_num))
#             combined_text += p.page_content + "\n"

#         # Find every heading-like line and its char offset in combined_text.
#         headings = [
#             (m.start(), m.group(1).strip())
#             for m in HEADING_PATTERN.finditer(combined_text)
#         ]

#         merged_docs.append(
#             Document(
#                 page_content=combined_text,
#                 metadata={
#                     "source": src,
#                     "page_offsets": page_marker_offsets,
#                     "headings": headings,
#                 },
#             )
#         )

#     # FIX: Policy docs are structured as numbered clauses (1., 2., 3. ... /
#     # Code – ExclXX). Default separators (paragraph/sentence) don't respect
#     # these boundaries, so a chunk can start MID-CLAUSE (e.g. "the expiry of
#     # 48 months...") without the keywords that identify what it's about
#     # ("Pre-Existing Disease"). This makes the reranker discard the correct
#     # chunk because it lexically looks unrelated to the question. We use a
#     # smaller chunk_size for finer granularity, and separately re-inject the
#     # nearest parent heading into every chunk below.
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=100,
#         add_start_index=True,
#         separators=["\n\n", "\n", ". ", " ", ""],
#     )

#     chunks = splitter.split_documents(merged_docs)

#     # Map each chunk's start_index back to the correct page number, AND
#     # prefix the chunk text with its nearest preceding heading so the
#     # embedding + reranker always "know" what clause the chunk belongs to,
#     # no matter where the char-based split landed.
#     for chunk in chunks:
#         offsets = chunk.metadata.pop("page_offsets", [])
#         headings = chunk.metadata.pop("headings", [])
#         start = chunk.metadata.get("start_index", 0)

#         page_num = "Unknown"
#         for offset, pnum in offsets:
#             if offset <= start:
#                 page_num = pnum
#             else:
#                 break
#         chunk.metadata["page"] = page_num

#         # Nearest heading at or before this chunk's start_index
#         nearest_heading = None
#         for offset, heading_text in headings:
#             if offset <= start:
#                 nearest_heading = heading_text
#             else:
#                 break

#         if nearest_heading and not chunk.page_content.startswith(nearest_heading):
#             chunk.metadata["section"] = nearest_heading
#             chunk.page_content = f"[Section: {nearest_heading}]\n{chunk.page_content}"

#     print(f"Total chunks created: {len(chunks)}")
#     return chunks


# def _remove_readonly(func, path, _):
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except Exception as e:
#         print(f"Warning: could not force delete {path}: {e}")


# def create_vector_store(chunks):
#     if os.path.exists(CHROMA_PATH):
#         try:
#             shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Warning: Could not delete old DB folder: {e}")

#     print("Creating Chroma DB...")
#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )
#     print("Vector DB created successfully!")


# def main():
#     chunks = load_and_split_documents()
#     create_vector_store(chunks)


# if __name__ == "__main__":
#     main()




# import os
# import re
# import shutil
# import time
# import stat
# from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain_ollama import OllamaEmbeddings
# from langchain_core.documents import Document

# DATA_PATH = "docs"
# CHROMA_PATH = "chroma_db"

# # Ollama Embedding Model
# embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# # ------------------------------------------------------------------
# # Matches short, title-like lines such as:
# #   "1. Pre-Existing Diseases (Code – Excl01)"
# #   "2. Specified Disease/Procedure Waiting Period (Code – Excl02)"
# #   "A. Waiting Periods (Only Applicable for Gold & Senior Citizen Plans)"
# #   "9. What Policy Does Not Cover"
# # Used to find the nearest parent heading for any chunk, so short chunks
# # that get cut mid-clause (e.g. "the expiry of 48 months...") still carry
# # their topic ("Pre-Existing Diseases") in the text that gets embedded.
# # ------------------------------------------------------------------
# HEADING_PATTERN = re.compile(
#     r"(?m)^((?:[A-Z]\.|\d{1,2}\.)\s+[A-Z][A-Za-z0-9 /\-\u2013\u2014\(\)&,\.']{3,90})\s*$"
# )


# def load_and_split_documents():
#     print("Loading PDFs page by page...")
#     loader = DirectoryLoader(
#         DATA_PATH,
#         glob="**/*.pdf",
#         loader_cls=PyPDFLoader,
#         show_progress=True,
#     )
#     pages = loader.load()
#     print(f"Total pages loaded: {len(pages)}")

#     # ------------------------------------------------------------------
#     # FIX: PyPDFLoader gives ONE Document per page. If we split each page
#     # separately, a clause/table that spans the bottom of page N into the
#     # top of page N+1 gets cut in half and neither half matches queries
#     # well. Instead we merge consecutive pages of the SAME source file
#     # into one long text (with a page marker per page), then split that.
#     # We keep the page marker in the text itself so each resulting chunk
#     # can be reliably mapped back to a page number.
#     # ------------------------------------------------------------------
#     pages_by_source = {}
#     for p in pages:
#         src = p.metadata.get("source", "unknown")
#         pages_by_source.setdefault(src, []).append(p)

#     merged_docs = []
#     for src, src_pages in pages_by_source.items():
#         # sort by original page order just in case
#         src_pages.sort(key=lambda d: d.metadata.get("page", 0))

#         combined_text = ""
#         page_marker_offsets = []  # (char_offset_in_combined_text, page_number_1_based)

#         for p in src_pages:
#             page_num = int(p.metadata.get("page", 0)) + 1  # 1-based
#             page_marker_offsets.append((len(combined_text), page_num))
#             combined_text += p.page_content + "\n"

#         # Find every heading-like line and its char offset in combined_text.
#         headings = [
#             (m.start(), m.group(1).strip())
#             for m in HEADING_PATTERN.finditer(combined_text)
#         ]

#         merged_docs.append(
#             Document(
#                 page_content=combined_text,
#                 metadata={
#                     "source": src,
#                     "page_offsets": page_marker_offsets,
#                     "headings": headings,
#                 },
#             )
#         )

#     # FIX: Policy docs are structured as numbered clauses (1., 2., 3. ... /
#     # Code – ExclXX). Default separators (paragraph/sentence) don't respect
#     # these boundaries, so a chunk can start MID-CLAUSE (e.g. "the expiry of
#     # 48 months...") without the keywords that identify what it's about
#     # ("Pre-Existing Disease"). This makes the reranker discard the correct
#     # chunk because it lexically looks unrelated to the question. We use a
#     # smaller chunk_size for finer granularity, and separately re-inject the
#     # nearest parent heading into every chunk below.
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=800,
#         chunk_overlap=250,
#         add_start_index=True,
#         separators=["\n\n", "\n", ". ", " ", ""],
#     )

#     chunks = splitter.split_documents(merged_docs)

#     # Map each chunk's start_index back to the correct page number, AND
#     # prefix the chunk text with its nearest preceding heading so the
#     # embedding + reranker always "know" what clause the chunk belongs to,
#     # no matter where the char-based split landed.
#     for chunk in chunks:
#         offsets = chunk.metadata.pop("page_offsets", [])
#         headings = chunk.metadata.pop("headings", [])
#         start = chunk.metadata.get("start_index", 0)

#         page_num = "Unknown"
#         page_start_offset = 0
#         for offset, pnum in offsets:
#             if offset <= start:
#                 page_num = pnum
#                 page_start_offset = offset
#             else:
#                 break
#         chunk.metadata["page"] = page_num

#         # ------------------------------------------------------------
#         # FIX: Only consider headings that fall on the SAME PAGE as this
#         # chunk (offset between page_start_offset and start). Without this,
#         # a numbered clause heading from a PREVIOUS page/section (e.g.
#         # "25. REGULATIONS") gets incorrectly carried onto completely
#         # unrelated content that starts a new page with no heading of its
#         # own (e.g. the "Table of Benefits" page, which is a table, not a
#         # numbered clause) — causing wrong section attribution and citation
#         # confusion downstream.
#         # ------------------------------------------------------------
#         nearest_heading = None
#         for offset, heading_text in headings:
#             if page_start_offset <= offset <= start:
#                 nearest_heading = heading_text
#             elif offset > start:
#                 break

#         if nearest_heading and not chunk.page_content.startswith(nearest_heading):
#             chunk.metadata["section"] = nearest_heading
#             chunk.page_content = f"[Section: {nearest_heading}]\n{chunk.page_content}"

#     print(f"Total chunks created: {len(chunks)}")
#     return chunks


# def _remove_readonly(func, path, _):
#     try:
#         os.chmod(path, stat.S_IWRITE)
#         func(path)
#     except Exception as e:
#         print(f"Warning: could not force delete {path}: {e}")


# def create_vector_store(chunks):
#     if os.path.exists(CHROMA_PATH):
#         try:
#             shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
#             time.sleep(1.5)
#         except Exception as e:
#             print(f"Warning: Could not delete old DB folder: {e}")

#     print("Creating Chroma DB...")
#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )
#     print("Vector DB created successfully!")


# def main():
#     chunks = load_and_split_documents()
#     create_vector_store(chunks)


# if __name__ == "__main__":
#     main()

import os
import re
import shutil
import time
import stat
import fitz  # PyMuPDF
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

DATA_PATH = "docs"
CHROMA_PATH = "chroma_db"

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

HEADING_PATTERN = re.compile(
    r"(?m)^((?:[A-Z]\.|\d{1,2}\.)\s+[A-Z][A-Za-z0-9 /\-\u2013\u2014\(\)&,\.']{3,90})\s*$"
)

def load_and_split_documents():
    print("Loading PDFs with PyMuPDF for precise bbox tracking...")
    merged_docs = []
    
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        return []

    for file_name in os.listdir(DATA_PATH):
        if not file_name.endswith(".pdf"):
            continue
        src_path = os.path.join(DATA_PATH, file_name)
        doc = fitz.open(src_path)
        
        combined_text = ""
        page_marker_offsets = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text("text")
            page_marker_offsets.append((len(combined_text), page_num + 1))
            combined_text += page_text + "\n"
            
        headings = [
            (m.start(), m.group(1).strip())
            for m in HEADING_PATTERN.finditer(combined_text)
        ]

        merged_docs.append(
            Document(
                page_content=combined_text,
                metadata={
                    "source": file_name,
                    "page_offsets": page_marker_offsets,
                    "headings": headings,
                },
            )
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=250,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(merged_docs)

    for chunk in chunks:
        offsets = chunk.metadata.pop("page_offsets", [])
        headings = chunk.metadata.pop("headings", [])
        start = chunk.metadata.get("start_index", 0)

        page_num = 1
        page_start_offset = 0
        for offset, pnum in offsets:
            if offset <= start:
                page_num = pnum
                page_start_offset = offset
            else:
                break
        chunk.metadata["page"] = page_num

        nearest_heading = None
        for offset, heading_text in headings:
            if page_start_offset <= offset <= start:
                nearest_heading = heading_text
            elif offset > start:
                break

        if nearest_heading:
            chunk.metadata["section"] = nearest_heading
            chunk.page_content = f"[Section: {nearest_heading}]\n{chunk.page_content}"

    print(f"Total chunks created: {len(chunks)}")
    return chunks

def _remove_readonly(func, path, _):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Warning: could not force delete {path}: {e}")

def create_vector_store(chunks):
    if os.path.exists(CHROMA_PATH):
        try:
            shutil.rmtree(CHROMA_PATH, onerror=_remove_readonly)
            time.sleep(1.5)
        except Exception as e:
            print(f"Warning: Could not delete old DB folder: {e}")

    print("Creating Chroma DB...")
    Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_PATH,
    )
    print("Vector DB created successfully!")

def main():
    chunks = load_and_split_documents()
    if chunks:
        create_vector_store(chunks)

if __name__ == "__main__":
    main()