#!/bin/bash

# Project Verification Script
# 项目验证脚本

set -e

echo "🔍 Deepfake Detection Platform - Project Verification"
echo "======================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1/ - MISSING"
        ((FAILED++))
    fi
}

echo "📁 Checking Project Structure..."
echo ""

# Root files
echo "Root Files:"
check_file "README.md"
check_file "README_CN.md"
check_file "docker-compose.yml"
check_file "start.sh"
check_file "stop.sh"
check_file "dev.sh"
check_file ".gitignore"
check_file "LICENSE"
echo ""

# Backend structure
echo "Backend Structure:"
check_dir "backend"
check_file "backend/Dockerfile"
check_file "backend/requirements.txt"
check_file "backend/alembic.ini"
check_file "backend/.env.example"
check_file "backend/app/main.py"
check_file "backend/app/api/auth.py"
check_file "backend/app/api/detection.py"
check_file "backend/app/api/admin.py"
check_file "backend/app/api/user.py"
check_file "backend/app/core/config.py"
check_file "backend/app/core/database.py"
check_file "backend/app/core/security.py"
check_file "backend/app/models/models.py"
check_file "backend/app/schemas/schemas.py"
check_file "backend/app/services/detection_service.py"
echo ""

# Frontend structure
echo "Frontend Structure:"
check_dir "frontend"
check_file "frontend/package.json"
check_file "frontend/vite.config.js"
check_file "frontend/index.html"
check_file "frontend/src/main.js"
check_file "frontend/src/App.vue"
check_file "frontend/src/api/axios.js"
check_file "frontend/src/api/index.js"
check_file "frontend/src/stores/auth.js"
check_file "frontend/src/router/index.js"
check_file "frontend/src/views/Login.vue"
check_file "frontend/src/views/Layout.vue"
check_file "frontend/src/views/user/Dashboard.vue"
check_file "frontend/src/views/user/Detection.vue"
check_file "frontend/src/views/user/Traceability.vue"
check_file "frontend/src/views/user/Profile.vue"
check_file "frontend/src/views/admin/AdminLayout.vue"
check_file "frontend/src/views/admin/Dashboard.vue"
check_file "frontend/src/views/admin/Users.vue"
check_file "frontend/src/views/admin/Audit.vue"
echo ""

# Documentation
echo "Documentation:"
check_file "docs/QUICKSTART.md"
check_file "docs/QUICKSTART_CN.md"
check_file "docs/MODEL_DEPLOY.md"
check_file "docs/DEPLOYMENT.md"
check_file "docs/API.md"
check_file "docs/PROJECT_STRUCTURE.md"
check_file "docs/PROJECT_STRUCTURE_CN.md"
check_file "PROJECT_SUMMARY.md"
check_file "PROJECT_SUMMARY_CN.md"
check_file "FINAL_REPORT_CN.md"
check_file "DELIVERY_CHECKLIST_CN.md"
check_file "使用指南.md"
echo ""

# Check executables
echo "Checking Script Permissions:"
if [ -x "start.sh" ]; then
    echo -e "${GREEN}✓${NC} start.sh is executable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} start.sh is not executable"
    ((FAILED++))
fi

if [ -x "stop.sh" ]; then
    echo -e "${GREEN}✓${NC} stop.sh is executable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} stop.sh is not executable"
    ((FAILED++))
fi

if [ -x "dev.sh" ]; then
    echo -e "${GREEN}✓${NC} dev.sh is executable"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} dev.sh is not executable"
    ((FAILED++))
fi
echo ""

# Summary
echo "======================================================"
echo "Verification Summary:"
echo "======================================================"
echo -e "Passed: ${GREEN}${PASSED}${NC}"
echo -e "Failed: ${RED}${FAILED}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Project is ready to deploy.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run: ./start.sh"
    echo "2. Access: http://localhost:5173"
    echo "3. Login: admin@example.com / admin123"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review the missing files.${NC}"
    exit 1
fi
