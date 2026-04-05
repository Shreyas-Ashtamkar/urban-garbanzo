"""Setup configuration for urban-garbanzo."""
from setuptools import setup, find_packages

setup(
    name="urban-garbanzo",
    version="0.1.0",
    description="Stop guessing if your prompts work. Get instant ratings on clarity, correctness, information density, hallucination risk, and redundancy.",
    author="Shreyas Ashtamkar",
    author_email="shreyas@example.com",
    url="https://github.com/Shreyas-Ashtamkar/urban-garbanzo",
    license="GPL-2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "tortoise-orm==0.20.0",
        "asyncpg==0.29.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "python-dotenv==1.0.0",
        "httpx==0.25.2",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-asyncio==0.21.1",
            "pytest-cov==4.1.0",
            "black==23.12.0",
            "ruff==0.1.8",
            "mypy==1.7.1",
            "pre-commit==3.5.0",
            "ipython==8.18.1",
        ],
    },
)
