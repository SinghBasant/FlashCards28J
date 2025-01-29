from typing import Dict, List
import os
import streamlit as st
from gemini_service import GeminiService

# Predefined domains for each certification
CERTIFICATION_DOMAINS = {
    "AWS Certified AI Practitioner": [
        "Fundamentals of AI and ML",
        "Fundamentals of Generative AI",
        "Applications of Foundation Models",
        "Guidelines for Responsible AI",
        "Security, Compliance, and Governance for AI Solutions"
    ],
    "Exam AZ-104: Microsoft Azure Administrator": [
        "Manage Azure identities and governance",
        "Implement and manage storage",
        "Deploy and manage Azure compute resources",
        "Implement and manage virtual networking",
        "Monitor and maintain Azure resources"
    ],
    "NVIDIA-Certified Associate: Generative AI and LLMs": [
        "Core Machine Learning and AI Knowledge",
        "Data Analysis",
        "Experimentation",
        "Software Development",
        "Trustworthy AI"
    ],
    "Google Cloud Certified Cloud Digital Leader": [
        "Digital transformation with Google Cloud",
        "Exploring data transformation with Google Cloud",
        "Innovating with Google Cloud artificial intelligence",
        "Modernizing infrastructure and applications with Google Cloud",
        "Trust and security with Google Cloud",
        "Scaling with Google Cloud operations"
    ],
    "AWS Certified Data Engineer Associate": [
        "Data Ingestion and Transformation",
        "Data Store Management",
        "Data Operations and Support",
        "Data Security and Governance"
       
    ],
    "AWS Certified Solutions Architect Associate": [
        "Design Secure Architectures",
        "Design Resilient Architectures",
        "Design High-Performing Architectures",
        "Design Cost-Optimized Architectures"
    ]
}

def get_api_key() -> str:
    """Get Gemini API key from either streamlit secrets or environment variable."""
    # First try to get from streamlit secrets
    api_key = st.secrets.get("GEMINI_API_KEY")
    
    # If not in secrets, try environment variable
    if not api_key:
        api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "Gemini API key not found. Please set it either in .streamlit/secrets.toml "
            "or as an environment variable 'GEMINI_API_KEY'"
        )
    
    return api_key

# Initialize Gemini service with API key
try:
    gemini_service = GeminiService(get_api_key())
except ValueError as e:
    st.error(str(e))
    st.stop()

def get_certification_data(certification_name: str, domain: str, num_cards: int = 5) -> List[Dict[str, str]]:
    """
    Fetch certification data from Gemini API for a specific domain.
    Returns list of flashcards for the specified domain.
    """
    return gemini_service.generate_flashcards(certification_name, domain, num_cards)

# List of supported certifications
SUPPORTED_CERTIFICATIONS = list(CERTIFICATION_DOMAINS.keys())

# Cache for storing generated content to avoid repeated API calls
certification_cache = {}

def get_cached_certification_data(certification_name: str, domain: str, num_cards: int = 5) -> List[Dict[str, str]]:
    """
    Get certification data with caching to minimize API calls.
    """
    cache_key = f"{certification_name}_{domain}_{num_cards}"
    if cache_key not in certification_cache:
        certification_cache[cache_key] = get_certification_data(certification_name, domain, num_cards)
    return certification_cache[cache_key]

"""
Original static data structure (kept as reference):
CERTIFICATIONS = {
    "AWS Certified AI Practitioner": {
        "Machine Learning Concepts": [
            {
                "question": "What is the difference between supervised and unsupervised learning?",
                "answer": "Supervised learning uses labeled data for training, while unsupervised learning finds patterns in unlabeled data."
            },
            ...
        ],
        ...
    },
    ...
}
"""