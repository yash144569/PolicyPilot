
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




import os
import re
import shutil
import time
import stat
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

DATA_PATH = "docs"
CHROMA_PATH = "chroma_db"

# Ollama Embedding Model
embedding_model = OllamaEmbeddings(model="nomic-embed-text")

# ------------------------------------------------------------------
# Matches short, title-like lines such as:
#   "1. Pre-Existing Diseases (Code – Excl01)"
#   "2. Specified Disease/Procedure Waiting Period (Code – Excl02)"
#   "A. Waiting Periods (Only Applicable for Gold & Senior Citizen Plans)"
#   "9. What Policy Does Not Cover"
# Used to find the nearest parent heading for any chunk, so short chunks
# that get cut mid-clause (e.g. "the expiry of 48 months...") still carry
# their topic ("Pre-Existing Diseases") in the text that gets embedded.
# ------------------------------------------------------------------
HEADING_PATTERN = re.compile(
    r"(?m)^((?:[A-Z]\.|\d{1,2}\.)\s+[A-Z][A-Za-z0-9 /\-\u2013\u2014\(\)&,\.']{3,90})\s*$"
)


def load_and_split_documents():
    print("Loading PDFs page by page...")
    loader = DirectoryLoader(
        DATA_PATH,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
        show_progress=True,
    )
    pages = loader.load()
    print(f"Total pages loaded: {len(pages)}")

    # ------------------------------------------------------------------
    # FIX: PyPDFLoader gives ONE Document per page. If we split each page
    # separately, a clause/table that spans the bottom of page N into the
    # top of page N+1 gets cut in half and neither half matches queries
    # well. Instead we merge consecutive pages of the SAME source file
    # into one long text (with a page marker per page), then split that.
    # We keep the page marker in the text itself so each resulting chunk
    # can be reliably mapped back to a page number.
    # ------------------------------------------------------------------
    pages_by_source = {}
    for p in pages:
        src = p.metadata.get("source", "unknown")
        pages_by_source.setdefault(src, []).append(p)

    merged_docs = []
    for src, src_pages in pages_by_source.items():
        # sort by original page order just in case
        src_pages.sort(key=lambda d: d.metadata.get("page", 0))

        combined_text = ""
        page_marker_offsets = []  # (char_offset_in_combined_text, page_number_1_based)

        for p in src_pages:
            page_num = int(p.metadata.get("page", 0)) + 1  # 1-based
            page_marker_offsets.append((len(combined_text), page_num))
            combined_text += p.page_content + "\n"

        # Find every heading-like line and its char offset in combined_text.
        headings = [
            (m.start(), m.group(1).strip())
            for m in HEADING_PATTERN.finditer(combined_text)
        ]

        merged_docs.append(
            Document(
                page_content=combined_text,
                metadata={
                    "source": src,
                    "page_offsets": page_marker_offsets,
                    "headings": headings,
                },
            )
        )

    # FIX: Policy docs are structured as numbered clauses (1., 2., 3. ... /
    # Code – ExclXX). Default separators (paragraph/sentence) don't respect
    # these boundaries, so a chunk can start MID-CLAUSE (e.g. "the expiry of
    # 48 months...") without the keywords that identify what it's about
    # ("Pre-Existing Disease"). This makes the reranker discard the correct
    # chunk because it lexically looks unrelated to the question. We use a
    # smaller chunk_size for finer granularity, and separately re-inject the
    # nearest parent heading into every chunk below.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=250,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_documents(merged_docs)

    # Map each chunk's start_index back to the correct page number, AND
    # prefix the chunk text with its nearest preceding heading so the
    # embedding + reranker always "know" what clause the chunk belongs to,
    # no matter where the char-based split landed.
    for chunk in chunks:
        offsets = chunk.metadata.pop("page_offsets", [])
        headings = chunk.metadata.pop("headings", [])
        start = chunk.metadata.get("start_index", 0)

        page_num = "Unknown"
        page_start_offset = 0
        for offset, pnum in offsets:
            if offset <= start:
                page_num = pnum
                page_start_offset = offset
            else:
                break
        chunk.metadata["page"] = page_num

        # ------------------------------------------------------------
        # FIX: Only consider headings that fall on the SAME PAGE as this
        # chunk (offset between page_start_offset and start). Without this,
        # a numbered clause heading from a PREVIOUS page/section (e.g.
        # "25. REGULATIONS") gets incorrectly carried onto completely
        # unrelated content that starts a new page with no heading of its
        # own (e.g. the "Table of Benefits" page, which is a table, not a
        # numbered clause) — causing wrong section attribution and citation
        # confusion downstream.
        # ------------------------------------------------------------
        nearest_heading = None
        for offset, heading_text in headings:
            if page_start_offset <= offset <= start:
                nearest_heading = heading_text
            elif offset > start:
                break

        if nearest_heading and not chunk.page_content.startswith(nearest_heading):
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
    create_vector_store(chunks)


if __name__ == "__main__":
    main()