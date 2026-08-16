# import os
# import time
# import ingestion
# import shutil
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware

# # आपके खुद के बनाए हुए मॉड्यूल्स को इम्पोर्ट कर रहे हैं
# import ingestion
# from query import ask_policy, FIXED_QUESTIONS

# # ---------------------------------------------------------------------------
# # 1. FastAPI App Setup & CORS Configuration
# # ---------------------------------------------------------------------------
# app = FastAPI(
#     title="PolicyPilot AI - Insurance Legal RAG API",
#     description="Backend API for uploading policy PDFs and querying via RAG (LangChain + ChromaDB + Llama 3.2)",
#     version="1.0.0"
# )

# # CORS इनेबल कर रहे हैं ताकि MERN / Angular फ्रंटएंड बिना किसी एरर के इस API को कॉल कर सके
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # प्रोडक्शन में आप अपने फ्रंटएंड का URL डाल सकते हैं
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# DOCS_DIR = "docs"
# os.makedirs(DOCS_DIR, exist_ok=True)

# # ---------------------------------------------------------------------------
# # 2. Pydantic Request Models
# # ---------------------------------------------------------------------------
# class QuestionRequest(BaseModel):
#     question: str


# # ===========================================================================
# # ENDPOINT 1: PDF Upload & Automatic Vector DB Creation
# # ===========================================================================
# # @app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
# # async def upload_policy_pdf(file: UploadFile = File(...)):
# #     """
# #     1. Removes old PDFs from 'docs/' folder.
# #     2. Saves user's uploaded PDF into 'docs/'.
# #     3. Automatically runs 'ingestion.main()' to chunk and build ChromaDB.
# #     """
# #     if not file.filename.endswith(".pdf"):
# #         raise HTTPException(status_code=400, detail="Only PDF files are supported.")

# #     try:
# #         # Step 1: docs/ फोल्डर की पुरानी फाइल्स साफ करें
# #         for old_file in os.listdir(DOCS_DIR):
# #             file_path = os.path.join(DOCS_DIR, old_file)
# #             if os.path.isfile(file_path):
# #                 os.unlink(file_path)

# #         # Step 2: यूज़र की नई PDF को docs/ फोल्डर में सेव करें
# #         new_file_path = os.path.join(DOCS_DIR, file.filename)
# #         with open(new_file_path, "wb") as buffer:
# #             shutil.copyfileobj(file.file, buffer)

# #         # Step 3: आपका पुराना ingestion.py रन करें (नया chroma_db बन जाएगा)
# #         print(f"File '{file.filename}' saved to 'docs/'. Running ingestion pipeline...")
# #         ingestion.main()
        
# #         return {
# #             "status": "success",
# #             "filename": file.filename,
# #             "message": "Policy PDF successfully uploaded to 'docs/' and Vector DB updated!"
# #         }
# #     except Exception as e:
# #         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# @app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
# async def upload_policy_pdf(file: UploadFile = File(...)):
#     if not file.filename.endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported.")

#     try:
#         # 1. docs/ फोल्डर की पुरानी फाइल्स साफ करें
#         for old_file in os.listdir(DOCS_DIR):
#             file_path = os.path.join(DOCS_DIR, old_file)
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)

#         # 2. यूज़र की नई PDF को docs/ फोल्डर में सेव करें
#         new_file_path = os.path.join(DOCS_DIR, file.filename)
#         with open(new_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # 3. हर बार एक नया डेटाबेस फोल्डर बनाएंगे (ताकि Read-Only एरर कभी न आए!)
#         new_db_name = f"chroma_db_{int(time.time())}"
#         ingestion.CHROMA_PATH = new_db_name
        
#         print(f"Running ingestion... New DB folder: {new_db_name}")
#         ingestion.main()
        
#         return {
#             "status": "success",
#             "filename": file.filename,
#             "message": "Policy PDF successfully uploaded and new DB created!"
#         }
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# # ===========================================================================
# # ENDPOINT 2: Ask Question (Chat Interface)
# # ===========================================================================
# @app.post("/api/ask", summary="Ask any question regarding the uploaded policy")
# def ask_insurance_question(req: QuestionRequest):
#     """
#     Sends user query to LangChain RAG pipeline with Smart Query Enhancement
#     and returns verified answers with Page/Section citations.
#     """
#     try:
#         answer_text, sources = ask_policy(req.question)
#         return {
#             "status": "success",
#             "question": req.question,
#             "answer": answer_text.strip(),
#             "sources": [{"source": src, "page": page} for src, page in sources]
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error querying policy: {str(e)}")


