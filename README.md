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