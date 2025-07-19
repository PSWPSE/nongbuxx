#!/usr/bin/env python3
"""모든 JWT identity 관련 코드 수정"""

import re

# user_routes.py에서 모든 get_jwt_identity() 다음에 오는 User.query.get() 수정
files_to_fix = [
    ('user_routes.py', [
        ('user = User.query.get(current_user_id)', 'user = User.query.get(int(current_user_id))'),
        ('user = User.query.filter_by(id=current_user_id)', 'user = User.query.filter_by(id=int(current_user_id))'),
    ]),
    ('auth_routes.py', [
        ('user = User.query.get(current_user_id)', 'user = User.query.get(int(current_user_id))'),
    ]),
    ('auth_middleware.py', [
        ('user = User.query.get(current_user_id)', 'user = User.query.get(int(current_user_id))'),
    ])
]

print("🔧 JWT identity 타입 수정 중...")
print("=" * 60)

for filename, replacements in files_to_fix:
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        original_content = content
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ {filename}: {old} → {new}")
        
        if content != original_content:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"✅ {filename} 수정 완료")
    except Exception as e:
        print(f"❌ {filename} 에러: {e}")

print("\n" + "=" * 60)
print("✅ 모든 수정 완료!") 