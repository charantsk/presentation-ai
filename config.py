import os

class Config:
    # Application settings
    DEBUG = True

    # File upload settings
    UPLOAD_FOLDER = 'generated_files'

    # API keys
    # In production, these should be environment variables
    PEXELS_API_KEY = 'THTqiDKdJPqa0wGgJYQnbSdzcpfIBZnvLuswsf6ho3JbYxnyZQGqcdax'  # Replace with your real Pexels API key

    # Model settings
    MODEL_PATH = 'customweights.gguf'
    IMAGE_MODEL_PATH = 'customweights.gguf'
    MODEL_CONTEXT_LENGTH = 1024

    # ✅ Database settings (add these)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # This creates a file named site.db in your root folder
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    ATOM_AUTHENTICATION = False

    CLAUDE_API_KEY = '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'
