#!/bin/bash

# Define environment name and project directory
ENV_NAME="fastapi_quiz_app"
PROJECT_DIR="backend"
APP_DIR="$PROJECT_DIR/app"
API_DIR="$APP_DIR/api"
API_ENDPOINTS_DIR="$API_DIR/endpoints"
CORE_DIR="$APP_DIR/core"
CRUD_DIR="$APP_DIR/crud"
DB_DIR="$APP_DIR/db"
MODELS_DIR="$APP_DIR/models"
SCHEMAS_DIR="$APP_DIR/schemas"

# Create a new Conda environment
conda create -y -n $ENV_NAME python=3.11
# Activate the newly created environment
conda activate $ENV_NAME

# Install FastAPI and Uvicorn
conda install -y -c conda-forge fastapi uvicorn

# Create project directories
mkdir -p "$API_ENDPOINTS_DIR" "$CORE_DIR" "$CRUD_DIR" "$DB_DIR" "$MODELS_DIR" "$SCHEMAS_DIR"

# Create initial Python files
touch "$APP_DIR/__init__.py" \
      "$API_DIR/__init__.py" \
      "$API_ENDPOINTS_DIR/__init__.py" \
      "$API_ENDPOINTS_DIR/users.py" \
      "$API_ENDPOINTS_DIR/questions.py" \
      "$CORE_DIR/__init__.py" \
      "$CORE_DIR/config.py" \
      "$CRUD_DIR/__init__.py" \
      "$CRUD_DIR/crud_users.py" \
      "$CRUD_DIR/crud_questions.py" \
      "$DB_DIR/__init__.py" \
      "$DB_DIR/base.py" \
      "$DB_DIR/session.py" \
      "$MODELS_DIR/__init__.py" \
      "$MODELS_DIR/users.py" \
      "$MODELS_DIR/questions.py" \
      "$SCHEMAS_DIR/__init__.py" \
      "$SCHEMAS_DIR/users.py" \
      "$SCHEMAS_DIR/questions.py" \
      "$PROJECT_DIR/main.py"

echo "FastAPI project setup with Conda completed."
