# Data Directory

This directory is used for storing uploaded car manuals and processed documents.

## Usage

When you deploy ManualAi, users can upload their car manuals through the web interface. The uploaded files will be processed by the backend and stored in this directory structure:

- `uploads/` - Original uploaded files
- `manual_store/` - Processed vector store data

## Note

Sample PDF files are not included in the repository to keep it lightweight. Users should upload their own car manuals through the application interface.
