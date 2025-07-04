"""
FastAPI exception handlers for database constraint violations.

This module provides centralized error handling for SQLAlchemy IntegrityError
exceptions, transforming them into user-friendly HTTP 400 responses.
"""

import re
import logging
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


def add_error_handlers(app: FastAPI) -> None:
    """Add database error handlers to FastAPI app."""
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        """Handle database integrity constraint violations."""
        
        logger.warning(f"Database integrity error on {request.method} {request.url}: {exc}")
        
        # Parse the error message for user-friendly response
        error_detail = parse_integrity_error(str(exc))
        
        return JSONResponse(
            status_code=400,
            content={
                "error": "Constraint Violation",
                "detail": error_detail["message"],
                "type": error_detail["type"],
                "field": error_detail.get("field"),
                "value": error_detail.get("value")
            }
        )


def parse_integrity_error(error_message: str) -> Dict[str, Any]:
    """
    Parse SQLAlchemy IntegrityError messages into user-friendly format.
    
    Args:
        error_message: The string representation of the IntegrityError
        
    Returns:
        Dict containing error type, message, and optional field/value info
    """
    
    # Foreign key constraint pattern
    if "FOREIGN KEY constraint failed" in error_message:
        return parse_foreign_key_error(error_message)
    
    # Unique constraint pattern  
    unique_pattern = r"UNIQUE constraint failed: (\w+)\.(\w+)"
    unique_match = re.search(unique_pattern, error_message)
    if unique_match:
        table, field = unique_match.groups()
        return {
            "type": "unique_violation",
            "field": field,
            "message": get_unique_constraint_message(field)
        }
    
    # Check constraint pattern
    if "CHECK constraint failed" in error_message:
        return parse_check_constraint_error(error_message)
    
    # Generic constraint violation
    return {
        "type": "constraint_violation",
        "message": "Database constraint violation occurred"
    }


def parse_foreign_key_error(error_message: str) -> Dict[str, Any]:
    """
    Parse foreign key constraint errors to extract field and value information.
    
    Args:
        error_message: The IntegrityError message string
        
    Returns:
        Dict with error details including field and value if extractable
    """
    
    # Try to extract field and value from INSERT statement using positional matching
    field_pattern = r"INSERT INTO \w+ \(([^)]+)\)"
    value_pattern = r"VALUES \(([^)]+)\)"
    
    field_match = re.search(field_pattern, error_message)
    value_match = re.search(value_pattern, error_message)
    
    if field_match and value_match:
        fields = [f.strip() for f in field_match.group(1).split(',')]
        values = [v.strip() for v in value_match.group(1).split(',')]
        
        # Find the first foreign key field and its corresponding value
        for i, field in enumerate(fields):
            if field.endswith('_id') and i < len(values):
                value_str = values[i].strip('\'"')
                if value_str.isdigit():
                    return {
                        "type": "foreign_key_violation",
                        "field": field,
                        "value": int(value_str),
                        "message": get_foreign_key_message(field, value_str)
                    }
    
    # Try to extract field from UPDATE statement
    update_pattern = r"UPDATE \w+ SET\s+(\w+_id)\s*=\s*(\d+)"
    update_match = re.search(update_pattern, error_message)
    
    if update_match:
        field, value = update_match.groups()
        return {
            "type": "foreign_key_violation", 
            "field": field,
            "value": int(value),
            "message": get_foreign_key_message(field, value)
        }
    
    # Generic foreign key error
    return {
        "type": "foreign_key_violation",
        "message": "Invalid foreign key reference"
    }


def parse_check_constraint_error(error_message: str) -> Dict[str, Any]:
    """
    Parse check constraint errors.
    
    Args:
        error_message: The IntegrityError message string
        
    Returns:
        Dict with error details
    """
    
    # Try to extract constraint name
    check_pattern = r"CHECK constraint failed: (\w+)"
    check_match = re.search(check_pattern, error_message)
    
    if check_match:
        constraint_name = check_match.group(1)
        return {
            "type": "check_violation",
            "constraint": constraint_name,
            "message": f"Invalid value for {constraint_name}"
        }
    
    return {
        "type": "check_violation",
        "message": "Invalid value provided"
    }


def get_foreign_key_message(field: str, value: str) -> str:
    """
    Generate user-friendly message for foreign key constraint violations.
    
    Args:
        field: The foreign key field name (e.g., "role_id")
        value: The invalid foreign key value
        
    Returns:
        User-friendly error message
    """
    
    # Map foreign key fields to user-friendly names
    field_names = {
        "role_id": "role",
        "user_id": "user", 
        "question_id": "question",
        "answer_choice_id": "answer choice",
        "group_id": "group",
        "time_period_id": "time period",
        "creator_id": "creator",
        "subject_id": "subject",
        "topic_id": "topic",
        "subtopic_id": "subtopic", 
        "concept_id": "concept",
        "discipline_id": "discipline",
        "domain_id": "domain",
        "question_set_id": "question set",
        "question_tag_id": "question tag",
        "permission_id": "permission"
    }
    
    friendly_name = field_names.get(field, field.replace("_id", ""))
    return f"Invalid {friendly_name}: {value}"


def get_unique_constraint_message(field: str) -> str:
    """
    Generate user-friendly message for unique constraint violations.
    
    Args:
        field: The field with unique constraint violation
        
    Returns:
        User-friendly error message
    """
    
    # Field-specific messages for better UX
    field_messages = {
        "email": "A user with this email already exists",
        "username": "A user with this username already exists", 
        "name": "A record with this name already exists",
        "slug": "A record with this identifier already exists"
    }
    
    return field_messages.get(field, f"A record with this {field} already exists")