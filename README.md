# AI-Based RAG Project  

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline for analyzing SEC 10-K filings (or other unstructured documents). It combines **document parsing, vector database storage, and a large language model (LLM)** to provide accurate, context-aware answers.  

---

## 🚀 Features  
- **Document Downloader**: Fetch SEC 10-K filings (Microsoft, Nvidia, Google, etc.) for multiple years.  
- **HTML Parser**: Extracts structured sections (Item 1, Item 1A, Item 7, Item 8, etc.) from filings.  
- **Chunking & Embedding**: Splits documents into semantic chunks and creates embeddings using OpenAI/HuggingFace models.  
- **Vector Database**: Stores embeddings in a vector DB (FAISS, Pinecone, or Chroma).  
- **RAG Query Engine**: Uses embeddings to retrieve relevant context and generate LLM-based answers.  
- **Scalable Design**: Easily extendable to handle multiple companies, years, and document types.  

---

## 🛠️ Project Structure  
```
├── src/
│   ├── downloader.py        # Downloads 10-K filings
│   ├── parser_html.py       # Parses HTML into structured JSON
│   ├── chunker.py           # Splits text into chunks for embeddings
│   ├── embedder.py          # Generates embeddings and stores in DB
│   ├── rag_pipeline.py      # Core RAG query pipeline
│   └── utils.py             # Helper functions
│
├── data/                    # Raw & parsed documents
│   ├── raw/                 # Downloaded HTML filings
│   └── parsed/              # JSON structured outputs
│
├── notebooks/               # Jupyter notebooks for testing
├── requirements.txt         # Python dependencies
├── README.md                # Project documentation
└── config.yaml              # Config file (API keys, DB paths, etc.)
```

---

## ⚙️ Installation  

1. **Clone the repository**  
```bash
git clone https://github.com/your-username/rag-project.git
cd rag-project
```

2. **Create virtual environment**  
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. **Install dependencies**  
```bash
pip install -r requirements.txt
```

4. **Set environment variables**  
Create a `.env` file:  
```ini
OPENAI_API_KEY=your_api_key_here
VECTOR_DB_PATH=./data/vector_store
```

---

## ▶️ Usage  

### 1. Download filings  
```bash
python src/downloader.py --company MSFT --years 2022 2023 2024
```

### 2. Parse filings into structured JSON  
```bash
python src/parser_html.py --input ./data/raw/MSFT_2022.html --output ./data/parsed/MSFT_2022.json
```

### 3. Generate embeddings & store in DB  
```bash
python src/embedder.py --input ./data/parsed/MSFT_2022.json
```

### 4. Run RAG pipeline for Q&A  
```bash
python src/rag_pipeline.py --query "What are the major risks faced by Microsoft in 2023?"
```

---

## 📊 Workflow  

1. **Download** → SEC 10-K filings  
2. **Parse** → Extract sections like *Item 1A: Risk Factors*  
3. **Chunk & Embed** → Break into chunks and store embeddings  
4. **Retrieve & Generate** → Answer queries with retrieved context + LLM  

---

## ✅ Example Query  
```bash
> python src/rag_pipeline.py --query "Summarize Nvidia's R&D spending trends in 2023."
```
**Output:**  
```
Nvidia reported an increase in R&D spending in 2023, primarily driven by AI and GPU advancements. Compared to 2022, expenses rose by ~30%, reflecting investments in data center and generative AI workloads.
```

---

## 📦 Dependencies  
- Python 3.9+  
- `openai` or `transformers` for embeddings  
- `faiss` / `chromadb` for vector search  
- `beautifulsoup4` for parsing HTML  
- `pandas`, `numpy`, `tqdm`  

---

## 🔮 Future Improvements  
- Add support for **multi-document comparisons** (cross-company/year).  
- Integrate **streamlit UI** for interactive querying.  
- Implement **fine-tuned summarization models**.  
- Add **Docker support** for deployment.  

---

## 📝 License  
This project is licensed under the MIT License.  
