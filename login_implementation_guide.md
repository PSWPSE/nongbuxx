# 로그인 기능 구현 가이드 - Cursor AI용

## 프로젝트 개요
- **프론트엔드**: Next.js 14 + NextAuth.js (Vercel 배포)
- **백엔드**: PostgreSQL + Prisma (Railway 배포)
- **인증 방식**: NextAuth.js 중심 아키텍처

---

## 1단계: 프론트엔드 설정 (Vercel)

### 1.1 Next.js 프로젝트 생성 및 의존성 설치

```bash
# 프로젝트 생성
npx create-next-app@latest my-app --typescript --tailwind --eslint --app

# 인증 관련 패키지 설치
npm install next-auth@beta @auth/prisma-adapter prisma @prisma/client
npm install bcryptjs @types/bcryptjs
npm install zod react-hook-form @hookform/resolvers

# UI 라이브러리 (선택사항)
npm install @radix-ui/react-slot @radix-ui/react-label
npm install class-variance-authority clsx tailwind-merge
```

### 1.2 환경 변수 설정 (.env.local)

```env
# NextAuth.js 설정
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000

# 데이터베이스 (Railway에서 제공)
DATABASE_URL=postgresql://username:password@host:port/database

# 소셜 로그인 (Google)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# 소셜 로그인 (GitHub)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### 1.3 Prisma 스키마 설정 (prisma/schema.prisma)

```prisma
// Cursor AI에게 이 파일을 생성하도록 지시
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Account {
  id                String  @id @default(cuid())
  userId            String  @map("user_id")
  type              String
  provider          String
  providerAccountId String  @map("provider_account_id")
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique @map("session_token")
  userId       String   @map("user_id")
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime? @map("email_verified")
  image         String?
  password      String?
  createdAt     DateTime  @default(now()) @map("created_at")
  updatedAt     DateTime  @updatedAt @map("updated_at")
  accounts      Account[]
  sessions      Session[]

  @@map("users")
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@map("verificationtokens")
}
```

### 1.4 NextAuth.js 설정 (app/api/auth/[...nextauth]/route.ts)

```typescript
// Cursor AI에게 이 파일을 생성하도록 지시
import NextAuth from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"
import GoogleProvider from "next-auth/providers/google"
import GitHubProvider from "next-auth/providers/github"
import CredentialsProvider from "next-auth/providers/credentials"
import bcrypt from "bcryptjs"

const handler = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    CredentialsProvider({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) return null
        
        const user = await prisma.user.findUnique({
          where: { email: credentials.email }
        })
        
        if (!user || !user.password) return null
        
        const passwordMatch = await bcrypt.compare(
          credentials.password,
          user.password
        )
        
        if (!passwordMatch) return null
        
        return {
          id: user.id,
          email: user.email,
          name: user.name,
          image: user.image,
        }
      }
    })
  ],
  session: { strategy: "jwt" },
  pages: {
    signIn: '/auth/signin',
    signUp: '/auth/signup',
  },
  callbacks: {
    async session({ session, token }) {
      if (token.sub) {
        session.user.id = token.sub
      }
      return session
    },
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id
      }
      return token
    }
  }
})

export { handler as GET, handler as POST }
```

### 1.5 Prisma 클라이언트 설정 (lib/prisma.ts)

```typescript
// Cursor AI에게 이 파일을 생성하도록 지시
import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

export const prisma = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma
```

### 1.6 회원가입 API 라우트 (app/api/auth/signup/route.ts)

```typescript
// Cursor AI에게 이 파일을 생성하도록 지시
import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'
import bcrypt from 'bcryptjs'
import { z } from 'zod'

