import os
import json
from google import generativeai as genai
from google.generativeai import types

MODEL_NAME = "gemini-2.5-flash-preview-05-20"


def _client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")
    return genai.Client(api_key=api_key)


def extract_search_params(description: str) -> dict:
    """Use Gemini to transform a natural language description into Addgene search parameters."""
    client = _client()
    prompt = (
        "Given the following plasmid design request, return JSON with fields 'query', 'vector_types', 'expression', 'species', and 'plasmid_type' if applicable.\n"  # noqa: E501
        "Only output the JSON.\n\n" + description
    )
    contents = [types.Content(role="user", parts=[types.Part.from_text(prompt)])]
    response = ""
    for chunk in client.models.generate_content_stream(model=MODEL_NAME, contents=contents):
        response += chunk.text
    try:
        data = json.loads(response)
        return {k: v for k, v in data.items() if v}
    except json.JSONDecodeError:
        return {"query": description}


def design_plasmid(description: str, protein_sequence: str) -> str:
    """Ask Gemini to design a plasmid from a description and protein sequence."""
    client = _client()
    prompt = (
        "Design an E. coli expression plasmid. Use the following protein sequence as the coding sequence. Provide the final plasmid in FASTA format.\n"
        f"Protein sequence:\n{protein_sequence}\n\n"
        f"Description: {description}"
    )
    contents = [types.Content(role="user", parts=[types.Part.from_text(prompt)])]
    response = ""
    for chunk in client.models.generate_content_stream(model=MODEL_NAME, contents=contents):
        response += chunk.text
    return response.strip()
