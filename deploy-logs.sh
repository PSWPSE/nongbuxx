#!/bin/bash

# NONGBUXX 배포 로그 실시간 확인 스크립트

echo "📜 NONGBUXX 배포 로그 확인"
echo "========================"

cd frontend

echo "🔍 실시간 로그 확인 중... (Ctrl+C로 종료)"
vercel logs --follow

cd .. 