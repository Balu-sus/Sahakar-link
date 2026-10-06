#!/bin/sh

echo "=================================================="
echo " Starting Sahakar-Link Platform Microservices... "
echo "=================================================="

# 1. API Gateway (Port 8000)
python3 services/api-gateway/main.py &

# 2. AI RAG Pipeline Service (Port 8002)
python3 ai-services/rag-pipeline/main.py &

# 3. IndicTrans2 Translation Service (Port 8003)
python3 ai-services/translation/main.py &

# 4. Local Fabric Sync Engine (Port 8004)
python3 services/sync-engine/main.py &

# 5. AdaFace Biometrics Service (Port 8005)
python3 ai-services/biometrics/main.py &

# 6. PaddleOCR Vision Service (Port 8006)
python3 ai-services/vision-ocr/main.py &

# 7. Skill Matcher Engine (Port 8007)
python3 ai-services/skill-matcher/main.py &

echo "All services initiated. Press Ctrl+C to stop."
wait
