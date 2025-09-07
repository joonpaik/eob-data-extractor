import fitz  # PyMuPDF
from typing import List
import magic
import zipfile, os, click

"""
    Goal: structure PDF to be in human-readable content
    The input will be a local PDF or a zip file containing PDFs.
    The output will be:
        -- a list of text contents extracted from the PDFs
        -- initial numbers of files inputted
        -- verified number of files that are valid PDFs
"""


class FileProcessor:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.files = []
        self.initial_files_number = 0
        self.verified_files_number = 0
        self.max_recursion_depth = 3 
        self.result = {}

    def process(self):
        try:
            # Check for encryption
            if fitz.open(self.file_path).needs_pass:
                raise ValueError("The provided file is encrypted and cannot be processed.")
            
            # check if file is zip
            if magic.from_file(self.file_path, mime=True) == 'application/zip':
                return self.process_zip()
            
            # check if it a single pdf
            elif self.validate_pdf(self.file_path):
                return self.process_single_pdf(self.file_path)
    
            else:
                raise ValueError("Unsupported file type. Please provide a PDF or a ZIP file containing PDFs.")
        except Exception as e:
            raise e
    
    def process_single_pdf(self, file_path: str):
        self.files.append(file_path)
        self.initial_files_number = 1
        reader = fitz.open(file_path)
        text = ""
        for p in reader:
            text += p.get_text()
        self.result[os.path.basename(file_path)] = text
        reader.close()
        self.verified_files_number = 1
        return self.result

    def process_zip(self):
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                if len(zip_ref.namelist()) == 0:
                    return self.result  # Empty zip file
                for file_name in zip_ref.namelist():
                    if file_name.endswith(".pdf"):
                        with zip_ref.open(file_name) as file:
                            content = file.read()

                            is_pdf = magic.from_buffer(content, mime=True) == 'application/pdf'
                            if is_pdf:
                                self.initial_files_number += 1
                                reader = fitz.open(stream=content, filetype="pdf")
                                text = ""
                                for p in reader:
                                    text += p.get_text()
                                self.result[os.path.basename(file_name)] = text
                                reader.close()
                                self.result[file_name] = text
                                self.verified_files_number += 1
        except zipfile.BadZipFile:
            click.secho(f"Error: The file {self.file_path} is not a valid zip file or is corrupted.", fg="red", err=True)
            raise ValueError("The provided zip file is corrupted or invalid.")     
        except Exception as e:
            click.secho(f"Error processing zip file {self.file_path}: {e}", fg="red", err=True)
            raise e
        return self.result

    def validate_pdf(self, file_path: str) -> bool:
        return magic.from_file(file_path, mime=True) == 'application/pdf'
    