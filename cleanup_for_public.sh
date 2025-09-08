#!/bin/bash
# Repository cleanup script for public release

set -e

echo "🧹 Starting repository cleanup for public release..."

# Navigate to project root
cd /home/wirsam/intui/sensorapi

# 1. Remove log files
echo "📝 Removing log files..."
find . -name "*.log" -type f -delete
echo "   - Deleted *.log files"

# 2. Remove test databases
echo "🗄️ Removing test databases..."
rm -f test_sensor_api.db
echo "   - Deleted test database files"

# 3. Remove Python cache directories
echo "🐍 Cleaning Python cache..."
find . -name "__pycache__" -type d ! -path "*/.venv/*" ! -path "*/venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -type f ! -path "*/.venv/*" ! -path "*/venv/*" -delete
echo "   - Deleted __pycache__ directories and .pyc files"

# 4. Remove version marker files
echo "🏷️ Removing version marker files..."
rm -f =*
echo "   - Deleted version marker files (=*.*.* pattern)"

# 5. Move notebook to docs (if keeping it)
if [ -f "sensor_data_analysis.ipynb" ]; then
    echo "📊 Moving analysis notebook to docs..."
    mkdir -p docs/examples
    mv sensor_data_analysis.ipynb docs/examples/
    echo "   - Moved sensor_data_analysis.ipynb to docs/examples/"
fi

# 6. Clean up any other development artifacts
echo "🧽 Cleaning other artifacts..."
rm -f *.db.backup 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true

echo "✅ Cleanup complete!"
echo ""
echo "🔐 CRITICAL SECURITY REMINDERS:"
echo "1. Rotate ALL database credentials before going public"
echo "2. Generate new JWT secrets"
echo "3. Create .env.example with placeholder values"
echo "4. Remove .env from any commits (check git history)"
echo "5. Update production environment with new credentials"
echo ""
echo "Next steps:"
echo "- Review MAKE_PUBLIC_CHECKLIST.md"
echo "- Test application with new environment"
echo "- Run security audit"
echo "- Create LICENSE file"