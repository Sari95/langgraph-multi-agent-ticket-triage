# LangGraph Multi-Agent Support Triage

This repository contains a complete, practical example of a multi-agent system designed to automate customer support ticket triage. Built with LangGraph, it routes incoming tickets based on priority and automatically drafts responses or escalates urgent cases to human review.

The system is model-agnostic and can switch seamlessly between a local backend (Ollama/Llama 3) and a cloud backend (OpenAI API).

Step-by-Step Tutorial: For a detailed breakdown of the architecture, design choices, and how the code works under the hood, check out the accompanying Medium Article: 

---

## Prerequisites

Before running the script, make sure you have the following installed on your machine:
* Python 3.10 or higher
* [Ollama](https://ollama.com/) (if you want to run the model locally)

---

## Setup & Installation: Follow these steps to get the project running on your local machine:

```bash
### 1. Clone the Repository
git clone [https://github.com/Sari95/langgraph-multi-agent-ticket-triage.git](https://github.com/Sari95/langgraph-multi-agent-ticket-triage.git)
cd langgraph-multi-agent-ticket-triage

### 2. Create and Activate a Virtual Environment
I recommend using a virtual environment to keep your dependencies clean.
On Windows:
python -m venv myenv
myenv\Scripts\activate

On macOS/Linux:
python -m venv myenv
source myenv/bin/activate

### 3. Install the Core Packages
pip install langgraph langchain-openai langchain-community

### Running Locally (Ollama)
ollama pull llama3