# # ===========================================================================
# # ENDPOINT 3: Policy Summary Dashboard (Auto-Generated Summary)
# # ===========================================================================
# @app.get("/api/summary", summary="Get auto-generated summary of key policy terms")
# def get_policy_summary():
#     """
#     Runs fixed questions to extract benefits, waiting periods, room rent caps, etc.
#     Useful for displaying a dashboard as soon as the PDF is uploaded.
#     """
#     try:
#         summary_data = []
#         for label, question in FIXED_QUESTIONS:
#             answer_text, sources = ask_policy(question)
#             summary_data.append({
#                 "label": label,
#                 "question": question,
#                 "answer": answer_text.strip(),
#                 "sources": [{"source": src, "page": page} for src, page in sources]
#             })
#         return {
#             "status": "success",
#             "summary": summary_data
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


# # ===========================================================================
# # ENDPOINT 4: Health Check
# # ===========================================================================
# @app.get("/", summary="API Status Check")
# def root():
#     return {"status": "running", "message": "PolicyPilot AI Backend API is ready."}

# import os
# import shutil
# import time
# import traceback
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# # तेरे बनाए मॉड्यूल्स
# import ingestion
# import query
# from query import ask_policy, FIXED_QUESTIONS

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
#         # 1. पुरानी PDF डिलीट करें
#         for old_file in os.listdir(DOCS_DIR):
#             file_path = os.path.join(DOCS_DIR, old_file)
#             if os.path.isfile(file_path):
#                 os.unlink(file_path)

#         # 2. नई PDF सेव करें
#         new_file_path = os.path.join(DOCS_DIR, file.filename)
#         with open(new_file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         # 3. नया डेटाबेस फोल्डर बनाएं ताकि Read-Only Error न आए
#         new_db_name = f"chroma_db_{int(time.time())}"
#         ingestion.CHROMA_PATH = new_db_name
        
#         print(f"Running ingestion... New DB folder: {new_db_name}")
#         ingestion.main()
        
#         # 4. सबसे ज़रूरी: query.py को भी बता दें कि अब नए DB से जवाब देना है!
#         query.CHROMA_PATH = new_db_name
#         query.db = query.Chroma(
#             persist_directory=new_db_name,
#             embedding_function=query.embedding_model,
#         )
#         query.retriever = query.db.as_retriever(
#             search_type="similarity",
#             search_kwargs={"k": 5},
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


# # @app.get("/api/summary", summary="Get auto-generated summary of key policy terms")
# # async def get_policy_summary():
# #     try:
# #         summary_results = []
# #         for item in FIXED_QUESTIONS:
# #             print(f"Generating summary for: {item['label']}...")
# #             res = ask_policy(item["question"])
# #             summary_results.append({
# #                 "label": item["label"],
# #                 "question": item["question"],
# #                 "answer": res["answer"],
# #                 "sources": res["sources"]
# #             })
# #         return {"status": "success", "summary": summary_results}
# #     except Exception as e:
# #         traceback.print_exc()
# #         raise HTTPException(status_code=500, detail=str(e))

# # @app.get("/api/summary", summary="Get auto-generated summary of key policy terms")
# # async def get_policy_summary():
# #     try:
# #         summary_results = []
# #         for item in FIXED_QUESTIONS:
# #             # 1. item चाहे dict हो या tuple, सही से label और question निकालो
# #             if isinstance(item, dict):
# #                 label = item.get("label", "Policy Detail")
# #                 question = item.get("question", "")
# #             else:
# #                 label = item[0]     
# #                 question = item[1]  

# #             print(f"Generating summary for: {label}...")
# #             res = ask_policy(question)
            
