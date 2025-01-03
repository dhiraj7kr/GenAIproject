import azure.functions as func
import logging
import json
import os
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
 
# Fetch environment variables
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
CHAT_COMPLETION_MODEL_NAME = os.getenv("CHAT_COMPLETION_MODEL_NAME")
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE")
 
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)
 
@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
 
    openai_client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
 
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)
 
    query = req_body.get('query')
    Department = req_body.get('department')
    index_name = "vaibhav-index"
 
    if req.method != 'POST' or not (query and Department):
        return func.HttpResponse(
            body=json.dumps({"status": "FAILED", "error": "ONLY POST IS ALLOWED "}),
            status_code=200,
            mimetype="application/json"
        )
 
    try:
        search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=index_name,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
 
        embedding_response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL_NAME,
            input=query
        )
        embedding = embedding_response.data[0].embedding
 
        vector_query = VectorizedQuery(
            vector=embedding,
            k_nearest_neighbors=10,
            fields="content_vector"
        )
 
        search_filter = None
        if Department != "ALL":
            search_filter = f"Department eq '{Department}'"
 
        results = search_client.search(
            search_text=None,
            vector_queries=[vector_query],
            select=["content", "file_download_url", "file_name", "Department"],
            filter=search_filter
        )
 
        search_results = [{"content": result["content"],
                           "file_download_url": result["file_download_url"],
                           "file_name": result["file_name"],
                           "@search.score":result["@search.score"]} for result in results]
 
        if not search_results:
            return func.HttpResponse(
                body=json.dumps({"response": None, "error": None}),
                status_code=200,
                mimetype="application/json"
            )
 
        answer = "\n".join(result["content"] for result in search_results)
        prompt = SYSTEM_MESSAGE + answer
 
        response = openai_client.chat.completions.create(
            model=CHAT_COMPLETION_MODEL_NAME,
            temperature=0.7,
            max_tokens=200,
            messages=[{"role": "system", "content": prompt},
                      {"role": "user", "content": query}]
        )
 
        response_text = response.choices[0].message.content
 
        if not response or "##Not Found##" in response_text:
            return func.HttpResponse(
                body=json.dumps({"response": None, "error": None}),
                status_code=200,
                mimetype="application/json"
            )
 
        files = []
 
        for result in search_results:
            file_name = result.get("file_name")
            file_download_url = result.get("file_download_url")
            content = result.get("content")
            score=result.get("@search.score")
 
            # Summarizing the content
            summary_response = openai_client.chat.completions.create(
                model=CHAT_COMPLETION_MODEL_NAME,
                messages=[{"role": "user", "content": f"Please summarize the following content: {content}"}],
                temperature=0,
                max_tokens=50
            )
            summary = summary_response.choices[0].message.content.strip()
 
            if not any(file['file_name'] == file_name for file in files):
                files.append({
                    "file_name": file_name,
                    "file_download_url": file_download_url,
                    "summary": summary,
                    "score":score
                })
 
        logging.info("Response content: %s", response_text)
 
        return func.HttpResponse(
            body=json.dumps({
                "response": response_text,
                "documents": files
            }),
            status_code=200,
            mimetype="application/json"
        )
 
    except Exception as e:
        return func.HttpResponse(
            body=json.dumps({"response": None, "error": str(e)}),
            status_code=200,
            mimetype="application/json"
        )
 
 