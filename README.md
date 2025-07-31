

# Structured Knowledge Extraction with Gemini + Graphiti

This project extracts structured entities and relationships from natural language text using **Google Gemini**, and stores them as a knowledge graph in a **Neo4j** database via **Graphiti**.

##  What It Does

1. **Takes in raw text**
2. **Uses Gemini (Generative AI) to extract structured data**:

   * Entities (e.g., people, places, things)
   * Relationships between entities
3. **Stores the extracted knowledge** as a graph in Neo4j via Graphiti.
4. Optionally, you can search the graph for knowledge.

---

##  Example

For this input:

> *"Marie Curie discovered radium and worked at Sorbonne University in Paris."*

It extracts:

### Entities:

* `marie curie` (scientist)
* `radium` (element)
* `sorbonne university` (institution)
* `paris` (city)

### Relationships:

* `marie curie → discovered → radium`
* `marie curie → worked_at → sorbonne university`
* `sorbonne university → located_in → paris`

---

##  Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/gemini-graphiti-kg.git
cd gemini-graphiti-kg
```

### 2. Install Dependencies

This project uses Python 3.9+.

```bash
pip install -r requirements.txt
```

Add these dependencies in your `requirements.txt` if not already:

```txt
pydantic
google-generativeai
graphiti-core
```

### 3. Environment Variables

Set your **Google Gemini API key**:

```bash
export GOOGLE_API_KEY="your_google_api_key"
```

Or create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key
```

### 4. Set Up Neo4j

Make sure a Neo4j instance is running locally with the following credentials:

* Bolt URL: `bolt://localhost:7687`
* Username: `neo4j`
* Password: `ok@test123`

Update these in `get_graphiti_obj()` if different.

---

##  How It Works

### Key Components

* **`ExtractableEntity` / `ExtractableRelationship`**: Pydantic models that describe the structured output.
* **`get_prompt(chunk)`**: Generates a prompt for Gemini to extract entities/relationships from text.
* **`get_structured_data(chunk)`**: Sends the prompt to Gemini and parses the JSON output.
* **`add_episode(graphiti, episode)`**: Adds the structured result to Neo4j via Graphiti.
* **`find_episode(graphiti, query)`**: Optional function to search the graph with a keyword.

---

## ▶️ Run the Script

The main script does the following:

1. Connects to Gemini
2. Sends a test sentence
3. Parses the Gemini response
4. Uploads it to Graphiti (Neo4j)

```bash
python your_script_name.py
```

Expected output:

```txt
Connection closed
```

---

## 🔍 Example Graphiti Query

```python
await find_episode(graphiti, "marie curie")
```

---

##  File Structure

```
.
├── main.py              # Core script for extraction and upload
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies
```

---

##  Dependencies

* [`graphiti-core`](https://pypi.org/project/graphiti-core/)
* [`google-generativeai`](https://pypi.org/project/google-generativeai/)
* `pydantic`

