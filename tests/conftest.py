"""
Pytest configuration and shared fixtures for FastAPI tests.

This module provides reusable test fixtures including the TestClient
for making HTTP requests to the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture: FastAPI TestClient instance.
    
    Provides a client for making HTTP requests to the FastAPI application
    without requiring a running server. The client is scoped per test function.
    
    Yields:
        TestClient: Configured test client for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture
def valid_activity():
    """
    Fixture: Valid activity name that exists in the app.
    
    Returns:
        str: Name of an existing activity in the in-memory database.
    """
    return "Chess Club"


@pytest.fixture
def invalid_activity():
    """
    Fixture: Invalid activity name that does not exist.
    
    Returns:
        str: Name of a non-existent activity.
    """
    return "Nonexistent Activity"


@pytest.fixture
def valid_email():
    """
    Fixture: Valid email address.
    
    Returns:
        str: A new/unique email for testing signup.
    """
    return "test.student@mergington.edu"


@pytest.fixture
def existing_email():
    """
    Fixture: Email that already exists in an activity's participants list.
    
    Returns:
        str: Email of an existing participant in Chess Club.
    """
    return "michael@mergington.edu"
