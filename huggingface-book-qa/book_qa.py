import os
import pickle
import numpy as np
from typing import List, Tuple
from pathlib import Path
import PyPDF2
from sentence_transformers import SentenceTransformer, util

class BookKnowledgeBase:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        self.documents = []  # List of text chunks
        self.embeddings = None
        self.book_name = None
        self.embeddings_file = "embeddings/book_embeddings.pkl"
        self.documents_file = "embeddings/book_documents.pkl"
        os.makedirs("embeddings", exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            print(f"Extracted {len(pdf_reader.pages)} pages")
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text
    
    def extract_text_from_file(self, file_path: str) -> str:
        if file_path.endswith('.pdf'):
            return self.extract_text_from_pdf(file_path)
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                return ""
    
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        return chunks
    
    def load_book(self, file_path: str):
        self.book_name = Path(file_path).stem
        
        print(f"\nLoading book: {self.book_name}")
        
        text = self.extract_text_from_file(file_path)
        if not text:
            print("Failed to extract text")
            return False
        
        print(f"Extracted {len(text)} characters")
        
        print("Chunking text...")
        self.documents = self.chunk_text(text)
        print(f"Created {len(self.documents)} chunks")
        
        print("Creating embeddings...")
        self.embeddings = self.model.encode(self.documents, convert_to_tensor=True)
        print("Embeddings created")
        
        self.save_embeddings()
        print("Saved")
        
        return True
    
    def save_embeddings(self):
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
            with open(self.documents_file, 'wb') as f:
                pickle.dump(self.documents, f)
        except Exception as e:
            print(f"Could not save embeddings: {e}")
    
    def load_embeddings(self):
        try:
            if os.path.exists(self.embeddings_file) and os.path.exists(self.documents_file):
                with open(self.embeddings_file, 'rb') as f:
                    self.embeddings = pickle.load(f)
                with open(self.documents_file, 'rb') as f:
                    self.documents = pickle.load(f)
                print("Loaded cached embeddings")
                return True
        except Exception as e:
            print(f"Could not load embeddings: {e}")
        return False
    
    def answer_question(self, question: str, top_k: int = 3, short: bool = True) -> Tuple[str, List[str]]:
        if not self.documents or self.embeddings is None:
            return "No book loaded", []
        
        question_embedding = self.model.encode(question, convert_to_tensor=True)
        cos_scores = util.pytorch_cos_sim(question_embedding, self.embeddings)[0]
        top_results = np.argsort(-cos_scores.cpu().numpy())[:top_k]
        relevant_chunks = [self.documents[idx] for idx in top_results]
        
        if short:
            best_chunk = relevant_chunks[0]
            import re
            sentences = re.split(r'[.!?]+', best_chunk)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            short_answer = ""
            word_count = 0
            for sentence in sentences:
                words = sentence.split()
                if word_count + len(words) <= 30:
                    if short_answer:
                        short_answer += " " + sentence
                    else:
                        short_answer = sentence
                    word_count += len(words)
                else:
                    break
            
            if not short_answer:
                words = sentences[0].split()[:15]
                short_answer = " ".join(words) + "..."
            
            answer = short_answer
        else:
            context = "\n\n".join(relevant_chunks)
            answer = f"Based on the book:\n\n{context}"
        
        return answer, relevant_chunks
    
    def get_book_summary(self) -> str:
        if not self.documents:
            return "No book loaded"
        
        return f"Book: {self.book_name}\nChunks: {len(self.documents)}"
