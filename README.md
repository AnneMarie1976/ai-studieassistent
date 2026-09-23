# GenAI Study Assistant 🎓

An AI-powered web application that generates concise study summaries and interactive quizzes from text inputs.

## 🚀 Live Demo
- **Frontend App:** https://main.d2dfqbgh0r3fv.amplifyapp.com

## 🛠️ Tech Stack & Architecture
- **Frontend:** AWS Amplify (HTML/JS)
- **API Layer:** Amazon API Gateway (`POST /generate`)
- **Backend:** AWS Lambda (Python 3.12, Serverless)
- **AI Integration:** Google Gemini API (`v1beta`)

[User] -> [AWS Amplify] -> [API Gateway] -> [AWS Lambda] -> [Google Gemini API]

## ✨ Features & Resilience
- **Serverless Architecture:** Cost-effective and automatically scalable.
- **Error Handling & Fallback:** Lambda automatically retries and rotates models upon receiving HTTP `503 Service Unavailable` rate-limit errors from Google Gemini API.
- **CORS Configured:** Secure interaction between Amplify frontend and Gateway endpoints.