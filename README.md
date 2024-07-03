# Ayushma AI

This is a Django Project

## Requirements

- OpenAI Account with a valid API Key
- Pinecone Account with a valid API Key
- Docker

## Optional Requirements

- AWS SES Accout
- AWS S3 Account
- Google Cloud account with access to speech to text API

## Running the Project

> We strongly recommend using Docker to run the project. Manual methods are not supported at the moment.

```bash
make up
```

## Env Variables

Add these environment variables to your `.env` file.

| Variable                       | Description                                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------- |
| AI_NAME                        | Name of the AI (default: Ayushma)                                                                                    |
| OPENAI_API_KEY                 | OpenAI API Key                                                                                                       |
| PINECONE_API_KEY               | Pinecone API Key                                                                                                     |
| PINECONE_INDEX                 | Pinecone Index                                                                                                       |
| CURRENT_DOMAIN                 | Current Domain where the frontend is hosted. ex. `https://ayushma.ohc.network`                                       |
| EMAIL_HOST                     | SES Email Host (Optional)                                                                                            |
| EMAIL_USER                     | SES Email User (Optional)                                                                                            |
| EMAIL_PASSWORD                 | SES Email Password (Optional)                                                                                        |
| GOOGLE_APPLICATION_CREDENTIALS | Google Cloud Credentials (Optional). These should be in a file named `gc_credential.json` in the root of the project |
| S3_SECRET_KEY                  | AWS S3 Secret Key (Optional)                                                                                         |
| S3_KEY_ID                      | AWS S3 Key ID (Optional)                                                                                             |
| S3_BUCKET_NAME                 | AWS S3 Bucket Name (Optional)                                                                                        |
| S3_REGION                      | AWS S3 Region (Optional)                                                                                             |
| GOOGLE_RECAPTCHA_SECRET_KEY    | Google Recaptcha Secret Key (Optional)                                                                               |

## Google Cloud

To use Google Cloud Speech to Text API, you need to enable the API and create a service account. Download the credentials and save them in a file named `gc_credential.json` in the root of the project.
