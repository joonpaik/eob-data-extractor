import click
from langchain_google_genai import ChatGoogleGenerativeAI
import pathlib
import os, json, httpx, pathlib, re
from dotenv import load_dotenv
from google.auth import default
import file_processor

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
@click.command()
@click.option('--file','-f', type=click.Path(exists=True), help='File to process')
def main(file):
    print(f"file: {file}")
    
    # Initialize the Google Generative AI model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", 
                                 google_api_key=api_key,
                                 temperature=0.5)
    file_path = pathlib.Path(file)
    name_to_text = file_processor.FileProcessor(str(file_path)).process()

    if not name_to_text:
        print("No valid PDF files found.")
        return json.dump({})

    responses = {}
    prompt = "Extract the Explanation of Benefits (EOB) details from the document below. \
            Collect and categorize all relevant information for the patient, insurance company, \
            and healthcare provider and format it into a JSON object string. IMPORTANT: \
            The response must be in this format: \
            ```json{\"key\": value}```"
    for name in name_to_text:
        response = llm.invoke(prompt + name_to_text[name])
        match = re.search(r'```json\s*\n?(.*?)\n?```', response.content, re.DOTALL)
        formatted_response = match.group(1) if match else "{}"
        json_response = json.loads(str(formatted_response))
        print(json_response)
        responses[name] = json_response
    
    result = json.dumps(responses, indent=4)
    print(result)
    return result
# testing
if __name__ == '__main__':
    main()