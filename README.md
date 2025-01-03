# GenAIproject
# Azure Function: Search and Summarize with OpenAI and Azure Search

This Azure Function performs a search query on Azure Cognitive Search, retrieves relevant documents based on embedding vectors, and then summarizes the content using OpenAI's language models. It also filters results by department (if provided) and returns both the search results and summaries of the content. 

## Prerequisites

Before deploying the Azure Function, make sure you have the following prerequisites set up:

### 1. Azure Account
- You need an active Azure account to use Azure Cognitive Search and Azure OpenAI Services.
- If you don’t have one, you can sign up for a free account [here](https://azure.com/free).

### 2. Azure Cognitive Search Service
- You must create a **Cognitive Search Service** in Azure. Follow this [guide](https://learn.microsoft.com/en-us/azure/search/search-create-service) to set up your search service.
- You should have an **Index** in your Azure Search Service to store the documents to be searched.

### 3. Azure OpenAI API
- Ensure you have access to **Azure OpenAI**. If you don’t, request access through your Azure portal.
- Follow this [guide](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/tutorials) to set up the Azure OpenAI API.

### 4. Python Environment
- Python 3.x should be installed on your local machine or environment where the function will run.
- Install the necessary Python packages (listed below) to run the function.

### 5. Environment Variables
Set up the following environment variables in your Azure environment or local setup (via `.env` or similar configurations).

#### Required Environment Variables:

- `SEARCH_ENDPOINT`: The endpoint URL for your Azure Cognitive Search service.
- `SEARCH_KEY`: The API key for your Azure Cognitive Search service.
- `AZURE_OPENAI_ENDPOINT`: The endpoint URL for your Azure OpenAI API.
- `AZURE_OPENAI_KEY`: The API key for your Azure OpenAI service.
- `EMBEDDING_MODEL_NAME`: The name of the embedding model to use for generating embeddings (e.g., `"text-embedding-ada-002"`).
- `AZURE_OPENAI_API_VERSION`: The version of the Azure OpenAI API you're using (e.g., `"2023-01-01"`).
- `CHAT_COMPLETION_MODEL_NAME`: The model name for OpenAI's chat completion (e.g., `"gpt-4"`).
- `SYSTEM_MESSAGE`: The system-level message for context, which will be used to guide the AI’s behavior during conversation.

## Steps to Deploy and Use the Function

### Step 1: Clone the Repository
Clone the repository that contains this function or set up a new Azure Function in your development environment.

```bash
git clone <repository-url>
```

### Step 2: Install Dependencies

Create and activate a virtual environment (optional but recommended) to install dependencies.

```bash
python -m venv env
source env/bin/activate  # On Windows use `env\Scripts\activate`
```

Install the required Python libraries.

```bash
pip install azure-functions
pip install openai
pip install azure-core
pip install azure-search-documents
```

### Step 3: Set Up Local Environment

Create a `.env` file or set environment variables manually:

```bash
SEARCH_ENDPOINT=<your_search_endpoint>
SEARCH_KEY=<your_search_key>
AZURE_OPENAI_ENDPOINT=<your_openai_endpoint>
AZURE_OPENAI_KEY=<your_openai_key>
EMBEDDING_MODEL_NAME=<embedding_model_name>
AZURE_OPENAI_API_VERSION=<api_version>
CHAT_COMPLETION_MODEL_NAME=<chat_model_name>
SYSTEM_MESSAGE=<system_message>
```

Make sure to replace `<your_search_endpoint>`, `<your_search_key>`, etc., with the actual values from your Azure resources.

### Step 4: Deploy the Function to Azure

1. **Create an Azure Function App** in your Azure portal if you don’t have one.
2. **Deploy the Function** using the Azure Functions tools in your IDE or through Azure CLI.

```bash
func azure functionapp publish <your-function-app-name>
```

### Step 5: Test the Function

Once the function is deployed, you can test it using a POST request. Here's an example of how to do this using `curl` or Postman.

#### Sample Request Body:

```json
{
  "query": "What is the process of data analysis?",
  "department": "ALL"
}
```

#### Sample Curl Command:

```bash
curl -X POST <your_function_url>/http_trigger -H "Content-Type: application/json" -d '{"query": "What is the process of data analysis?", "department": "ALL"}'
```

The function should return a response with relevant search results from Azure Cognitive Search, along with summaries of the content and a completion response from OpenAI.

#### Sample Response:

```json
{
  "response": "Here is the summary of the data analysis process...",
  "documents": [
    {
      "file_name": "data_analysis_guide.pdf",
      "file_download_url": "https://example.com/data_analysis_guide.pdf",
      "summary": "This document explains the various stages of data analysis...",
      "score": 0.85
    },
    {
      "file_name": "data_analysis_process.docx",
      "file_download_url": "https://example.com/data_analysis_process.docx",
      "summary": "Data analysis involves several key stages such as data collection...",
      "score": 0.80
    }
  ]
}
```

### Step 6: Monitor Logs

You can monitor the function’s logs to debug any issues or review the function's behavior:

1. **View logs in Azure Portal** by navigating to your Function App.
2. **View logs locally** using the Azure Functions Core Tools.

```bash
func start
```

This will start the function locally and show the log output in your terminal.

### Error Handling

The function includes error handling for:

- **Invalid input** (e.g., missing required fields).
- **Invalid or empty search results**.
- **API errors** from either OpenAI or Azure Search.
- **Exceptions during processing** are caught, and a generic error message is returned.

## Summary of the Function’s Workflow

1. **Receive the Request**: The function receives a POST request with a search query and optionally a department filter.
2. **Generate Embedding**: The query is sent to OpenAI's embedding model to generate an embedding.
3. **Search in Azure Cognitive Search**: The generated embedding is used to perform a vector search in Azure Cognitive Search.
4. **Summarize Content**: The relevant search results are summarized using OpenAI's chat model.
5. **Return Results**: The function returns the response, including the AI-generated summary and the relevant documents.

## Troubleshooting

- **Issue: No Search Results Returned**: Ensure your Azure Cognitive Search service is correctly set up and that your documents have been indexed properly with vector fields.
- **Issue: Invalid JSON Request**: Double-check your request payload to ensure it’s valid JSON.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This detailed README should help guide you through setting up, deploying, and using the Azure Function that integrates OpenAI and Azure Search.


# Explanation of the project

Here's an explanation of what each part of the code is doing step by step.

### **Imports and Setup**

```python
import azure.functions as func
import logging
import json
import os
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
```

1. **Import Libraries:**
   - `azure.functions` is used to interact with Azure Functions.
   - `logging` is for logging debug or error messages.
   - `json` helps to work with JSON data (parse and generate JSON).
   - `os` is used to fetch environment variables.
   - `AzureKeyCredential` is used to authenticate the Azure Cognitive Search client.
   - `AzureOpenAI` is the OpenAI API client for Azure.
   - `SearchClient` allows you to query Azure Cognitive Search.
   - `VectorizedQuery` is used for creating a vectorized search query.

### **Fetching Environment Variables**

```python
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
CHAT_COMPLETION_MODEL_NAME = os.getenv("CHAT_COMPLETION_MODEL_NAME")
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE")
```

2. **Fetching Environment Variables:**
   - Using `os.getenv()` to fetch various environment variables that hold sensitive or configurable values:
     - `SEARCH_ENDPOINT` and `SEARCH_KEY` for Azure Cognitive Search credentials.
     - `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY` for the Azure OpenAI API credentials.
     - `EMBEDDING_MODEL_NAME` specifies which embedding model to use (e.g., "text-embedding-ada-002").
     - `AZURE_OPENAI_API_VERSION` is the version of the OpenAI API to use.
     - `CHAT_COMPLETION_MODEL_NAME` specifies the OpenAI chat model (e.g., "gpt-4").
     - `SYSTEM_MESSAGE` is a custom message for system-level instruction in OpenAI models.

### **Setting up the Azure Function App**

```python
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
```

3. **FunctionApp Setup:**
   - This line sets up the Azure Function app and defines the authentication level for the HTTP trigger to be **anonymous** (meaning it doesn’t require authentication to call).

### **HTTP Trigger Function**

```python
@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
```

4. **Route Declaration and Function Definition:**
   - The `@app.route` decorator binds the HTTP endpoint (`http_trigger`) to the function.
   - `http_trigger` is the function that handles incoming HTTP requests.
   - It logs a message every time a request is processed.

### **Parse the Request Body**

```python
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)
```

5. **Parse JSON Request Body:**
   - The function attempts to parse the request body as JSON using `req.get_json()`.
   - If the body is not valid JSON (raises `ValueError`), it returns a `400 Bad Request` with an "Invalid JSON" error message.

### **Extract Query and Department from the Body**

```python
    query = req_body.get('query')
    Department = req_body.get('department')
    index_name = "vaibhav-index"
```

6. **Extract Query Parameters:**
   - Extracts the `query` and `department` fields from the parsed JSON body.
   - Sets the `index_name` to "vaibhav-index", which will be used in the search query.

### **Check for Valid HTTP Method and Required Parameters**

```python
    if req.method != 'POST' or not (query and Department):
        return func.HttpResponse(
            body=json.dumps({"status": "FAILED", "error": "ONLY POST IS ALLOWED "}),
            status_code=200,
            mimetype="application/json"
        )
```

7. **Validate HTTP Method and Parameters:**
   - Checks if the HTTP request method is `POST` and if both `query` and `department` are provided.
   - If not, it returns an error message stating "ONLY POST IS ALLOWED" in JSON format.

### **Search and Embedding with OpenAI**

```python
    openai_client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
```

8. **Create OpenAI Client:**
   - Initializes the OpenAI client using the Azure OpenAI API credentials and version.

```python
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=index_name,
        credential=AzureKeyCredential(SEARCH_KEY)
    )
```

9. **Create Azure Cognitive Search Client:**
   - Initializes the Azure Cognitive Search client using the endpoint, index name, and API key.

```python
    embedding_response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL_NAME,
        input=query
    )
    embedding = embedding_response.data[0].embedding
```

10. **Generate Embedding for Query:**
    - Sends the search query to the OpenAI API for embedding.
    - The model specified in `EMBEDDING_MODEL_NAME` is used to create an embedding.
    - The embedding is stored in `embedding` for use in the vector search.

```python
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=10,
        fields="content_vector"
    )
```

11. **Prepare Vector Search Query:**
    - Creates a vectorized search query with the generated embedding, requesting the top 10 nearest neighbors using the field `content_vector`.

```python
    search_filter = None
    if Department != "ALL":
        search_filter = f"Department eq '{Department}'"
```

12. **Filter Results by Department (if provided):**
    - If a `Department` is provided (and not "ALL"), it constructs a filter string to restrict the search to that department.

```python
    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=["content", "file_download_url", "file_name", "Department"],
        filter=search_filter
    )
```

13. **Perform Search Query:**
    - Executes the search query on Azure Cognitive Search using the vectorized query.
    - The query returns documents with fields `content`, `file_download_url`, `file_name`, and `Department`.
    - The `filter` limits the results based on the department.

### **Process and Format Search Results**

```python
    search_results = [{"content": result["content"],
                       "file_download_url": result["file_download_url"],
                       "file_name": result["file_name"],
                       "@search.score":result["@search.score"]} for result in results]
```

14. **Format Search Results:**
    - Creates a list of dictionaries with key details (content, file URL, file name, score) from the search results.

```python
    if not search_results:
        return func.HttpResponse(
            body=json.dumps({"response": None, "error": None}),
            status_code=200,
            mimetype="application/json"
        )
```

15. **No Results Case:**
    - If no search results are found, it returns a `200 OK` response with `null` values for both `response` and `error`.

### **Generate and Format AI Response**

```python
    answer = "\n".join(result["content"] for result in search_results)
    prompt = SYSTEM_MESSAGE + answer
```

16. **Combine Results for AI Input:**
    - Joins the content of the search results into a single string `answer`.
    - Combines this `answer` with a predefined `SYSTEM_MESSAGE` to create a prompt that will be sent to the OpenAI model.

```python
    response = openai_client.chat.completions.create(
        model=CHAT_COMPLETION_MODEL_NAME,
        temperature=0.7,
        max_tokens=200,
        messages=[{"role": "system", "content": prompt},
                  {"role": "user", "content": query}]
    )
```

17. **Generate Chat Completion:**
    - Sends the `prompt` (including the `SYSTEM_MESSAGE` and the search results) to the OpenAI chat completion API.
    - The user’s original query is included to guide the response.
    - The temperature (creativity) and max tokens (length of response) are controlled.

```python
    response_text = response.choices[0].message.content
```

18. **Extract AI Response:**
    - Extracts the content of the AI's response from the chat completion result.

### **Check for Valid AI Response**

```python
    if not response or "##Not Found##" in response_text:
        return func.HttpResponse(
            body=json.dumps({"response": None, "error": None}),
            status_code=200,
            mimetype="application/json"
        )
```

19. **No AI Response or Invalid Response:**
    - If no response is generated or the AI's response contains "##Not Found##", it returns a `200 OK` response with `null` values for `response` and `error`.

### **Summarize Content and Prepare Final Response**

```python
    files = []
    for result in search_results:
        file_name = result.get("file_name")
        file_download_url = result.get("file_download_url")
        content = result.get("content")
        score=result.get("@search.score")
```

20. **Prepare to Summarize Search Results:**
    - Creates an empty list `files` to store the detailed documents and summaries.
    - Loops over the search results to extract details.

```python
        summary_response = openai_client.chat.completions.create(
            model=CHAT_COMPLETION_MODEL_NAME,
            messages=[{"role": "user", "content": f"Please summarize the following content: {content}"}],
            temperature=0,
            max_tokens=50
        )
        summary = summary_response.choices[0].message.content.strip()
```

21. **Summarize Content for Each Document:**
    - For each document, sends the `content` to the OpenAI API to generate a summary.
    - Limits the summary to 50 tokens and strips any extra whitespace.

```python
        if not any(file['file_name'] == file_name for file in files):
            files.append({
                "file_name": file_name,
                "file_download_url": file_download_url,
                "summary": summary,
                "score": score
            })
```

22. **Store Files with Summaries:**
    - Ensures no duplicate files are added to the `files` list.
    - Appends a dictionary with `file_name`, `file_download_url`, `summary`, and `score`.

### **Return Final Response**

```python
    return func.HttpResponse(
        body=json.dumps({
            "response": response_text,
            "documents": files
        }),
        status_code=200,
        mimetype="application/json"
    )
```

23. **Return Success Response:**
    - Returns a `200 OK` response with:
        - The AI-generated `response_text`.
        - A list of summarized documents.

### **Error Handling**

```python
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"response": None, "error": str(e)}),
            status_code=200,
            mimetype="application/json"
        )
```

24. **General Exception Handling:**
    - If an error occurs anywhere during the process, it catches the exception and returns it as part of the response with the error message.

---

This is a detailed breakdown of the Azure Function code, explaining what each part of the code does. Let me know if you need further clarification!


