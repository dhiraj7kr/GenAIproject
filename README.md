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
