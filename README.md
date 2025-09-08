# eob-data-extractor
A Python CLI tool for extracting and processing data from ZIP files and PDFs using Large Language Models. 

Prerequisites
- Python 3.8 or higher
- Google API key for Gemini Flash API usage
- System dependencies for PDF processing


# System Dependencies
macOS: 

```bash
# Install libmagic for file type detection
brew install libmagic

# For PDF processing (if needed)
brew install poppler
```
Ubuntu/Debian:

```bash
bashsudo apt-get update
sudo apt-get install libmagic1 libmagic-dev
sudo apt-get install poppler-utils 
```
Windows: Install using conda (recommended for Windows)
```bash
conda install -c conda-forge libmagic
```
Or download libmagic binaries and add to PATH

## Installation
### Quick Start
```bash
git clone <repository-url>
cd eob-data-extractor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### Configure Environment
```bash
# Create .env file with your Google API key
echo "GOOGLE_API_KEY=your_actual_api_key_here" > .env
```

### Run The Extractor
```bash
python extract_eob.py --file <path/to/file>
```

### Test the setup
```bash
python test_extract_eob.py
```

## Getting Google API Key
- Go to Google AI Studio
- Sign in with your Google account
- Click "Create API Key"
- Copy the generated key to your .env file

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)

# Process
The objective of the assignment is to output a structured JSON for downstream automation.

## Project Structure
I decided to split the project into three major parts: 
- extract_eob.py (what is actually called)
- agent.py (for the agent)
- file_processor.py (internal file handling)


By organizing the project in this style, I felt I had a better grasp of how the end product was going to turn out.

## Edge Cases Handled
- Invalid file types (.txt, .docx, .jpg, etc.)
- Both PDFs and ZIP file of PDFs
- Files pretending to be PDFs
- Password Protected Files
- Empty ZIP files
- Corrupted files
- PDFs that are unrelated to EOBs
- ZIP files with both valid and invalid file types

My test coverage covers more than that 2-3 sample EOB PDFs you have requested, but I have kept them there for your review. This is called by using the command:
```bash
python test_extract_eob.py
```

The three main sample EOBs I have used is in the root directory alongside the rest of my main .py files

## Ways to Improve
While this was a fun assignment, there are a few ways I would try to improve this implementation given more time. 

First, I would like to implement a retry mechanism. It is not guarenteed that the agent will output all the information correctly the first time, but if I could implement a dynamic prompt specification function, this tool would be greatly improved

Second, I would like to have handled nested directories and nested ZIP files. I made the assumption that the input would not be this scenario, but it is an important edge case to consider.

Third, I would like to implement better handling on the API calls to Gemini Flash. While this implementation is sufficiently for low-scale processing, scalability is an important aspect to consider in a growing company like Onehots Labs.


# Output Format

## Relevant Parties
 I tried to approach this task in terms of who are affected by the data from a Explanation of Benefits:
- Patients
- Healthcare Providers
- Insurance Companies
By prioritizing information pertaining to these three, Onehot Labs will be able to pinpoint a particular EOB quickly if properly indexed.

## Claims
The purpose of an EOB is to give a summary of covered services and to estimate the amount the patient, healthcare providers, and insurance companies all need to pay, which is why claims must have its own category as well.

Usually an EOB will send one claim id, but it is possible to have several, which is why I decided to make the value of the "claim_info" section as dictionary. Furthermore, a claim can have multiple services under it, and since services are usually displayed in rows, it seem appropriate to represent the data as a list of dictionaries, portraying each service object. This will have a breakdown of cost per service and how much coverage each service received

## Cost
Each service's cost is represented already, but since the total cost is also listed in the EOB, it seemed appropriate and efficient to just record the total amount paid by the patient and insurance company.

## Denied Services
EOBs are also the place where an insurance company can deny converage for a particular service. Typically, the insurance companies will have to explain why they denied a certain service, usually accompanied by a code. It seemed necesscary, then to have the "denied_info" category so that Onehot Labs would have that information on hand in preparation for potential appeals. 