const signupSchema = z.object({
  name: z.string().min(2, "이름은 2자 이상이어야 합니다"),
  email: z.string().email("올바른 이메일 형식이 아닙니다"),
  password: z.string().min(8, "비밀번호는 8자 이상이어야 합니다")
})

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { name, email, password } = signupSchema.parse(body)

    // 이미 존재하는 사용자 확인
    const existingUser = await prisma.user.findUnique({
      where: { email }
    })

    if (existingUser) {
      return NextResponse.json(
        { error: "이미 존재하는 이메일입니다" },
        { status: 400 }
      )
    }

    // 비밀번호 해싱
    const hashedPassword = await bcrypt.hash(password, 12)

    // 사용자 생성
    const user = await prisma.user.create({
      data: {
        name,
        email,
        password: hashedPassword,
      },
    })

    return NextResponse.json(
      { message: "회원가입이 완료되었습니다", userId: user.id },
      { status: 201 }
    )
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: error.errors[0].message },
        { status: 400 }
      )
    }
    return NextResponse.json(
      { error: "서버 오류가 발생했습니다" },
      { status: 500 }
    )
  }
}
```

---

## 2단계: UI 컴포넌트 생성

### 2.1 로그인 페이지 (app/auth/signin/page.tsx)

```tsx
// Cursor AI에게 이 파일을 생성하도록 지시
'use client'

import { signIn, getSession } from 'next-auth/react'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function SignInPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      })

      if (result?.error) {
        setError('이메일 또는 비밀번호가 올바르지 않습니다')
      } else {
        router.push('/')
      }
    } catch (error) {
      setError('로그인 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-2xl font-bold text-center">로그인</h2>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              이메일
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              비밀번호
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <div className="space-y-4">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">또는</span>
            </div>
          </div>

          <button
            onClick={() => signIn('google')}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Google로 로그인
          </button>

          <button
            onClick={() => signIn('github')}
            className="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            GitHub로 로그인
          </button>
        </div>

        <div className="text-center">
          <Link href="/auth/signup" className="text-indigo-600 hover:text-indigo-500">
            계정이 없으신가요? 회원가입
          </Link>
        </div>
      </div>
    </div>
  )
}
```

### 2.2 회원가입 페이지 (app/auth/signup/page.tsx)

```tsx
// Cursor AI에게 이 파일을 생성하도록 지시
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function SignUpPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (formData.password !== formData.confirmPassword) {
      setError('비밀번호가 일치하지 않습니다')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
        }),
      })

      const data = await response.json()

      if (response.ok) {
        router.push('/auth/signin?message=회원가입이 완료되었습니다')
      } else {
        setError(data.error || '회원가입 중 오류가 발생했습니다')
      }
    } catch (error) {
      setError('서버 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="text-2xl font-bold text-center">회원가입</h2>
        </div>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700">
              이름
            </label>
            <input
              id="name"
              name="name"
              type="text"
              required
              value={formData.name}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              이메일
            </label>
            <input
              id="email"
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              비밀번호
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
              비밀번호 확인
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? '회원가입 중...' : '회원가입'}
          </button>
        </form>

        <div className="text-center">
          <Link href="/auth/signin" className="text-indigo-600 hover:text-indigo-500">
            이미 계정이 있으신가요? 로그인
          </Link>
        </div>
      </div>
    </div>
  )
}
```

### 2.3 세션 프로바이더 설정 (components/providers/session-provider.tsx)

```tsx
// Cursor AI에게 이 파일을 생성하도록 지시
'use client'

import { SessionProvider } from 'next-auth/react'

export default function Providers({
  children,
}: {
  children: React.ReactNode
}) {
  return <SessionProvider>{children}</SessionProvider>
}
```

### 2.4 레이아웃 업데이트 (app/layout.tsx)

```tsx
// Cursor AI에게 기존 layout.tsx에 SessionProvider를 추가하도록 지시
import Providers from '@/components/providers/session-provider'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
```

---

## 3단계: Railway 배포 설정

### 3.1 Railway 프로젝트 생성 및 PostgreSQL 추가

```bash
# Railway CLI 설치 (선택사항)
npm install -g @railway/cli

