#!/usr/bin/env python3
"""Quick script to check environment variables"""
import os
from app.config import settings

print("=" * 60)
print("Environment Variables Check")
print("=" * 60)

print(f"\nDATABASE_URL from os.getenv: {os.getenv('DATABASE_URL', 'NOT SET')[:50]}...")
print(f"settings.database_url: {settings.database_url[:50]}...")
print(f"\nANTHROPIC_API_KEY: {'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'}")
print(f"SECRET_KEY: {'SET' if os.getenv('SECRET_KEY') else 'NOT SET'}")
print(f"PORT: {os.getenv('PORT', 'NOT SET')}")
print(f"HOST: {os.getenv('HOST', 'NOT SET')}")

print("\n" + "=" * 60)
print("Configuration Summary")
print("=" * 60)
print(f"Database URL points to: {settings.database_url.split('@')[1].split('/')[0] if '@' in settings.database_url else 'localhost'}")
print("=" * 60)
