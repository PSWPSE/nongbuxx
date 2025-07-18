# 🔧 .env 파일 업데이트 가이드

## 📋 업데이트해야 할 항목들

### 1. API 키 (이미 가지고 있다면)

```bash
# 현재 상태 (템플릿)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# 변경 후 (실제 API 키로)
ANTHROPIC_API_KEY=sk-ant-api03-실제키값
OPENAI_API_KEY=sk-실제키값
```

### 2. 보안 키 (개발용)

```bash
# 현재 상태 (템플릿)
SECRET_KEY=your-secret-key-at-least-32-characters-long
JWT_SECRET_KEY=your-jwt-secret-key-at-least-32-chars
ENCRYPTION_KEY=32-character-encryption-key-here

# 변경 후 (개발용 간단한 값)
SECRET_KEY=dev-secret-key-for-local-development-only
JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only
ENCRYPTION_KEY=dev32charactersencryptionkeyhere
```

## 🔄 전체 .env 파일 예시 (로컬 개발용)

```bash
# API Keys - 최소 하나는 필요합니다
ANTHROPIC_API_KEY=sk-ant-api03-실제키값여기에입력
OPENAI_API_KEY=sk-실제키값여기에입력

# Application Settings
FLASK_ENV=development
DEBUG=False
PORT=8080

# Database Configuration
DATABASE_URL=sqlite:///nongbuxx.db

# Security & Authentication (개발용)
SECRET_KEY=dev-secret-key-for-local-development-only
JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only
ENCRYPTION_KEY=dev32charactersencryptionkeyhere

# Email Configuration (선택사항 - 주석 그대로 유지)
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=true
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-specific-password
```

## ⚡ 빠른 업데이트 명령어

터미널에서 직접 업데이트:

```bash
# 보안 키 업데이트 (개발용)
sed -i '' 's/SECRET_KEY=.*/SECRET_KEY=dev-secret-key-for-local-development-only/' .env
sed -i '' 's/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=dev-jwt-secret-key-for-local-only/' .env
sed -i '' 's/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=dev32charactersencryptionkeyhere/' .env
```

## ✅ 설정 완료 확인

Python에서 실행:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# 설정 확인
print("✅ 설정 상태:")
print(f"- ANTHROPIC_API_KEY: {'설정됨' if os.getenv('ANTHROPIC_API_KEY') != 'your_anthropic_api_key_here' else '❌ 기본값'}")
print(f"- OPENAI_API_KEY: {'설정됨' if os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else '❌ 기본값'}")
print(f"- SECRET_KEY: {'설정됨' if 'dev-secret' in os.getenv('SECRET_KEY', '') else '❌ 기본값'}")
print(f"- DATABASE_URL: {os.getenv('DATABASE_URL')}")
``` 