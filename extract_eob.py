import click
from langchain_google_genai import ChatGoogleGenerativeAI
import pathlib
import os, json, httpx, pathlib, re, sys
from dotenv import load_dotenv
from google.auth import default
import file_processor, agent

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

    ag = agent.Agent(api_key)
    extracted_details = ag.extract_eob_details(name_to_text)
    if not extracted_details:
        click.echo("{}")
        sys.exit(0)
    click.echo(json.dumps(extracted_details, indent=4))
    sys.exit(0)
    

# testing
if __name__ == '__main__':
    main()