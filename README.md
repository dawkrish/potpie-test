# Potpie Assignment

## Table Of Contents
* [Setup Instructions](#setup-instructions)
* [Technologies Used](#technologies-used)
* [Workflow](#workflow)
* [API Documentation](#api-documentation)
    - [Process Document](#1-process-document)
    - [Start Chat](#2-start-chat)
    - [Send Message](#3-send-message)
    - [Chat History](#4-get-chat-history)
* [Possible Improvements](#possible-improvements)

## Setup Instructions

```
git clone git@github.com:dawkrish/potpie-test.git
```

```
cd potpie-test
```

```
python3 -m venv venv
```

```
pip install -r requirements.txt
```


## Technologies used

* Python (>=3.10) because we use pattern-matching
* Flask for REST API
* ChromaDB as vector DB to store the embeddings (we have done persistently)
* PyPDF2 to get text from pdf files
* python-docx to get text from docx files
* dotenv to load environment variables 
* HuggingFace Embeddings (to embed text and later used to make vectorstore)
* Langchain ties up everything
* llm used is ChatMistralAI, currently I have used all the tokens :"


## Workflow
* User uploads the file.

* User creats an **asset_id** with the end point `POST /api/document/process`
    * text is extracted out for different extension types using `get_file_text` (embeddings.py)
    * `save_embeddings` (embeddings.py) is called to save the embedding.
        * creates a **uuid** and assigns to `asset_id`
        * `get_huggingface_embeddings` (embeddings.py) is used for embeddings (we have a default-embedder too `get_default_embeddings`)
        * `chroma_collection.add` to **save** the embedding
        * returns `asset_id`
    * the end point returns `asset_id`

* User creates a "thread_id" with the end point `POST /api/chat/start`
    * This end point takes the `asset_id` from the previous end point
    * It returns a `thread_id` .
    * The thread `thread_to_asset_map` exists to keep mappings, its a in-memory global variable
    * Now after getting the *thread_id* user can start chatting.

* End point `POST /api/chat/message` is used for to chat.
    * `user_message` the user prompt/query and `thread_id` which we got from last end point is needed
    * we get response from `response_to_message` (rag.py)
    * we use mistral-ai for now, it can be changed
    * The response will be in stream;  Streaming can be turned off.
    * at this end point, the "chat-message" gets stored in the variable `chat_history`, another in-memory global variable
    * The chats are non-persistent. We can integrate sqlite3 to save the chats.

* End point `GET /api/chat/history/<thread_id>` returns the specific chat.



## API Documentation
**Generate from Mistral-AI** 

This API provides endpoints for processing documents and managing chat sessions. Below are the available endpoints and their usage.

### Endpoints

### 1. Process Document

**Endpoint:** `/api/document/process`

**Method:** `POST`

**Description:** Processes a document and saves its embeddings.

**Request Body:**
```json
{
    "file_path": "path/to/your/file"
}
```

**Response:**
- **Success (200):**
  ```json
  {
      "asset_id": "generated_asset_id"
  }
  ```
- **Error (400):**
  ```json
  {
      "error": "file_path is required"
  }
  ```

### 2. Start Chat

**Endpoint:** `/api/chat/start`

**Method:** `POST`

**Description:** Starts a new chat session based on a given asset ID.

**Request Body:**
```json
{
    "asset_id": "your_asset_id"
}
```

**Response:**
- **Success (200):**
  ```json
  {
      "thread_id": "generated_thread_id"
  }
  ```
- **Error (400):**
  ```json
  {
      "error": "asset_id is required"
  }
  ```
- **Error (404):**
  ```json
  {
      "error": "Invalid asset_id, no embeddings exist for it"
  }
  ```

### 3. Send Message

**Endpoint:** `/api/chat/message`

**Method:** `POST`

**Description:** Sends a user message and receives an AI response.

**Request Body:**
```json
{
    "thread_id": "your_thread_id",
    "user_message": "your_message"
}
```

**Response:**
- **Success (200):**
  ```json
  {
      "ai_response": "generated_ai_response"
  }
  ```
- **Error (400):**
  ```json
  {
      "error": "thread_id is required"
  }
  ```
- **Error (400):**
  ```json
  {
      "error": "user_message is required"
  }
  ```
- **Error (404):**
  ```json
  {
      "error": "Invalid chat-thread id, create a new one"
  }
  ```

### 4. Get Chat History

**Endpoint:** `/api/chat/history/<thread_id>`

**Method:** `GET`

**Description:** Retrieves the chat history for a given thread ID.

**Response:**
- **Success (200):**
  ```json
  {
      "chat_history": [
          {
              "timestamp": "2023-10-01T12:00:00Z",
              "user_message": "your_message",
              "ai_response": "generated_ai_response"
          }
      ]
  }
  ```
- **Error (400):**
  ```json
  {
      "error": "thread_id does not exist in memory"
  }
  ```

### Possible Improvements
* Better handling of chat-history, possibly using `lang-graph`
* Options to chose LLM
* Options for streaming
* Making code more flexible
* Python files documentation using Mistral-AI model Codestral (it is awesome.)
