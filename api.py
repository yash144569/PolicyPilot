
# ---->
# import os
# import gc
# import shutil
# import time
# import traceback
# import chromadb  # <--- सबसे ज़रूरी चीज़ यहाँ इम्पोर्ट कर दी है!

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# import ingestion
# import query
# from query import ask_policy

# app = FastAPI(
#     title="PolicyPilot AI - Insurance Legal RAG API",
#     description="Backend API for uploading policy PDFs and querying via RAG",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DOCS_DIR = "docs"
# os.makedirs(DOCS_DIR, exist_ok=True)

# class QuestionRequest(BaseModel):
#     question: str

# @app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
# async def upload_policy_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported.")
#     try:
#         # 1. पुरानी PDF डिलीट करना
#         for old_file in os.listdir(DOCS_DIR):
#             file_path = os.path.join(DOCS_DIR, old_file)
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)

#         # 2. नई PDF सेव करना
#         new_file_path = os.path.join(DOCS_DIR, file.filename)
#         with open(new_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         fixed_db_name = "chroma_db"
#         ingestion.CHROMA_PATH = fixed_db_name
        
#         # 🔥 THE ULTIMATE FIX: ChromaDB के इंटरनल कैश और लॉक को तबाह करना 🔥
#         query.retriever = None
#         query.db = None
        
#         # यह लाइन Chroma को मजबूर करेगी कि वो SQLite डेटाबेस को पूरी तरह आज़ाद कर दे
#         chromadb.api.client.SharedSystemClient.clear_system_cache() 
        
#         gc.collect()  # मेमोरी से कचरा साफ़ करो
#         time.sleep(1) # OS को फाइल लॉक छोड़ने के लिए 1 सेकंड का टाइम दो
        
#         print(f"Running ingestion... Re-creating DB folder: {fixed_db_name}")
#         ingestion.main() 
        
#         # 3. Query इंजन को दोबारा नए डेटाबेस से कनेक्ट करो
#         query.CHROMA_PATH = fixed_db_name
#         query.db = query.Chroma(
#             persist_directory=fixed_db_name,
#             embedding_function=query.embedding_model,
#         )
#         query.retriever = query.db.as_retriever(
#             search_type="mmr",
#             search_kwargs={
#                 "k": 15,          # अब 5 की जगह टॉप 8 अलग-अलग चंक्स लाएगा
#                 "fetch_k": 60    # डेटाबेस से 30 निकालेगा, और उनमें से 8 सबसे बेस्ट/अलग छांटेगा
#             },
#         )
        
#         return {
#             "status": "success",
#             "filename": file.filename,
#             "message": "Policy PDF successfully uploaded and connected!"
#         }
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


# @app.post("/api/ask", summary="Ask any question regarding the uploaded policy")
# async def ask_question(req: QuestionRequest):
#     try:
#         result = ask_policy(req.question)
#         return {"status": "success", "data": result}
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/summary", summary="Get auto-generated summary based on policy type")
# async def get_policy_summary():
#     try:
#         # 1. AI से पूछो कि पॉलिसी किस टाइप की है
#         policy_type = query.detect_policy_type()
#         print(f"Detected Policy Type: {policy_type}")

#         # 2. कॉमन सवाल निकालो 
#         common_questions = query.POLICY_QUESTIONS.get("Common", [])

#         # 3. उस खास टाइप के सवाल निकालो
#         specific_questions = query.POLICY_QUESTIONS.get(policy_type, query.POLICY_QUESTIONS["Unknown"])
        
#         # 4. दोनों लिस्ट को आपस में जोड़ दो!
#         questions_to_ask = common_questions + specific_questions
        
#         summary_results = []
        
#         # 5. सारे सवालों के जवाब निकालो
#         for item in questions_to_ask:
#             label = item[0]     
#             question = item[1]  

#             print(f"Generating summary for: {label}...")
#             res = ask_policy(question)
            
#             if isinstance(res, dict):
#                 ans = res.get("answer", "")
#                 src = res.get("sources", [])
#             elif isinstance(res, (tuple, list)):
#                 ans = res[0] if len(res) > 0 else ""
#                 src = res[1] if len(res) > 1 else []
#             else:
#                 ans = str(res)
#                 src = []

#             summary_results.append({
#                 "label": label,
#                 "question": question,
#                 "answer": ans,
#                 "sources": src
#             })
            
#         return {
#             "status": "success", 
#             "policy_type_detected": policy_type, 
#             "summary": summary_results
#         }
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# import os
# import gc
# import shutil
# import time
# import traceback
# import chromadb

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# import ingestion
# import query
# from query import ask_policy

# app = FastAPI(
#     title="PolicyPilot AI - Insurance Legal RAG API",
#     description="Backend API for uploading policy PDFs and querying via RAG",
#     version="1.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=False,   # NOTE: '*' + credentials=True is invalid per CORS spec
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DOCS_DIR = "docs"
# os.makedirs(DOCS_DIR, exist_ok=True)


# class QuestionRequest(BaseModel):
#     question: str


# @app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
# async def upload_policy_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported.")
#     try:
#         # 1. Purani PDF delete karna
#         for old_file in os.listdir(DOCS_DIR):
#             file_path = os.path.join(DOCS_DIR, old_file)
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)

