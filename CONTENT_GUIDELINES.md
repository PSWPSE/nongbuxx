# NONGBUXX 콘텐츠 생성 가이드라인

## 개요
이 문서는 NONGBUXX 서비스에서 뉴스 기사를 한국어 마크다운 콘텐츠로 변환할 때 준수해야 할 가이드라인을 제공합니다.

## 🔍 블로그 SEO 최적화 가이드라인

### 플랫폼별 SEO 전략

#### 🟦 워드프레스 SEO 최적화
- **헤딩 구조**: H1(제목) → H2(주요 섹션) → H3(세부 항목) 계층 구조
- **키워드 최적화**: 포커스 키워드 1개, LSI 키워드 3-5개 자연스럽게 배치
- **콘텐츠 분량**: 4000-5000자 이상의 충분한 정보량
- **링크 최적화**: 내부 링크 3-5개, 신뢰할 수 있는 외부 소스 연결
- **Yoast SEO 호환**: 워드프레스 SEO 플러그인과 호환되는 구조
- **시각적 개선**: 적절한 문단 간격, 가독성 높은 폰트 크기, 여백 활용

##### 📝 워드프레스 HTML 형식 전용 가이드라인
- **창의적 제목 생성**: 원본 뉴스 제목을 절대 사용하지 않고 완전히 새로운 관점의 제목 생성
- **콘텐츠 재구성**: 원본 뉴스를 단순 요약하지 않고 새로운 스토리텔링으로 재구성
- **AI 인사이트 추가**: 관련 배경 지식, 업계 동향, 미래 전망 등 심층 분석 포함
- **데이터 강화**: 통계, 비교 분석, 추가 조사 내용으로 콘텐츠 가치 극대화
- **이미지 플레이스홀더**: 적절한 위치에 이미지 추천 사항 제공 (실제 URL 제외)
- **시각적 요소**: 하이라이트, 박스 디자인, 구분선 등으로 가독성 향상

#### 🟡 티스토리 SEO 최적화
- **카카오 검색 최적화**: 한국어 키워드 중심의 제목 및 내용 구성
- **태그 활용**: 검색량이 높은 한국어 태그 5-10개 제안
- **요약 최적화**: 티스토리 요약란에 적합한 100자 내외 요약문
- **모바일 우선**: 모바일 화면에 최적화된 짧은 문단 구성
- **사용자 참여**: 댓글 유도 및 SNS 공유 최적화
- **카테고리 활용**: IT/테크, 경제/금융 등 적절한 카테고리 분류

#### 🟢 네이버 블로그 SEO 최적화
- **네이버 검색 알고리즘**: 네이버 검색에 특화된 키워드 배치
- **키워드 밀도**: 네이버 최적화를 위한 2-4% 키워드 밀도 유지
- **연관 검색어**: 네이버 연관 검색어 기반 키워드 포함
- **네이버 생태계**: 네이버 뉴스, 지식iN 연결 및 활용
- **스마트 에디터**: 네이버 에디터 호환 구조 및 포맷
- **실시간 검색**: 트렌딩 키워드 반영한 콘텐츠 구성

### 공통 SEO 원칙
- **사용자 의도**: 정보성, 상업성, 탐색성 검색 의도 고려

## 📱 시각적 품질 및 가독성 가이드라인

### HTML 콘텐츠 시각적 개선
- **문단 간격**: margin-bottom: 1.5em, line-height: 1.8로 충분한 여백 확보
- **제목 계층**: 
  - H1: font-size: 2.5em, 진한 검정색
  - H2: font-size: 2em, 적절한 상하 여백
  - H3: font-size: 1.5em, 부드러운 회색
- **강조 요소**:
  - 하이라이트: 노란색 배경으로 중요 내용 강조
  - 박스 디자인: 회색 배경의 둥근 박스로 핵심 정보 구분
  - 구분선: 섹션 간 시각적 분리
- **모바일 최적화**: max-width: 800px로 읽기 편한 너비 제한
- **신뢰성**: 출처 명확 표기 및 데이터 기반 내용
- **가독성**: 짧은 문단, 불릿 포인트, 시각적 구성 요소 활용
- **모바일 최적화**: 모든 플랫폼에서 모바일 친화적 구조