# #             # 2. res चाहे dict हो, tuple हो या string, कभी क्रैश नहीं होने देंगे!
# #             if isinstance(res, dict):
# #                 ans = res.get("answer", "")
# #                 src = res.get("sources", [])
# #             elif isinstance(res, (tuple, list)):
# #                 ans = res[0] if len(res) > 0 else ""
# #                 src = res[1] if len(res) > 1 else []
# #             else:
# #                 ans = str(res)
# #                 src = []

# #             summary_results.append({
# #                 "label": label,
# #                 "question": question,
# #                 "answer": ans,
# #                 "sources": src
# #             })
# #         return {"status": "success", "summary": summary_results}
# #     except Exception as e:
# #         traceback.print_exc()
# #         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/api/summary", summary="Get auto-generated summary based on policy type")
# async def get_policy_summary():
#     try:
#         # 1. AI से पूछो कि पॉलिसी किस टाइप की है
#         policy_type = query.detect_policy_type()
#         print(f"Detected Policy Type: {policy_type}")

#         # 2. कॉमन सवाल निकालो (जो हर पॉलिसी में पूछे जाएंगे)
#         common_questions = query.POLICY_QUESTIONS.get("Common", [])

#         # 3. उस खास टाइप के सवाल निकालो
#         specific_questions = query.POLICY_QUESTIONS.get(policy_type, query.POLICY_QUESTIONS["Unknown"])
        
#         # 4. दोनों लिस्ट को आपस में जोड़ दो!
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
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# import os
# import gc
# import shutil
# import time
# import traceback
# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel

# import ingestion
# import query
# from query import ask_policy  # <-- देखो, यहाँ से FIXED_QUESTIONS हटा दिया है!

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

# # @app.post("/api/upload", summary="Upload a new Policy PDF and re-create Vector DB")
# # async def upload_policy_pdf(file: UploadFile = File(...)):
# #     if not file.filename.endswith(".pdf"):
# #         raise HTTPException(status_code=400, detail="Only PDF files are supported.")
# #     try:
# #         for old_file in os.listdir(DOCS_DIR):
# #             file_path = os.path.join(DOCS_DIR, old_file)
# #             if os.path.isfile(file_path):
# #                 os.unlink(file_path)

# #         new_file_path = os.path.join(DOCS_DIR, file.filename)
# #         with open(new_file_path, "wb") as buffer:
# #             shutil.copyfileobj(file.file, buffer)

# #         new_db_name = f"chroma_db_{int(time.time())}"
# #         ingestion.CHROMA_PATH = new_db_name
        
# #         print(f"Running ingestion... New DB folder: {new_db_name}")
# #         ingestion.main()
        
# #         query.CHROMA_PATH = new_db_name
# #         query.db = query.Chroma(
# #             persist_directory=new_db_name,
# #             embedding_function=query.embedding_model,
# #         )
# #         query.retriever = query.db.as_retriever(
# #             search_type="similarity",
# #             search_kwargs={"k": 5},
# #         )
        
# #         return {
# #             "status": "success",
# #             "filename": file.filename,
# #             "message": "Policy PDF successfully uploaded and connected!"
# #         }
# #     except Exception as e:
# #         traceback.print_exc()
# #         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

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
        
#         # 🔥 THE MAGICAL FIX: SQLite का फाइल लॉक हटाना 🔥
#         # Ingestion से पहले पुरानी DB का कनेक्शन तोड़ दो
#         query.retriever = None
#         query.db = None
#         gc.collect()  # मेमोरी से कचरा साफ़ करो (फाइल कनेक्शन आज़ाद हो जाएगा)
#         time.sleep(1) # OS को फाइल लॉक छोड़ने के लिए 1 सेकंड का टाइम दो
        
#         print(f"Running ingestion... Re-creating DB folder: {fixed_db_name}")
#         ingestion.main() 
        
#         # 3. Query इंजन को दोबारा नए डेटाबेस से कनेक्ट करो
#         query.CHROMA_PATH = fixed_db_name
#         query.db = query.Chroma(
#             persist_directory=fixed_db_name,
#             embedding_function=query.embedding_model,
#         )
#         query.retriever = query.db.as_retriever(
#             search_kwargs={"k": 5},
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
        
#         # 4. दोनों लिस्ट को आपस में जोड़ दो!
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