# Using AS1-mini with Neo4j GraphRAG

This guide explains how to use AS1-mini as a custom LLM implementation with Neo4j GraphRAG, replacing the default OpenAI LLM.

## Components

1. **AS1 LLM Adapter** (`as1_llm.py`): Custom implementation of the GraphRAG LLMInterface that connects to the AS1-mini API
2. **Sentence Transformer Embedder** (`custom_rag.py`): Adapter that wraps our existing EmbeddingService to implement GraphRAG's Embedder interface
3. **Custom GraphRAG Implementation** (`custom_rag.py`): Puts everything together in a user-friendly class
4. **Simple RAG Example** (`rag_as1.py`): Direct replacement for the original `rag.py` script

## Setup

### Prerequisites

1. Neo4j database with vector indexing capability
2. AS1-mini API key
3. Python packages: neo4j, neo4j-graphrag, sentence-transformers

### Installation

1. Install required packages:
   ```bash
   pip install neo4j neo4j-graphrag sentence-transformers requests
   ```

2. Set environment variables:
   ```bash
   # Neo4j connection
   export NEO4J_URI="neo4j://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="password"
   
   # Vector index name
   export NEO4J_INDEX_NAME="vector-index"
   
   # AS1 API key
   export AS1_API_KEY="your_as1_api_key_here"
   ```

## Usage

### Option 1: Simple Replacement for OpenAI

Use `rag_as1.py` as a drop-in replacement for your existing `rag.py` script:

```bash
python rag_as1.py
```

### Option 2: Using the CustomGraphRAG Class

```python
from custom_rag import CustomGraphRAG

# Initialize custom GraphRAG
rag = CustomGraphRAG(
    neo4j_uri="neo4j://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    as1_api_key="your_as1_api_key_here"
)

try:
    # Run a query
    query = "How do I do similarity search in Neo4j?"
    response = rag.search(query)
    print(f"Response: {response}")
finally:
    # Close the Neo4j connection
    rag.close()
```

### Option 3: Using Components Directly

If you need more control, you can use the components directly:

```python
from neo4j import GraphDatabase
from as1_llm import AS1LLM
from embedding_service import EmbeddingService
from custom_rag import SentenceTransformerEmbedder
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.generation import GraphRAG

# Initialize Neo4j driver
driver = GraphDatabase.driver("neo4j://localhost:7687", auth=("neo4j", "password"))

# Initialize embedding service and adapter
embedding_service = EmbeddingService()
embedder = SentenceTransformerEmbedder(embedding_service)

# Initialize retriever
retriever = VectorRetriever(driver, "vector-index", embedder)

# Initialize LLM
llm = AS1LLM(api_key="your_as1_api_key_here")

# Initialize GraphRAG
rag = GraphRAG(retriever=retriever, llm=llm)

# Run query
response = rag.search(query_text="Your query here", retriever_config={"top_k": 5})
print(response.answer)
```

## Customizing AS1 Parameters

You can customize the AS1LLM behavior by adjusting parameters in the constructor:

```python
llm = AS1LLM(
    api_key="your_as1_api_key_here",
    model_name="asi1-mini",  # Model name
    temperature=0.0,         # Temperature (0.0 = deterministic)
    max_tokens=1024,         # Maximum tokens to generate
    stream=False             # Whether to stream the response
)
```

## Troubleshooting

### LLM Not Working

If you encounter issues with AS1-mini:

1. Verify your API key is correct and properly set
2. Check the response from the API for error messages
3. Ensure you have internet connectivity
4. Check the API documentation for rate limits or other constraints

### Embedding Issues

If you encounter issues with embeddings:

1. Verify that the sentence-transformers package is installed
2. Check that the model specified in EmbeddingService is available
3. For large texts, consider chunking before embedding 