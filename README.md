# Ayushma AI

## Installation

create a virtual environment and install the requirements

```bash
pip3 install --user virtualenv
virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements/local.txt
```

## Required Env Variables

You can add these at the end of your `activate` file in `[virtualenvfolder] -> bin` like `export [env] = [value]`

| Variable | Description
| --- | ---
| OPENAI_API_KEY | OpenAI API Key 
| PINECONE_API_KEY | Pinecone API Key 
| PINECONE_ENVIRONMENT | Pinecone Environment
| PINECONE_INDEX | Pinecone Index
