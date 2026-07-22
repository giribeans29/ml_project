# Agentic ML Project

## Overview
This repository contains the backend architecture for an agentic machine learning application. It orchestrates complex, stateful LLM workflows using **LangGraph**, serves client requests via a **FastAPI** backend, and manages session state and data persistence using a lightweight **SQLite** database.

## Architecture Highlights
* **LangGraph:** Chosen over standard ADKs to handle cyclical execution, granular state tracking, and complex agent routing using a graph-based state machine.
* **FastAPI:** Provides a highly performant, asynchronous gateway for incoming requests with built-in Pydantic validation.
* **SQLite:** A lightweight, serverless relational database used for seamless local data handling and context retrieval.

## Prerequisites
* Python 3.9+
* API Keys for your chosen LLM provider (e.g., OpenAI)

## Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/giribeans29/ml_project.git](https://github.com/giribeans29/ml_project.git)
   cd ml_project