## 주식 심볼 처리 규칙 (중요)

### 기본 원칙
- 주식 종목명이 언급되면 반드시 종목명 뒤에 `$심볼` 형태로 표기
- **반드시 미국 시장 기준의 표준 심볼만 사용**
- 거래소 접미사는 절대 사용하지 않음

### 금지 사항 ❌
- `$RELIANCE.NS` (인도 거래소 접미사)
- `$TSLA.BO` (봄베이 거래소 접미사)
- `$AAPL.L` (런던 거래소 접미사)
- `$MSFT.TO` (토론토 거래소 접미사)
- 기타 모든 거래소 접미사 (.NS, .BO, .L, .TO, .PA, .DE 등)

### 올바른 예시 ✅
- 테슬라 $TSLA
- 애플 $AAPL
- 마이크로소프트 $MSFT
- 구글 $GOOGL
- 아마존 $AMZN
- 엔비디아 $NVDA
- 메타 $META
- 블랙록 $BLK

### 인도 기업 처리 규칙
- 대표적인 미국 거래소 심볼 사용 (ADR 심볼보다 미국 거래소 심볼 우선)
  - 릴라이언스 인더스트리 → `$RELI` (미국 거래소 심볼)
  - 인포시스 → `$INFY` (ADR 심볼)
- 미국 거래소 심볼이 없는 경우: 확실하지 않으면 심볼 생략

### 심볼 표기 형식
- 괄호 사용 금지: `테슬라($TSLA)` ❌
- 공백으로 구분: `테슬라 $TSLA` ✅
- 심볼을 모르는 경우: 심볼 표기 생략

#### X(트위터) 콘텐츠 전용 공백 규칙
- **X 콘텐츠에만 적용**: $심볼 앞뒤로 반드시 한 칸의 공백 확보
- **올바른 예시**: `삼성전자 $005930.KS , 테슬라 $TSLA , 애플 $AAPL 등`
- **적용 범위**: X(트위터) 콘텐츠 생성 시에만 적용, 다른 콘텐츠 유형(블로그, Threads, 스탠다드 등)은 기존 규칙 유지

## 콘텐츠 구조 규칙

### 1. 제목 형식
- 형태: `이모지 제목내용`
- 예시: `💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시`
- 이모지는 정확히 1개만 사용
- 이모지와 제목 사이에 공백 하나만 사용

### 2. 섹션 구조
- 각 주요 섹션은 `▶`로 시작
- 섹션 제목은 명사형으로 끝남 (예: "현황:", "전망:", "영향:")
- 섹션 제목 뒤에는 반드시 콜론(`:`) 사용

### 3. 글머리 기호
- 주요 사실/현황: `•` 기호 사용
- 순차적 내용: `1. 2. 3.` 번호 사용
- 인용구나 발언: 따옴표(`" "`) 사용

### 4. 문체와 톤
- 객관적이고 명확한 문체
- 문장은 간결하게 (1-2줄 이내)
- 전문 용어는 가능한 한글로 설명
- 숫자나 통계는 단위와 함께 명확히 표기

## 제외해야 할 내용

### 완전 삭제 대상
- 기자 소개나 프로필 정보
- 기자 연락처나 이메일 정보
- 기자 경력이나 소속 언론사 소개
- 홍보성 메시지나 광고 문구
- 뉴스레터 구독 안내
- 소셜 미디어 팔로우 유도 문구
- 앱 다운로드나 서비스 가입 권유
- 상업적 홍보나 광고성 콘텐츠

## 이모지 선택 가이드

### 카테고리별 이모지
- **금융/투자**: 💰 💵 📈 📊
- **기술/혁신**: 🚀 💡 🔧 🌟
- **정책/규제**: ⚖️ 📜 🏛️ 🔨
- **갈등/경쟁**: 🔥 ⚔️ 🎯 🎲
- **협력/계약**: 🤝 📝 🎊 🌈
- **성장/발전**: 🌱 🎉 💪 ⭐

## 품질 체크리스트

### 주식 심볼 검증
- [ ] 모든 주식 심볼이 미국 시장 기준인가?
- [ ] 거래소 접미사가 제거되었는가?
- [ ] 심볼 표기가 `종목명 $심볼` 형태인가?

