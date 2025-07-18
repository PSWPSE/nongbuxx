# NONGBUXX Frontend Vercel 배포 가이드

## 🎯 안정적인 배포를 위한 최종 솔루션

### 📋 전제 조건
- GitHub 저장소: https://github.com/PSWPSE/nongbuxx
- Frontend 경로: `/frontend`
- Vercel 프로젝트: nongbuxxfrontend

### ✅ 권장 방법: Vercel Dashboard 설정

#### 1단계: Vercel 대시보드 접속
1. https://vercel.com/dashboard 로그인
2. `nongbuxxfrontend` 프로젝트 선택

#### 2단계: 프로젝트 설정 변경
1. **Settings** 탭 클릭
2. **General** 섹션으로 이동
3. 다음 설정 적용:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Other`
   - **Build Command**: ` ` (빈 칸으로 설정)
   - **Output Directory**: ` ` (빈 칸으로 설정)
   - **Install Command**: ` ` (빈 칸으로 설정)

#### 3단계: 재배포
1. **Save** 버튼 클릭
2. **Deployments** 탭으로 이동
3. 최신 배포 옆의 **...** 메뉴 클릭
4. **Redeploy** 선택
5. **Redeploy** 확인

### 🔧 대안: 코드 기반 설정

만약 코드로 관리하고 싶다면:

#### frontend/vercel.json (이미 존재)
```json
{
  "version": 2,
  "buildCommand": "echo 'No build needed for static files'",
  "outputDirectory": ".",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
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

### ⚠️ 주의사항
1. **루트에 vercel.json을 만들지 마세요** - 혼란만 야기합니다
2. **Dashboard 설정이 코드보다 우선순위가 높습니다**
3. **한 가지 방법만 사용하세요** - 혼용하지 마세요

### 🚀 배포 확인

#### 배포 성공 확인:
1. Vercel Dashboard에서 초록색 체크 표시 확인
2. https://nongbuxxfrontend.vercel.app/ 접속
3. 최신 변경사항 반영 확인

#### 문제 해결:
- **404 에러**: Root Directory 설정 재확인
- **빌드 실패**: Build Command를 빈 칸으로 설정
- **캐시 문제**: 브라우저 강제 새로고침 (Ctrl+Shift+R)

### 📱 연락처
문제가 지속될 경우:
1. Vercel Support: https://vercel.com/support
2. GitHub Issues: https://github.com/PSWPSE/nongbuxx/issues

---
마지막 업데이트: 2025-07-18 