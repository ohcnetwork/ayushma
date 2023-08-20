# Ayushma AI

This is a Django Project.

## Requirements

- Python 3.8
- Postgres 15
- OpenAI Account with a valid API Key
- Pinecone Account with a valid API Key

## Optional Requirements

- Docker
- AWS SES Accout
- AWS S3 Account
- Google Cloud account with access to speech to text API

## Installation

create a virtual environment and install the requirements

```bash
pip3 install --user virtualenv
virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements/local.txt
```

## Env Variables

You can add these at the end of your `activate` file in `[virtualenvfolder] -> bin` like `export [env] = [value]`

| Variable | Description
| --- | ---
| AI_NAME | Name of the AI (default: Ayushma)
| OPENAI_API_KEY | OpenAI API Key 
| PINECONE_API_KEY | Pinecone API Key 
| PINECONE_ENVIRONMENT | Pinecone Environment
| PINECONE_INDEX | Pinecone Index
| CURRENT_DOMAIN | Current Domain where the frontend is hosted. ex. `https://ayushma.ohc.network`
| EMAIL_HOST | SES Email Host (Optional)
| EMAIL_USER | SES Email User (Optional)
| EMAIL_PASSWORD | SES Email Password (Optional)
| GOOGLE_APPLICATION_CREDENTIALS | Google Cloud Credentials (Optional). These should be in a file named `gc_credential.json` in the root of the project
| S3_SECRET_KEY | AWS S3 Secret Key (Optional)
| S3_KEY_ID | AWS S3 Key ID (Optional)
| S3_BUCKET_NAME | AWS S3 Bucket Name (Optional)
| S3_REGION | AWS S3 Region (Optional)