#!/bin/bash
# Build FlashcardApp thành file .AppImage chạy được trên hầu hết bản Ubuntu/Linux,
# không cần cài Python/PyQt6 trên máy đích.
#
# Cách dùng:  bash build_appimage.sh
# Kết quả:    FlashcardApp-x86_64.AppImage (nằm ngay thư mục gốc dự án)

set -e
cd "$(dirname "$0")"

echo "==> 1) Dọn build cũ"
rm -rf build dist AppDir FlashcardApp-x86_64.AppImage
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "==> 2) Build bằng PyInstaller (dùng đúng FlashcardApp.spec — có kèm dữ liệu gốc)"
pyinstaller FlashcardApp.spec

echo "==> 3) Tạo cấu trúc AppDir"
mkdir -p AppDir/usr/bin
cp dist/FlashcardApp AppDir/usr/bin/FlashcardApp
cp app_icon.png AppDir/FlashcardApp.png

cat > AppDir/FlashcardApp.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=FlashcardApp
Exec=FlashcardApp
Icon=FlashcardApp
Categories=Education;
Terminal=false
EOF

cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/FlashcardApp" "$@"
EOF
chmod +x AppDir/AppRun

echo "==> 4) Tải appimagetool (nếu chưa có sẵn trong /tmp)"
APPIMAGETOOL=/tmp/appimagetool
if [ ! -f "$APPIMAGETOOL" ]; then
    wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -O "$APPIMAGETOOL" \
        || curl -sL "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage" -o "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

echo "==> 5) Đóng gói AppDir thành .AppImage"
# --appimage-extract-and-run: dùng khi máy không có FUSE (phổ biến trong máy
# ảo/container/WSL) — vẫn ra đúng kết quả, chỉ là appimagetool tự giải nén ra
# chạy tạm thay vì mount trực tiếp, không ảnh hưởng gì tới file .AppImage tạo ra.
"$APPIMAGETOOL" --appimage-extract-and-run AppDir FlashcardApp-x86_64.AppImage

echo ""
echo "==> XONG: FlashcardApp-x86_64.AppImage"
echo "    Copy file này sang máy Ubuntu/Linux khác, cấp quyền chạy rồi mở:"
echo "        chmod +x FlashcardApp-x86_64.AppImage"
echo "        ./FlashcardApp-x86_64.AppImage"
