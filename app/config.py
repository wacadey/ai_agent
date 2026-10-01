'''
프로그램 전체 환경변수 로드, 관리
'''
import os
from dotenv import load_dotenv

# 환경변수 로드(.env)
load_dotenv() # 환경변수 설정 완료됨(os레벨)

# 변수로 사용
# .env -> load_dotenv() -> os단 환경변수 자동세팅
# os.getenv( 키값, 기본값(누락시사용) )
# 리전
AWS_REGION          = os.getenv('AWS_REGION', 'us-east-1')
# LLM 모델
BEDROCK_CHAT_MODEL  = os.getenv('BEDROCK_CHAT_MODEL', 'us.anthropic.claude-sonnet-5')
# 임베딩 모델, 토크나이저(api용 사용)
BEDROCK_EMBED_MODEL = os.getenv('BEDROCK_EMBED_MODEL', 'amazon.titan-embed-text-v2:0')
# 백터DB 주소
DATABASE_URL        = os.getenv('DATABASE_URL', 'postgresql://agent:agent@localhost:5432/agentlab')
# 메모리 기능을 위한 사용자 ID 구성
USER_ID             = os.getenv('USER_ID', 'de-ai-12')
