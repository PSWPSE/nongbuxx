#!/bin/bash

echo "🧹 JWT 테스트 파일 정리 중..."

# JWT 테스트 파일들을 temp_jwt_tests 폴더로 이동
mkdir -p temp_jwt_tests

# 이동할 파일들
files_to_move=(
    "test_jwt_*.py"
    "jwt_*.py"
    "verify_jwt_*.py"
    "check_jwt_*.py"
    "fix_jwt_*.py"
    "debug_jwt_*.py"
    "detailed_jwt_*.py"
    "final_jwt_*.py"
    "wait_and_*.py"
    "test_backend_config.py"
    "test_auth.py"
    "verify_setup.py"
    "railway_env_check.py"
    "check_railway_*.py"
    "fix_all_jwt_*.py"
)

for pattern in "${files_to_move[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            mv "$file" temp_jwt_tests/
            echo "  ✓ $file 이동됨"
        fi
    done
done

echo "✅ 정리 완료! temp_jwt_tests 폴더로 이동되었습니다." 