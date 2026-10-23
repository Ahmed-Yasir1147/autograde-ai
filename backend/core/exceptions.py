"""Defines custom exceptions for the application."""

from typing import List, Dict
from enum import Enum

class FileValidationErrors(Enum):
    """Enumeration of file validation errors."""
    ILLEGAL_FILE_SIZE = "IllegalFileSizeError"
    UNSUPPORTED_FILE_TYPE = "UnsupportedFileTypeError"

class FileBaseError(Exception):
    """Base class for file-related exceptions."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class IllegalFileSizeError(FileBaseError):
    """Exception raised when the uploaded file size exceeds the allowed limit."""
    def __init__(self, message: str = "Uploaded file size exceeds the allowed limit.", file_name: str = ""):
        super().__init__(message)
        self.file_name = file_name

class UnsupportedFileTypeError(FileBaseError):
    """Exception raised when the uploaded file type is not supported."""
    def __init__(self, message: str = "Uploaded file type is not supported.", file_name: str = ""):
        super().__init__(message)
        self.file_name = file_name

class FileValidationError(FileBaseError):
    """Exception raised when there is an error during file validation."""
    def __init__(
            self, 
            message: str = "An error occurred while validating the file.", 
            failed_files: Dict[str, FileValidationErrors] = "" # file_names -> Dict[file_name, error]
        ): 
        super().__init__(message)
        self.file_names = failed_files

class FileProcessingError(FileBaseError):
    """Exception raised when there is an error during file processing."""
    def __init__(self, message: str = "An error occurred while processing the file.", file_name: str = ""):
        super().__init__(message, file_name)

class ModelAPIBaseError(Exception):
    """Base class for model API-related exceptions."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class ModelAPIConnectionError(ModelAPIBaseError):
    """Exception raised when there is a connection error with the model API."""
    def __init__(self, message: str = "Failed to connect to the model API.", model_name: str = "Gemini"):
        super().__init__(model_name + message)

class ModelLimitReachedError(ModelAPIBaseError):
    """Exception raised when the model API limit is reached."""
    def __init__(self, message: str = "Model API limit reached.", model_name: str = "Gemini"):
        super().__init__(model_name + message)

class IncorrectFormattingError(ModelAPIBaseError):
    """Exception raised when the input data is incorrectly formatted for the model API."""
    def __init__(self, message: str = "Incorrectly formatted input data for the model API."):
        super().__init__(message)

class IncorrectGradingError(ModelAPIBaseError):
    """Exception raised when the model API returns an incorrect grading result."""
    def __init__(self, message: str = "Incorrect grading result from the model API."):
        super().__init__(message)



