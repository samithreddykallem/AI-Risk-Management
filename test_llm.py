"""
Test script to verify LLM client connectivity and response handling.
Reads LLM configuration securely from environment variables / .env.
"""
import sys
import os

from ai_engine.llm.provider_factory import get_llm_provider
from ai_engine.models.system_profile import SystemProfile


def test_llm_connection():
    print("[*] Initializing reusable LLM client...")
    llm = get_llm_provider()
    print(f"[*] Provider active: {llm.__class__.__name__}")

    print("\n--- Test 1: Text Generation ---")
    prompt = "Say hello and give a one-sentence overview of AI risk auditing."
    try:
        response_text = llm.generate_text(prompt=prompt)
        print(f"Response:\n{response_text}")
    except Exception as e:
        print(f"[!] Text generation failed: {e}")

    print("\n--- Test 2: Structured JSON Schema Generation ---")
    structured_prompt = "Generate a system profile for a healthcare patient diagnostic recommendation AI assistant."
    try:
        profile = llm.generate_structured(prompt=structured_prompt, schema=SystemProfile)
        print(f"Structured Output:\nSystem Name: {profile.system_name}\nDomain: {profile.primary_domain}\nSummary: {profile.profile_summary}")
    except Exception as e:
        print(f"[!] Structured JSON generation failed: {e}")


if __name__ == "__main__":
    test_llm_connection()