### 콘텐츠 구조 검증
- [ ] 제목에 이모지가 정확히 1개 있는가?
- [ ] 섹션 구조가 `▶ 제목:` 형태인가?
- [ ] 글머리 기호가 일관되게 사용되었는가?

### 내용 품질 검증
- [ ] 기자 정보가 모두 제거되었는가?
- [ ] 홍보성 내용이 제거되었는가?
- [ ] 문체가 객관적이고 명확한가?

## 블로그 콘텐츠 작성 가이드라인

### 기본 요구사항

#### 📏 분량 기준
- **최소 5000자 이상** (필수 조건)
- 5000자 미달 시 다음 방법으로 콘텐츠 보강:
  - 관련 배경정보 추가
  - 시장 분석 및 트렌드 설명
  - 전문가 의견 및 인용구
  - 유사 사례 및 과거 비교
  - 독자에게 도움이 되는 추가 정보

#### 🗣️ 말투 및 문체
- **친절하고 설득력있는 말투** (필수)
- **친근한 말투** 사용 - 독자와의 거리감 최소화
- 종결어미: "~에요", "~해요", "~죠" 등 친근한 표현 활용
- 대화하듯 편안한 어조로 작성
- 독자를 배려하는 따뜻하고 세심한 표현

### 콘텐츠 구성 가이드

#### 📝 구조적 요소
1. **매력적인 제목** - 클릭을 유도하는 흥미로운 제목
2. **한줄 요약** - 핵심 내용을 간단히 요약
3. **🎯 핵심 하이라이트** - 3-4개의 주요 포인트
4. **📖 배경 및 컨텍스트** - 독자 이해를 돕는 설명
5. **🔍 상세 분석** - 논리적이고 체계적인 분석
6. **📊 데이터 및 통계** - 신뢰할 수 있는 근거 제시
7. **💭 시장 반응 및 전망** - 다각도 분석과 전망
8. **💡 투자자 관점** - 실용적 인사이트 제공
9. **🔮 미래 전망** - 결론 및 예측

#### 🎨 시각적 요소 활용
- **📸 이미지 플레이스홀더**: 관련 이미지 위치 명시
- **📊 차트/그래프 제안**: 데이터 시각화 아이디어
- **📋 정보 박스**: 중요 정보를 별도 강조
- **🎯 아이콘 활용**: 각 섹션별 적절한 아이콘
- **💡 콜아웃 박스**: 핵심 메시지 강조

### 문체 및 톤 세부 가이드

#### ✅ 권장 표현
- "이런 점이 정말 흥미로워요"
- "함께 살펴볼까요?"
- "여러분도 궁금하셨을 텐데요"
- "이 부분은 특히 주목할 만해요"
- "생각보다 간단해요"
- "조금 더 자세히 알아볼게요"

#### ❌ 피해야 할 표현
- 과도하게 딱딱한 공식적 문체
- 너무 전문적이어서 어려운 용어 남발
- 감정이 배제된 기계적인 설명
- 독자를 배려하지 않는 일방적 서술

### 품질 체크리스트

#### 📊 분량 확인
- [ ] 5000자 이상인가?
- [ ] 5000자 미달 시 관련 정보로 보강했는가?
- [ ] 내용이 풍부하고 알찬가?

#### 🗣️ 말투 확인
- [ ] 친근하고 따뜻한 어조인가?
- [ ] 설득력있는 논리적 구성인가?
- [ ] 독자와의 거리감이 적절한가?
- [ ] 대화하듯 자연스러운 문체인가?

#### 📖 내용 품질
- [ ] 독자에게 도움이 되는 실용적 정보인가?
- [ ] 논리적이고 체계적으로 구성되었는가?
- [ ] 시각적 요소 제안이 적절한가?
- [ ] 전체적인 읽는 재미가 있는가?

