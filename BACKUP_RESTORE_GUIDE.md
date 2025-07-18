# 🔄 NONGBUXX 백업 및 복원 가이드

## 📅 백업 정보
- **백업 일시**: 2025년 7월 18일 22:35
- **백업 버전**: v1.0.0-before-auth
- **백업 이유**: 로그인 기능 추가 전 안정된 버전 보존

## 🗄️ 백업 내용

### 1. Git 태그
- **태그명**: `v1.0.0-before-auth`
- **설명**: 로그인 기능 추가 전 마지막 안정 버전
- **GitHub에 동기화됨**: ✅

### 2. Git 브랜치
- **현재 작업 브랜치**: `feature/login-system`
- **안정 버전 브랜치**: `main`

### 3. 전체 프로젝트 백업
- **위치**: `backups/nongbuxx-before-auth-20250718-223514.zip`
- **크기**: 188KB
- **포함 내용**: 모든 소스 코드, 설정 파일, 프론트엔드 파일

## 🔧 복원 방법

### 방법 1: Git 태그로 복원 (권장)

```bash
# 현재 변경사항 확인
git status

# 변경사항이 있다면 stash로 임시 저장
git stash

# 백업된 태그로 체크아웃
git checkout v1.0.0-before-auth

# 또는 main 브랜치로 돌아가기
git checkout main
```

### 방법 2: 특정 시점으로 완전 복원

```bash
# 현재 브랜치의 변경사항을 모두 버리고 태그 시점으로 복원
git reset --hard v1.0.0-before-auth

# 원격 저장소와 동기화
git push --force origin main
```

### 방법 3: ZIP 백업에서 복원

```bash
# 백업 디렉토리로 이동
cd ~/

# 새 디렉토리에 압축 해제
unzip /Users/alphabridge/nongbuxx/backups/nongbuxx-before-auth-20250718-223514.zip -d nongbuxx-restored

# 기존 프로젝트 백업
mv nongbuxx nongbuxx-with-login

# 복원된 프로젝트로 교체
mv nongbuxx-restored nongbuxx
```

## ⚠️ 주의사항

1. **데이터베이스**: 현재는 DB가 없으므로 파일 시스템만 복원하면 됨
2. **생성된 콘텐츠**: `generated_content/` 폴더는 백업에 포함되지 않음
3. **환경 변수**: `.env` 파일은 백업에 포함됨

## 🚀 로그인 기능 개발 진행 시

```bash
# 현재 브랜치 확인
git branch

# feature/login-system 브랜치에서 작업
git checkout feature/login-system

# 작업 진행...
```

## 🔍 백업 상태 확인

```bash
# Git 태그 목록 확인
git tag -l

# 현재 브랜치 확인
git branch

# 백업 파일 확인
ls -la backups/
```

## 📝 추가 백업 권장사항

로그인 기능 개발 중 주요 마일스톤마다 추가 백업 생성:
```bash
# 예시: 데이터베이스 설정 완료 후
git tag -a v1.1.0-db-setup -m "데이터베이스 설정 완료"
git push origin v1.1.0-db-setup
``` 