# 또는 Railway 웹 콘솔에서:
# 1. 새 프로젝트 생성
# 2. PostgreSQL 데이터베이스 추가
# 3. 환경 변수에서 DATABASE_URL 복사
```

### 3.2 데이터베이스 마이그레이션

```bash
# 로컬에서 먼저 테스트
npx prisma generate
npx prisma db push

# 프로덕션 환경에서 실행할 명령어
npx prisma migrate deploy
```

### 3.3 package.json 스크립트 추가

```json
{
  "scripts": {
    "build": "next build",
    "start": "next start",
    "postinstall": "prisma generate",
    "db:migrate": "prisma migrate deploy",
    "db:seed": "prisma db seed"
  }
}
```

---

## 4단계: Vercel 배포 설정

### 4.1 Vercel 환경 변수 설정

```bash
# Vercel CLI 설치
npm install -g vercel

# 또는 Vercel 웹 콘솔에서 환경 변수 설정:
# NEXTAUTH_SECRET
# NEXTAUTH_URL
# DATABASE_URL
# GOOGLE_CLIENT_ID
# GOOGLE_CLIENT_SECRET
# GITHUB_CLIENT_ID
# GITHUB_CLIENT_SECRET
```

### 4.2 vercel.json 설정 (선택사항)

```json
{
  "functions": {
    "app/api/auth/[...nextauth]/route.ts": {
      "maxDuration": 30
    }
  }
}
```

---

## 5단계: 보안 강화 (추가 설정)

### 5.1 미들웨어 설정 (middleware.ts)

```typescript
// Cursor AI에게 이 파일을 생성하도록 지시
import { withAuth } from "next-auth/middleware"

export default withAuth(
  function middleware(req) {
    // 추가 미들웨어 로직
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token
    },
  }
)

export const config = {
  matcher: ["/dashboard/:path*", "/profile/:path*", "/admin/:path*"]
}
```

### 5.2 Rate Limiting 설정

```bash
# 패키지 설치
npm install @upstash/ratelimit @upstash/redis
```

---

## 6단계: 테스트 및 검증

### 6.1 체크리스트

- [ ] 로컬 환경에서 회원가입 테스트
- [ ] 로컬 환경에서 로그인 테스트
- [ ] 소셜 로그인 (Google, GitHub) 테스트
- [ ] 세션 유지 확인
- [ ] 로그아웃 기능 테스트
- [ ] 보호된 라우트 접근 테스트
- [ ] 데이터베이스 연결 확인
- [ ] 환경 변수 설정 확인

### 6.2 배포 체크리스트

- [ ] Railway PostgreSQL 설정 완료
- [ ] Vercel 환경 변수 설정 완료
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 프로덕션 환경 테스트 완료
- [ ] HTTPS 설정 확인
- [ ] 도메인 연결 완료

---

## Cursor AI 지시사항

1. **프로젝트 초기 설정**: "위의 1.1 단계 명령어들을 실행하여 Next.js 프로젝트를 설정하고 필요한 패키지를 설치해주세요."

2. **환경 변수 설정**: "1.2 단계의 .env.local 파일을 생성하고 환경 변수를 설정해주세요."

3. **데이터베이스 스키마**: "1.3 단계의 Prisma 스키마를 prisma/schema.prisma 파일에 생성해주세요."

4. **NextAuth 설정**: "1.4 단계의 NextAuth 설정을 app/api/auth/[...nextauth]/route.ts 파일에 생성해주세요."

5. **나머지 파일들**: "순서대로 각 단계의 파일들을 생성하고 설정해주세요."

6. **데이터베이스 연결**: "npx prisma generate && npx prisma db push 명령어를 실행해주세요."

7. **테스트 실행**: "npm run dev로 개발 서버를 실행하고 localhost:3000에서 테스트해주세요."

이 가이드를 따라하면 안전하고 현대적인 로그인 시스템을 구축할 수 있습니다.