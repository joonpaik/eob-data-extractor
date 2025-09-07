import click
from langchain_google_genai import ChatGoogleGenerativeAI
import pathlib
import os, json, httpx, pathlib, re, sys
from dotenv import load_dotenv
from google.auth import default
import file_processor

"""
    Python CLI tool to extract Explanantion of Benefits (EOB) details from PDF files.
    Supports single PDF files or ZIP files containing multiple PDFs.
    Utilizes Google Generative AI to process and extract relevant information.

    Handle all edge cases 
"""

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
@click.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='File to process')
@click.argument('files', nargs=-1, type=click.Path(exists=True))
def main(file, files):
    # Handle Number of inputs
    if not file:
        click.secho("Error: please provide a file path using the --file option.", fg="red", err=True)
        raise click.Abort()
    file_number = len(files) + 1 if file else len(files)
    if file_number > 1:
        click.secho("Error: please provide only one file path.", fg="red", err=True)
        raise click.Abort()
    
    # Handle Corrupted/Encrpyted files
    try:
        with open(file, 'rb') as f:
            f.read()
    except Exception as e:
        f.close()
        click.secho(f"Error: The file {file} is corrupted or unreadable.", fg="red", err=True)
        raise click.Abort()
    
    file_path = pathlib.Path(file)
    file_name = file_path.name
    fp = file_processor.FileProcessor(str(file_path))
    name_to_text = {}
    try:
        name_to_text = fp.process()
    except Exception as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        raise click.Abort()

    if not name_to_text:
        click.echo("{}")
        sys.exit(0)
    
    # Initialize the Google Generative AI model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", 
                                 google_api_key=api_key,
                                 temperature=0.5)

    content_cleaning_prompt = "Check the text to verify that the content is \
            relevant to health insurance Explanation of Benefits (EOB) documents. \
            If the content is not relevant, return NOT RELEVANT \
            if it is relevant, return the text as is. Here is the content: \n\n"
    cleaned_name_to_text = {}
    for name in name_to_text:
        response = llm.invoke(content_cleaning_prompt + name_to_text[name])
        cleaned_text = response.content.strip()
        # print(cleaned_text)
        if cleaned_text != "NOT RELEVANT":
            cleaned_name_to_text[name] = cleaned_text
        
    if not cleaned_name_to_text:
        click.echo("{}")
        sys.exit(0)

    prompt = "Extract the Explanation of Benefits (EOB) details from the document below. \
            Collect and categorize all relevant information for the patient, insurance company, \
            and healthcare provider and format it into a JSON object string. \
            The JSON object must contain the following keys with the following fields: \
            { \
                \"{file_name}\": \
                { \
                    \"patient_info\": \
                    { \
                        \"name\": \"\", \
                        \"address\": \"\", \
                        \"phone\": \"\", \
                        \"email\": \"\", \
                        \"member_id\": \"\", \
                        \"group_number\": \"\" \
                }, \
                \"insurance_info\": \
                { \
                    \"company_name\": \"\", \
                    \"company_address\": \"\", \
                    \"company_phone\": \"\", \
                    \"policy_number\": \"\", \
                }, \
                \"provider_info\": \
                { \
                    \"name\": \"\", \
                    \"address\": \"\", \
                    \"billing_provider\": \"\", \
                    \"performing_provider\": \"\" \
                }, \
                \"claim_info\": \
                { \
                    \"{claim_number}\": \
                    [ \
                        { \
                            \"date_of_service\": \"\", \
                            \"service_code\": \"\", \
                            \"claim_number\": \"\", \
                            \"total_charge\": \"\", \
                            \"amount_paid_by_insurance\": \"\", \
                            \"amount_paid_by_patient\": \"\", \
                            \"deductible\": \"\", \
                            \"co_pay\": \"\", \
                            \"co_insurance\": \"\", \
                            \"diagnosis_codes\": [\"\"], \
                            \"status\": \"\", \
                            \"notes\": \"\" \
                        } \
                    ] \
                }, \
                \"cost_info\": \
                { \
                    \"total_billed_amount\": \"\", \
                    \"total_amount_paid_by_insurance\": \"\", \
                    \"total_amount_paid_by_patient\": \"\", \
                    \"remaining_balance\": \"\" \
                }, \
                \"denied_info\": \
                [ \
                    { \
                        \"service\":  \"\", \
                        \"date\":  \"\", \
                        \"remark_code\":  \"\", \
                        \"reason\":  \"\", \
                    } \
                ]\
              } \
            }\
            Please remove any stray newlines or excess whitespace. The resulting json must be in this format: \
            ```json{\"key\": value}```"
    
    responses = {}
    for name in cleaned_name_to_text:
        response = llm.invoke(prompt + cleaned_name_to_text[name])
        match = re.search(r'```json\s*\n?(.*?)\n?```', response.content, re.DOTALL)
        formatted_response = match.group(1) if match else "{}"
        json_response = json.loads(str(formatted_response))
        responses[name] = json_response
    
    result = json.dumps(responses, indent=4)
    click.echo(result)
    sys.exit(0)

# testing
if __name__ == '__main__':
    main()