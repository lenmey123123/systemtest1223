from setuptools import setup, find_packages

setup(
    name="saas-agents",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
        "aiohttp",
        "asyncio",
    ],
) 