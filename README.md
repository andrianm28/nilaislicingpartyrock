# Business Name Generator Pro

A serverless AI-powered business name generator built with AWS Lambda, API Gateway (Function URLs), Amazon Bedrock, and S3.

## Architecture

- **Frontend**: Static HTML/CSS/JS hosted on S3 (dark theme)
- **Backend**: Streaming Flask Lambda using Lambda Web Adapter
- **AI Model**: Claude Haiku 4.5 via Amazon Bedrock (global cross-region inference)
- **Deployment**: GitHub Actions with AWS SAM

## How It Works

1. User enters an industry, optional keywords, and picks a naming style
2. Clicks "Generate Business Names"
3. The app streams 10 AI-generated business name ideas with explanations in real-time

## Project Structure

```
.
├── frontend/
│   └── index.html              # Single-page app (dark theme)
├── lambdas/
│   └── business_name_ideas/
│       ├── app.py              # Flask streaming app
│       ├── requirements.txt    # Python dependencies
│       └── run.sh              # Lambda Web Adapter entrypoint
├── infra/
│   └── template.yaml          # AWS SAM template
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD pipeline
└── README.md
```

## Pre-Deployment Checklist

### 1. Enable Bedrock Model Access

In the AWS Console → Amazon Bedrock → Model Access (region: `ap-southeast-1`):

- Enable **Claude Haiku 4.5** (`global.anthropic.claude-haiku-4-5-20251001-v1:0-20260217-v1:0`)

> The `global.` inference profile routes requests worldwide for maximum throughput.
> First-time accounts may need to submit a use-case form.

### 2. Create an S3 Bucket for SAM Deployments

```bash
aws s3 mb s3://your-sam-deploy-bucket --region ap-southeast-1
```

### 3. Configure GitHub Secrets

In your GitHub repo → Settings → Secrets and variables → Actions:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM access key with deploy permissions |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `SAM_DEPLOY_BUCKET` | S3 bucket name for SAM artifacts |

### 4. IAM Permissions for Deployment

The deploying IAM user/role needs:
- CloudFormation full access
- S3 full access
- Lambda full access
- IAM role creation (for the Bedrock role)
- Bedrock model access

## Deployment

Push to `main` branch or trigger the workflow manually:

```bash
git add .
git commit -m "Initial deploy"
git push origin main
```

The GitHub Actions workflow will:
1. Build the SAM template
2. Deploy the CloudFormation stack
3. Inject Lambda Function URLs into the frontend
4. Sync the frontend to S3

## Local Development

### Run the Lambda locally:

```bash
cd lambdas/business_name_ideas
pip install -r requirements.txt
python app.py
```

Then test with curl:

```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"industry": "coffee shop", "name_style": "Modern", "keywords": "cozy, urban"}'
```

## Tech Stack

- Python 3.12 + Flask (streaming)
- AWS Lambda with Lambda Web Adapter (response streaming)
- Amazon Bedrock (Claude Haiku 4.5 - global inference profile)
- AWS SAM for infrastructure
- S3 static website hosting
- GitHub Actions CI/CD
