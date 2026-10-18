# NyayaSim (AI Court Sim): Tech Stack Options

A layer-by-layer list of technology choices for NyayaSim, with several strong options for each layer. Option 1 is the suggested default for a student team. Prices, free tiers and limits change often, so check current terms before committing.

## 1. How to use this list

1. Start from one of the suggested combinations in section 3.
2. Swap a layer only when a stated reason applies, such as a language requirement, a privacy need or a cost limit.
3. Test any model or retrieval choice on your own test set before keeping it.
4. Keep agent code independent of the provider, so a model or database can be replaced later.

## 2. Options by layer

| Layer | Option 1 (suggested) | Option 2 | Option 3 | Option 4 | Choose differently when |
| --- | --- | --- | --- | --- | --- |
| Language | Python | TypeScript (Node) |  |  | The team is stronger in JavaScript |
| Language model API | Anthropic Claude | OpenAI GPT models | Google Gemini | Open-weight models (Llama, Qwen, Mistral) via a local or hosted runner | You need low cost or full local control; compare providers on your own test set |
| Local model runner | Ollama | vLLM | llama.cpp | LM Studio | You run open-weight models on your own machine or server |
| Agent orchestration | Plain Python functions and a simple orchestrator | LangGraph | CrewAI | AutoGen or Microsoft Agent Framework | Use a framework only when branching and state become hard to manage by hand |
| Structured output and validation | Pydantic | Instructor | JSON Schema with jsonschema | Provider-native structured output | You want automatic retries on invalid output |
| Backend framework | FastAPI | Flask | Django | Node with Express | You need an admin panel quickly (Django) |
| Relational database | PostgreSQL | SQLite | MySQL or MariaDB |  | SQLite for local prototypes; PostgreSQL for multi-user use and the vector extension |
| Document store (optional) | MongoDB | JSON files on disk |  |  | You prefer flexible logs over relational tables |
| Vector search | pgvector | Chroma | Qdrant | FAISS | Use pgvector to stay in one database |
| Keyword search | PostgreSQL full-text search | BM25 (rank\_bm25) | OpenSearch or Elasticsearch |  | A small corpus needs nothing heavier than BM25 |
| Embeddings | BGE-M3 | multilingual-e5 | OpenAI embedding models | Cohere embeddings | You need Indian-language support (BGE-M3 and e5 are multilingual) |
| PDF text extraction | PyMuPDF | pdfplumber | Docling | Unstructured | Layout and tables matter (Docling, pdfplumber) |
| OCR for scanned files | Tesseract | PaddleOCR | Google Document AI | AWS Textract | Scans are poor quality or handwritten |
| Task queue (optional) | None at first; run in-process | RQ with Redis | Celery with Redis | Arq | Runs are long enough that the interface should not wait |
| Cache | Local file or SQLite cache | Redis |  |  | Multiple users or machines share the cache |
| Frontend (simple) | Streamlit | Gradio | Reflex |  | Fastest route to a working interface |
| Frontend (custom) | Next.js with React | Vue with Nuxt | SvelteKit |  | You want full design control |
| UI components | shadcn/ui with Tailwind | Material UI | Chakra UI |  | Depends on the frontend framework |
| Diagrams and visuals | Mermaid | draw.io | Excalidraw | Figma | Report and architecture diagram |
| Authentication (if needed) | Supabase Auth | Clerk | Auth0 | Simple password with sessions | Skip entirely if the demo has one user |
| Observability and tracing | Langfuse | LangSmith | Arize Phoenix | MLflow or a custom log table | Langfuse and Phoenix can be self-hosted |
| Evaluation | pytest with custom scorers | promptfoo | DeepEval | Ragas | promptfoo is convenient for prompt comparisons |
| Code quality | Ruff and Black | pre-commit hooks | mypy |  | Keeps the team's code consistent |
| Version control and collaboration | GitHub | GitLab | Bitbucket |  | Use whichever your college supports |
| Continuous integration | GitHub Actions | GitLab CI | CircleCI |  | Matches the repository host |
| Containers | Docker with Docker Compose | Podman |  |  | Everyone needs the same environment |
| Hosting for demo | Hugging Face Spaces | Render | Railway | Fly.io | Check free-tier limits; AWS, Azure or GCP if the college provides credits |
| Secrets management | Environment file (ignored by Git) | Doppler | HashiCorp Vault | Cloud secrets manager | Anything shared beyond the team |
| Documentation | Markdown in the repository | MkDocs | Docusaurus | Notion | Where the team already writes |
| Project management | GitHub Projects |  |  | Linear | The tool the team will actually use |

## 

## 3. Decision notes for the key layers

### Language model

- Use a stronger model for the judges, verifier support check and reviewer, where reasoning quality matters most.
- Use a smaller, cheaper model for intake and simple extraction.
- Use different models or prompt framings for the three judges to reduce shared blind spots.
- Whatever the provider, wrap calls in one gateway so settings, cost and caching are handled in one place.

### Orchestration

- Plain Python is easier to debug and to explain, and is enough for a linear pipeline with a few branches.
- A graph framework such as LangGraph helps when you need resumable runs, parallel branches or visual state, but adds a learning curve.
- Multi-agent chat frameworks such as CrewAI or AutoGen speed up demos but give less control over the strict structure this project needs (fixed roles, independent judge opinions, enforced rules).

### Retrieval

- For a small corpus with stable section IDs, exact lookup plus BM25 is often enough and is easy to evaluate.
- Add embeddings when keyword search misses relevant sections or when you add regional language input.
- Whatever you use, the verifier must still check every citation by exact ID lookup.

### Database

- SQLite is the quickest start and works for a single user.
- PostgreSQL is the better long-term choice if you want multiple users, JSON queries and pgvector in one place.

### Interface

- Streamlit or Gradio gets a usable demo with the least code.
- Choose Next.js only if the team wants a custom design and has frontend skills.

### Observability and evaluation

- A custom log table is enough at first, and is already in the database schema.
- Add Langfuse or Phoenix if you want ready-made trace views.
- Keep scoring in plain tests (pytest) so results are reproducible without extra services.

## 5. Selection checklist

- [ ] The language model choice is tested on the team's own test cases
- [ ] A spending limit is set on every paid API
- [ ] Free-tier limits and terms have been checked for every hosted service
- [ ] Secrets are kept out of the repository
- [ ] Every team member can run the project locally
- [ ] The provider can be swapped without changing agent code
- [ ] Data stays fictional, so hosted services are acceptable
