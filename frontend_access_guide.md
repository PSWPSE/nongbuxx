# Vercel 프론트엔드 접근권한 설정 가이드

## 🔍 현재 상황
- ✅ 메인 URL 정상: https://nongbuxxfrontend.vercel.app/
- ✅ 프로젝트 URL 정상: https://nongbuxxfrontend-dsvsdvsdvsds-projects.vercel.app/
- ⚠️ 특정 배포 URL 제한: https://nongbuxxfrontend-6n5noq7lr-dsvsdvsdvsds-projects.vercel.app/

## 🔧 해결 방법

### 1. 즉시 사용 가능한 방법
**메인 URL 사용**: https://nongbuxxfrontend.vercel.app/
- 이 URL은 이미 정상 작동하며 접근 제한이 없음
- 백엔드 연결도 정상 작동함

### 2. Vercel 대시보드에서 보안 설정 변경

#### A. 브라우저에서 Vercel 대시보드 접속
1. https://vercel.com/ 로그인
2. 프로젝트 목록에서 "nongbuxx_frontend" 선택

#### B. Deployment Protection 설정 변경
1. 프로젝트 페이지 → "Settings" 탭 클릭
2. "General" 섹션으로 이동
3. "Deployment Protection" 찾기
4. 설정 옵션:
   - **None**: 모든 배포에 공개 접근 허용
   - **Vercel Authentication**: Vercel 계정 필요
   - **Password Protection**: 비밀번호 입력 필요

#### C. 권장 설정
```
Deployment Protection: None
```
또는
```
Deployment Protection: Vercel Authentication
→ "Bypass for Automation" 체크
```

### 3. CLI를 통한 프로젝트 설정 변경

#### A. 프로젝트 재배포 (공개 설정으로)
```bash
cd frontend
vercel --prod --public
```

#### B. 환경 변수 확인
```bash
vercel env ls
```

#### C. 도메인 별칭 추가
```bash
vercel alias https://nongbuxxfrontend-6n5noq7lr-dsvsdvsdvsds-projects.vercel.app nongbuxx.vercel.app
```

### 4. Team/Organization 설정 확인

#### A. 현재 팀 확인
```bash
vercel teams ls
```

#### B. 팀 설정 변경 (필요시)
```bash
vercel teams switch [team-id]
```

## 🚀 권장 솔루션

### 즉시 해결 (권장)
1. **메인 URL 사용**: `https://nongbuxxfrontend.vercel.app/`
2. 프론트엔드 config.js에서 이 URL 참조
3. 문서/링크에서 이 URL 사용

### 장기적 해결
1. Vercel 대시보드에서 Deployment Protection 비활성화
2. 커스텀 도메인 설정 (선택사항)
3. 환경별 접근 제어 정책 수립

## 🔗 최종 서비스 URL
- **프론트엔드**: https://nongbuxxfrontend.vercel.app/
- **백엔드**: https://nongbuxxbackend-production.up.railway.app/
- **연결 상태**: ✅ 정상 작동

## 📝 추가 보안 옵션

### 1. Environment Variables
```bash
# Vercel 환경 변수 설정
vercel env add NEXT_PUBLIC_API_URL production
# 값: https://nongbuxxbackend-production.up.railway.app
```

### 2. Custom Headers (vercel.json)
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options", 
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

### 3. IP 화이트리스트 (Enterprise 기능)
- Vercel Pro/Enterprise에서 제공
- 특정 IP 주소에서만 접근 허용

## 🛠️ 트러블슈팅

### 문제: 401 Unauthorized
**원인**: Deployment Protection 활성화
**해결**: 메인 alias URL 사용 또는 보안 설정 변경

### 문제: 404 Not Found
**원인**: 잘못된 라우팅 또는 빌드 오류
**해결**: vercel.json의 rewrites 설정 확인

### 문제: CORS 오류
**원인**: 백엔드 CORS 설정 문제
**해결**: 이미 해결됨 (백엔드에서 Vercel 도메인 허용)

## 📞 추가 지원
- Vercel 문서: https://vercel.com/docs
- Vercel 지원: https://vercel.com/support
- Discord 커뮤니티: https://vercel.com/discord
