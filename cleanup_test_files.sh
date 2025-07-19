#!/bin/bash

echo "🧹 JWT 테스트 파일 정리"
echo "다음 파일들을 삭제합니다:"
echo "- test_backend_config.py"
echo "- test_jwt_db_connection.py"  
echo "- verify_jwt_deployment.py"
echo "- wait_and_verify.sh"
echo "- check_jwt_fix.py"
echo "- railway_env_check.py"

read -p "계속하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    rm -f test_backend_config.py
    rm -f test_jwt_db_connection.py
    rm -f verify_jwt_deployment.py
    rm -f wait_and_verify.sh
    rm -f check_jwt_fix.py
    rm -f railway_env_check.py
    rm -f cleanup_test_files.sh
    
    echo "✅ 정리 완료!"
else
    echo "❌ 취소되었습니다."
fi 