#         # 2. Nayi PDF save karna
#         new_file_path = os.path.join(DOCS_DIR, file.filename)
#         with open(new_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         fixed_db_name = "chroma_db"
#         ingestion.CHROMA_PATH = fixed_db_name

#         # Chroma ke internal cache/lock ko release karna
#         query.db = None
#         chromadb.api.client.SharedSystemClient.clear_system_cache()

#         gc.collect()
#         time.sleep(1)

#         print(f"Running ingestion... Re-creating DB folder: {fixed_db_name}")
#         ingestion.main()

#         # 3. Query engine ko dobara naye DB se connect karo
#         query.CHROMA_PATH = fixed_db_name
#         query.db = query.Chroma(
#             persist_directory=fixed_db_name,
#             embedding_function=query.embedding_model,
#         )

#         return {
#             "status": "success",
#             "filename": file.filename,
#             "message": "Policy PDF successfully uploaded and connected!"
#         }
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


# @app.post("/api/ask", summary="Ask any question regarding the uploaded policy")
# async def ask_question(req: QuestionRequest):
#     try:
#         result = ask_policy(req.question)
#         return {"status": "success", "data": result}
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# @app.get("/api/summary", summary="Get auto-generated summary based on policy type")
# async def get_policy_summary():
#     try:
#         policy_type = query.detect_policy_type()
#         print(f"Detected Policy Type: {policy_type}")

#         common_questions = query.POLICY_QUESTIONS.get("Common", [])
#         specific_questions = query.POLICY_QUESTIONS.get(policy_type, query.POLICY_QUESTIONS["Unknown"])

#         questions_to_ask = common_questions + specific_questions

#         summary_results = []

#         for label, question in questions_to_ask:
#             print(f"Generating summary for: {label}...")
#             res = ask_policy(question)

#             if isinstance(res, dict):
#                 ans = res.get("answer", "")
#                 src = res.get("sources", [])
#             elif isinstance(res, (tuple, list)):
#                 ans = res[0] if len(res) > 0 else ""
#                 src = res[1] if len(res) > 1 else []
#             else:
#                 ans = str(res)
#                 src = []

#             summary_results.append({
#                 "label": label,
#                 "question": question,
#                 "answer": ans,
#                 "sources": src
#             })

#         return {
#             "status": "success",
#             "policy_type_detected": policy_type,
#             "summary": summary_results
#         }

#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

from dotenv import load_dotenv
load_dotenv()

import os
import gc
import shutil
import time
import traceback
import chromadb

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import ingestion
import query
from query import ask_policy

app = FastAPI(
    title="PolicyPilot AI - Insurance Legal RAG API",
    description="Backend API for uploading policy PDFs and querying via RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # NOTE: '*' + credentials=True is invalid per CORS spec
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCS_DIR = "docs"
os.makedirs(DOCS_DIR, exist_ok=True)


class QuestionRequest(BaseModel):
    question: str


@app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
async def upload_policy_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    try:
        # 1. Purani PDF delete karna
        for old_file in os.listdir(DOCS_DIR):
            file_path = os.path.join(DOCS_DIR, old_file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

        # 2. Nayi PDF save karna
        new_file_path = os.path.join(DOCS_DIR, file.filename)
        with open(new_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        fixed_db_name = "chroma_db"
        ingestion.CHROMA_PATH = fixed_db_name

        # Chroma ke internal cache/lock ko release karna
        query.db = None
        chromadb.api.client.SharedSystemClient.clear_system_cache()

        gc.collect()
        time.sleep(1)

        print(f"Running ingestion... Re-creating DB folder: {fixed_db_name}")
        ingestion.main()

        # 3. Query engine ko dobara naye DB se connect karo
        query.CHROMA_PATH = fixed_db_name
        query.db = query.Chroma(
            persist_directory=fixed_db_name,
            embedding_function=query.embedding_model,
        )

        return {
            "status": "success",
            "filename": file.filename,
            "message": "Policy PDF successfully uploaded and connected!"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.post("/api/ask", summary="Ask any question regarding the uploaded policy")
async def ask_question(req: QuestionRequest):
    try:
        result = ask_policy(req.question)
        return {"status": "success", "data": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary", summary="Get auto-generated summary based on policy type")
async def get_policy_summary():
    try:
        policy_type = query.detect_policy_type()
        print(f"Detected Policy Type: {policy_type}")

        common_questions = query.POLICY_QUESTIONS.get("Common", [])
        specific_questions = query.POLICY_QUESTIONS.get(policy_type, query.POLICY_QUESTIONS["Unknown"])

        questions_to_ask = common_questions + specific_questions

        summary_results = []

        for label, question in questions_to_ask:
            print(f"Generating summary for: {label}...")
            res = ask_policy(question)

            if isinstance(res, dict):
                ans = res.get("answer", "")
                src = res.get("sources", [])
            elif isinstance(res, (tuple, list)):
                ans = res[0] if len(res) > 0 else ""
                src = res[1] if len(res) > 1 else []
            else:
                ans = str(res)
                src = []

            summary_results.append({
                "label": label,
                "question": question,
                "answer": ans,
                "sources": src
            })

        return {
            "status": "success",
            "policy_type_detected": policy_type,
            "summary": summary_results
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))