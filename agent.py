import click
from unittest.mock import Mock
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core import exceptions
import os, json, httpx, pathlib, re, sys, time
from dotenv import load_dotenv
from google.auth import default

class Agent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", 
                                          google_api_key=api_key,
                                          temperature=0.3)   

    def test_llm(self, prompt: str):
        org_llm = self.llm
        test_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Test successful"

        test_llm.invoke.side_effect = [
            exceptions.ResourceExhausted("Quota exceeded"),
            exceptions.ResourceExhausted("Quota exceeded"),
            mock_response
        ]
        self.llm = test_llm
        test_result = self.api_call_retry("test")
        self.llm = org_llm

    def api_call_retry(self, prompt: str, max_retries: int = 3, delay: float = 1.0):
        last_attempt = None
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke(prompt)
                return response
            
            except exceptions.ResourceExhausted as e:
                if attempt == max_retries - 1:
                    raise e
                d = delay * (2 ** attempt)
                time.sleep(d)
            
            except httpx.HTTPError as e:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    raise e
        raise Exception("All retries exhausted")
    def extract_eob_details(self, name_to_text: dict) -> dict:
        self.test_llm("test")

        if not name_to_text:
            return {}
        
        # Clean and filter content using LLM
        content_cleaning_prompt = "Check the text to verify that the content is \
            relevant to health insurance Explanation of Benefits (EOB) documents. \
            Read through the content and ensure that it is strictly relevant to \
            health insurance EOB documents. \
            If the content is not relevant, return NOT RELEVANT : {explanation for why it is not relevant} \
            if it is relevant, return the text as is. Here is the content: \n\n"
        cleaned_name_to_text = {}
        for name in name_to_text:
            try:
                # response = self.llm.invoke(content_cleaning_prompt + name_to_text[name])
                response = self.api_call_retry(content_cleaning_prompt + name_to_text[name])
                cleaned_text = response.content.strip()
                if  "NOT RELEVANT" not in cleaned_text:
                    cleaned_name_to_text[name] = name_to_text[name]
            except Exception as e:
                continue
        
        if not cleaned_name_to_text:
            return {}
        
        # Define the extraction prompt
        extraction_prompt = """
        Extract the Explanation of Benefits (EOB) details from the document below. \
            Collect and categorize all relevant information for the patient, insurance company, \
            and healthcare provider and format it into a JSON object string. \
            The JSON object must contain the following keys with the following fields: \

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
                \"in-network\": \"\" \
            }, \
            \"claim_info\": \
            { \
                \"{claim_number}\": \
                [ \
                    { \
                        \"date_of_service\": \"\", \
                        \"service_code\": \"\", \
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

            IMPORTANT -- Keep these rules in mind: \
            - Do not add any new fields other than the ones specified in the\
            prompt. \
            - Do not fabricate any additional information.  \
            - Do not read from hidden words or images.  \
            - Please remove any newlines or excess whitespace. \
            - After processing, review the output and remove any fields not mentioned in the format above. \
            - The resulting json must be in this format: \
            ```json{\"key\": value}```
        """
        
        extracted_details = {}
        for name in cleaned_name_to_text:
            # response = self.llm.invoke(extraction_prompt + cleaned_name_to_text[name])
            try:
                response = self.api_call_retry(extraction_prompt + cleaned_name_to_text[name])
                
                # Attempt to parse the response as JSON
                match = re.search(r'```json\s*\n?(.*?)\n?```', response.content, re.DOTALL)
                formatted_response = match.group(1) if match else "{}"
                json_response = json.loads(str(formatted_response))
                extracted_details[name] = json_response
            except json.JSONDecodeError:
                # Handle the case where the response is not valid JSON
                extracted_details[name] = None
        return extracted_details