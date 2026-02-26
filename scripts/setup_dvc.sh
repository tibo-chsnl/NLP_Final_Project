#!/bin/bash
# ============================================================
# DVC Remote Setup Script
# ============================================================
# Each team member runs this ONCE after cloning the repository.
#
# PREREQUISITES:
# 1. Open this OneDrive shared folder link in your browser:
#    https://efrei365net-my.sharepoint.com/:f:/g/personal/thibault_chesnel_efrei_net/IgDUIyJaL3Z9Q6Q4r8ch2WG-Ada88vuYFq3tm_xLQe-949Q?e=cYMPZa
#
# 2. Click "Add shortcut to My files" (Ajouter un raccourci à Mes fichiers)
#    This will sync the folder locally via OneDrive.
#
# 3. Find the local sync path on your machine. Examples:
#    macOS:  /Users/<you>/Library/CloudStorage/OneDrive-Efrei/dvc-storage
#    Windows: C:\Users\<you>\OneDrive - Efrei\dvc-storage
#    Linux:  ~/OneDrive/dvc-storage
#
# 4. Run this script with your local path as argument:
#    ./scripts/setup_dvc.sh /path/to/your/synced/dvc-storage
# ============================================================

set -e

if [ -z "$1" ]; then
    echo "❌ Usage: ./scripts/setup_dvc.sh <path-to-local-onedrive-dvc-storage>"
    echo ""
    echo "Example (macOS):"
    echo "  ./scripts/setup_dvc.sh /Users/\$(whoami)/Library/CloudStorage/OneDrive-Efrei/M2/S9/NLP/dvc-storage"
    echo ""
    echo "📖 See the comments at the top of this script for full instructions."
    exit 1
fi

DVC_PATH="$1"

# Verify the path exists
if [ ! -d "$DVC_PATH" ]; then
    echo "⚠️  Directory '$DVC_PATH' does not exist."
    read -p "Create it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$DVC_PATH"
        echo "✅ Created $DVC_PATH"
    else
        echo "❌ Aborted. Please create the directory or check the path."
        exit 1
    fi
fi

# Configure DVC remote locally (config.local is gitignored by DVC)
uv run dvc remote add --local -f shared "$DVC_PATH"

echo ""
echo "✅ DVC remote configured successfully!"
echo "   Remote: shared"
echo "   Path:   $DVC_PATH"
echo ""
echo "You can now run:"
echo "   uv run dvc pull    # Download data"
echo "   uv run dvc push    # Upload data"