#### 🏷️ 해시태그 (블로그 콘텐츠 전용)
- [ ] 글 마지막에 해시태그 5개가 포함되어 있는가?
- [ ] 해시태그가 글의 핵심 내용을 잘 표현하는가?
- [ ] 해시태그 형식이 올바른가? (#키워드1 #키워드2 #키워드3 #키워드4 #키워드5)
- [ ] "**태그:**" 제목이 해시태그 앞에 붙어있는가?

## 블로그 콘텐츠 해시태그 가이드라인

### 📋 기본 원칙
- 모든 블로그 콘텐츠는 마지막에 반드시 해시태그 5개를 포함해야 함
- 해시태그는 글의 핵심 주제를 명확하게 표현해야 함
- "**태그:**" 제목 뒤에 해시태그를 나열

### 🏷️ 해시태그 형식
```
**태그:** #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
```

### 📝 해시태그 선정 기준
- **핵심 주제**: 기사의 메인 테마 (예: #암호화폐, #인공지능, #전기차)
- **관련 기업**: 언급된 주요 기업명 (예: #테슬라, #애플, #구글)
- **산업 분야**: 해당 산업 또는 시장 (예: #핀테크, #바이오테크, #반도체)
- **지역/국가**: 관련 지역이나 국가 (예: #미국, #중국, #한국)
- **트렌드/이슈**: 현재 화제가 되는 키워드 (예: #ESG, #메타버스, #NFT)

### ✅ 좋은 예시
```
**태그:** #비트코인 #암호화폐거래소 #크라켄 #블록체인 #핀테크
```

### ❌ 나쁜 예시
```
- 해시태그 개수 부족: #비트코인 #크라켄 (2개만)
- 형식 오류: 태그: 비트코인, 크라켄, 암호화폐 (# 없음)
- 제목 누락: #비트코인 #크라켄 #암호화폐 #블록체인 #핀테크 ("**태그:**" 없음)
```

## X(트위터) 콘텐츠 작성 가이드라인

### 📱 X 콘텐츠 전용 문체 규칙

#### 🚨 X 콘텐츠 절대 규칙 - 반드시 준수
1. **본문에서 각 문장마다 불릿 포인트(•) 필수 사용** - 각 정보를 명확히 구분
2. **문장 마무리마다 줄바꿈 필수** - 가독성 향상을 위한 시각적 구분
3. **헤딩(##) 사용 절대 금지** - 평문으로만 작성
4. **"▶ 섹션명:" 형식 사용 금지** - 자연스러운 문장으로 연결
5. **모든 문장은 간결하고 핵심적으로** - 한 문장 최대 2줄
6. **전체 분량 280자 내외** (해시태그 포함)
7. **명사형 종결어미 필수** - "~음", "~슴", "~함", "~임" 등으로 마무리

#### 🎯 명사형 종결어미 사용 규칙 (X 콘텐츠 필수)
X(트위터) 콘텐츠는 간결성을 위해 모든 문장을 명사형 종결어미로 마무리:

#### ✅ 올바른 종결어미 예시
- **동작**: "발표함", "증가함", "감소함", "상승함", "하락함"
- **상태**: "예상됨", "분석됨", "파악됨", "확인됨", "보고됨"
- **진행**: "진행 중", "검토 중", "준비 중", "논의 중", "주목하는 중"
- **평가**: "주목받음", "평가받음", "기대됨", "우려됨"
- **가능성**: "가능함", "필요함", "중요함", "시급함", "전망임"

#### ❌ 금지되는 종결어미
- **서술형**: "~습니다", "~했다", "~한다", "~이다", "~된다"
- **의문형**: "~일까?", "~는가?", "~을까?"
- **명령형**: "~하세요", "~해라", "~하라"
- **청유형**: "~합시다", "~하자"

#### 📝 X 콘텐츠 올바른 구조
```
🔥 테슬라 주가 급등에 월가 주목

• 테슬라 $TSLA 주가가 실적 발표 후 12% 급등함
• 예상을 뛰어넘는 차량 인도량과 마진 개선이 주요 원인으로 분석됨
• 월가 애널리스트들이 자율주행 기술 진전과 에너지 사업 성장에 주목하는 중
• 골드만삭스는 목표주가를 300달러로 상향 조정함
• 전기차 시장 전반에 긍정적 영향을 미칠 것으로 예상됨
• 경쟁사들도 주가 상승세를 보이며 섹터 전체가 재평가받을 전망임

#테슬라 #전기차 #주식시장 #자율주행 #월가
```

#### ❌ 잘못된 X 콘텐츠 예시 (서술형 종결어미 사용)
```
🔥 파월 의장의 불확실한 운명에도 시장은 담담한 반응 

▶ 주요 내용:
• 제롬 파월 연준 의장의 재임 여부에 대한 불확실성이 높아지고 있음에도 불구하고, 금융시장은 비교적 차분한 모습을 보이고 있습니다. 
• 바이든 대통령이 파월 의장의 연임을 지지할 것이라는 기대감이 있었으나, 최근 들어 그 가능성이 낮아지고 있다는 관측이 나오고 있습니다.
• 하지만 시장은 파월 의장의 거취와 무관하게 연준의 통화정책 기조가 크게 변하지 않을 것이라는 믿음을 갖고 있는 듯합니다.
```

#### 🚫 문체 변환 예시
- ❌ "발표했습니다" → ✅ "발표함"
- ❌ "상승했다" → ✅ "상승함"  
- ❌ "예상된다" → ✅ "예상됨"
- ❌ "주목받고 있다" → ✅ "주목받는 중"
- ❌ "결정되었다" → ✅ "결정됨"
- ❌ "시작했습니다" → ✅ "시작함"
- ❌ "영향을 미칠 것이다" → ✅ "영향을 미칠 전망임"

#### 🚨 중요: 적용 범위
- **X 콘텐츠 생성에만 적용**: 이 말투는 X(트위터) 콘텐츠 생성 시에만 사용
- **다른 콘텐츠 유형 제외**: 블로그, 스레드, 스탠다드 등 다른 콘텐츠 유형은 기존 가이드라인 그대로 유지
- **일관성 유지**: X 콘텐츠 내에서는 일관되게 이 말투를 적용

#### 📋 X 콘텐츠 품질 체크리스트
- [ ] 본문의 각 문장이 불렛 포인트(•)로 시작하는가?
- [ ] 각 문장 마무리마다 줄바꿈이 되어있는가?
- [ ] 문장 마무리가 간결하고 정돈된 형태인가?
- [ ] "~전망", "~상황", "~우려도 제기됨" 등의 표현을 적절히 사용했는가?
- [ ] 다른 콘텐츠 유형과 구별되는 X 전용 말투인가?
- [ ] 전체적으로 간결하고 핵심적인 내용인가?
- [ ] **주식 심볼 공백 규칙**: $심볼 앞뒤로 한 칸의 공백이 확보되었는가? (예: 테슬라 $TSLA 등)

## 업데이트 이력
- 2024-01-XX: 초기 가이드라인 작성
- 2024-01-XX: 주식 심볼 처리 규칙 강화 (미국 시장 기준 명시, 거래소 접미사 금지)
- 2025-07-14: 블로그 콘텐츠 작성 가이드라인 추가 (5000자 이상, 친근한 말투 적용)
- 2025-07-15: 블로그 콘텐츠 해시태그 5개 필수 추가 가이드라인 적용
- 2025-07-16: X(트위터) 콘텐츠 전용 마무리 말투 가이드라인 추가 (간결하고 정돈된 표현)
- 2025-07-16: X(트위터) 콘텐츠 전용 주식 심볼 공백 규칙 추가 ($심볼 앞뒤로 한 칸 공백 확보)
- 2025-07-17: 완성형 블로그 SEO 최적화 가이드라인 추가 (워드프레스, 티스토리, 네이버 블로그 플랫폼별 상세 SEO 전략)
- 2025-07-17: 워드프레스 블로그 최적 분량 기준 상향 조정 (2000-4000자 → 4000-5000자)
- 2025-07-17: X(Twitter) 콘텐츠 가이드라인 강화 및 전용 생성 함수 추가 (불릿 포인트 및 헤딩 사용 금지, 간결한 문장 필수)
- 2025-07-17: X(Twitter) 콘텐츠 명사형 종결어미 필수 적용 (~음, ~슴, ~함, ~임 등으로 마무리)
- 2025-07-18: X(Twitter) 콘텐츠 형식 개선 (본문 각 문장에 불렛 포인트(•) 필수, 문장마다 줄바꿈 적용) 