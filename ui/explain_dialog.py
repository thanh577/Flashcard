
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QScrollArea, QWidget,
                             QTabWidget)
from PyQt6.QtCore import Qt
from core.ai_lookup import AILookupWorker, load_cache, save_cache

CMDS = {
    "ls": {
        "desc": "Liệt kê file và thư mục",
        "flags": {
            "-l": "Định dạng dài (permissions, size, date)",
            "-a": "Hiển thị tất cả (kể cả file ẩn .xxx)",
            "-la": "Kết hợp -l và -a",
            "-lh": "Dung lượng dễ đọc (KB, MB, GB)",
            "-lt": "Sắp xếp theo thời gian sửa đổi",
            "-lS": "Sắp xếp theo kích thước (lớn nhất trước)",
            "-r": "Đảo ngược thứ tự sắp xếp",
            "-R": "Đệ quy (liệt kê cả thư mục con)",
            "-1": "Mỗi file trên một dòng",
            "-d": "Chỉ hiển thị thư mục, không vào bên trong",
            "-i": "Hiển thị inode number",
        },
        "examples": [
            ("ls -la", "Liệt kê tất cả file + chi tiết",
             "drwxr-xr-x  5 user  group   4096 Jul 22 10:00 .\n"
             "-rw-r--r--  1 user  group    123 Jul 21 09:00 file.txt\n"
             "drwx------  2 user  group   4096 Jul 20 08:00 .ssh"),
            ("ls -lh *.py", "File .py với dung lượng dễ đọc",
             "-rw-r--r--  1 user  group  2.3K Jul 22 10:00 main.py\n"
             "-rw-r--r--  1 user  group  1.1K Jul 21 09:00 utils.py"),
            ("ls -lt", "Sắp xếp theo thời gian (mới nhất đầu)",
             "-rw-r--r--  1 user  group  123 Jul 22 14:00 newest.py\n"
             "-rw-r--r--  1 user  group  456 Jul 21 10:00 older.py"),
        ],
    },
    "grep": {
        "desc": "Tìm kiếm văn bản theo pattern (global regex print)",
        "flags": {
            "-r": "Đệ quy — tìm trong tất cả thư mục con",
            "-i": "Không phân biệt chữ hoa/thường",
            "-n": "Hiển thị số dòng",
            "-v": "Đảo ngược — hiển thị dòng KHÔNG khớp",
            "-c": "Đếm số dòng khớp, không in nội dung",
            "-l": "Chỉ hiển thị tên file có kết quả",
            "-w": "Tìm nguyên từ (whole word)",
            "-E": "Sử dụng extended regex (egrep)",
            "-o": "Chỉ in phần khớp, không in cả dòng",
            "-A1": "In thêm 1 dòng sau kết quả (after context)",
            "-B1": "In thêm 1 dòng trước kết quả (before context)",
            "-C1": "In thêm 1 dòng cả trước và sau (context)",
            "-e": "Pattern bắt đầu bằng - (vd: grep -e '--pattern')",
            "-H": "Luôn hiển thị tên file (mặc định khi nhiều file)",
            "-h": "Không hiển thị tên file",
            "-m 5": "Chỉ lấy tối đa 5 kết quả",
            "--color": "Tô màu kết quả khớp",
        },
        "examples": [
            ("grep 'error' log.txt", "Tìm 'error' trong file log",
             "2024-01-01 10:00 error: connection refused\n"
             "2024-01-01 10:01 error: timeout after 30s"),
            ("grep -r -n 'TODO' src/", "Tìm TODO đệ quy, hiển thị số dòng",
             "src/main.py:42:    # TODO: add error handling\n"
             "src/utils.py:15:    # TODO: optimize this loop"),
            ("grep -c '^$' file.txt", "Đếm số dòng trống trong file",
             "42"),
        ],
    },
    "find": {
        "desc": "Tìm file trong cây thư mục",
        "flags": {
            "-name": "Tìm theo tên (vd: '*.txt')",
            "-iname": "Tìm theo tên KHÔNG phân biệt hoa/thường",
            "-type f": "Chỉ tìm file thường",
            "-type d": "Chỉ tìm thư mục",
            "-size +10M": "File lớn hơn 10MB",
            "-size -1k": "File nhỏ hơn 1KB",
            "-mtime -7": "File sửa đổi trong 7 ngày qua",
            "-mtime +30": "File sửa đổi hơn 30 ngày trước",
            "-maxdepth 2": "Giới hạn độ sâu tìm (2 cấp)",
            "-exec cmd {} +": "Thực thi lệnh trên kết quả tìm được",
            "-delete": "Xóa các file tìm được",
            "-empty": "Tìm file rỗng",
            "-perm 644": "Tìm theo quyền truy cập",
            "-user": "Tìm file của user cụ thể",
        },
        "examples": [
            ("find /var/log -name '*.log' -mtime -1",
             "File .log sửa đổi trong 24h qua",
             "/var/log/syslog\n/var/log/auth.log"),
            ("find . -type f -size +100M",
             "File lớn hơn 100MB",
             "./backup/database.sql\n./videos/demo.mp4"),
            ("find . -name '*.tmp' -delete",
             "Xóa tất cả file .tmp (cẩn thận!)",
             "(không output — xóa thành công)"),
        ],
    },
    "cp": {
        "desc": "Sao chép file hoặc thư mục",
        "flags": {
            "-r": "Sao chép cả thư mục con (recursive)",
            "-i": "Hỏi trước khi ghi đè",
            "-u": "Chỉ sao chép khi nguồn mới hơn đích",
            "-v": "Hiển thị chi tiết từng file (verbose)",
            "-p": "Giữ nguyên quyền, chủ sở hữu, thời gian",
            "-a": "Chế độ archive — giữ nguyên tất cả thuộc tính",
            "-n": "Không ghi đè file đã tồn tại",
            "-l": "Tạo hardlink thay vì copy",
            "-s": "Tạo symlink thay vì copy",
        },
        "examples": [
            ("cp file.txt backup/", "Copy file vào thư mục",
             "(thành công — không output)"),
            ("cp -r data/ data_backup/", "Copy cả thư mục",
             "(thành công — tất cả file trong data/ được copy)"),
            ("cp -v *.txt /tmp/", "Copy có verbose",
             "file1.txt -> /tmp/file1.txt\nfile2.txt -> /tmp/file2.txt"),
        ],
    },
    "mv": {
        "desc": "Di chuyển hoặc đổi tên file",
        "flags": {
            "-i": "Hỏi trước khi ghi đè",
            "-u": "Chỉ di chuyển khi nguồn mới hơn đích",
            "-v": "Hiển thị chi tiết",
            "-n": "Không ghi đè file đã tồn tại",
        },
        "examples": [
            ("mv old.txt new.txt", "Đổi tên file",
             "(thành công)"),
            ("mv file.txt /tmp/", "Di chuyển file",
             "(thành công)"),
            ("mv -i *.txt /target/", "Di chuyển, hỏi trước ghi đè",
             "overwrite /target/file.txt? (y/n)"),
        ],
    },
    "rm": {
        "desc": "Xóa file hoặc thư mục",
        "flags": {
            "-r": "Xóa cả thư mục con (recursive)",
            "-f": "Buộc xóa — không hỏi, không báo lỗi",
            "-rf": "Kết hợp -r và -f (cẩn thận!)",
            "-i": "Hỏi trước khi xóa từng file",
            "-v": "Hiển thị file đang xóa",
        },
        "examples": [
            ("rm file.txt", "Xóa 1 file",
             "(không output — xóa thành công)"),
            ("rm -rf /tmp/cache/", "Xóa thư mục cache",
             "(không output — tất cả bị xóa)"),
            ("rm -i *.log", "Xóa từng file có hỏi",
             "remove access.log? (y/n) y\nremove error.log? (y/n) n"),
        ],
    },
    "mkdir": {
        "desc": "Tạo thư mục mới",
        "flags": {
            "-p": "Tạo thư mục cha nếu chưa tồn tại",
            "-v": "Hiển thị thư mục đang tạo",
            "-m": "Đặt quyền cho thư mục (vd: mkdir -m 755 dir)",
        },
        "examples": [
            ("mkdir newdir", "Tạo thư mục",
             "(thành công)"),
            ("mkdir -p a/b/c/d", "Tạo cây thư mục lồng nhau",
             "(tạo a/, a/b/, a/b/c/, a/b/c/d/ cùng lúc)"),
            ("mkdir -v dir1 dir2 dir3", "Tạo nhiều thư mục",
             "mkdir: created directory 'dir1'\n"
             "mkdir: created directory 'dir2'\n"
             "mkdir: created directory 'dir3'"),
        ],
    },
    "cat": {
        "desc": "Xem nội dung file (concatenate)",
        "flags": {
            "-n": "Hiển thị số dòng",
            "-b": "Đánh số dòng (bỏ qua dòng trống)",
            "-s": "Nén nhiều dòng trống thành 1",
            "-E": "Hiển thị $ ở cuối mỗi dòng",
            "-T": "Hiển thị tab thành ^I",
            "-A": "Hiển thị tất cả ký tự đặc biệt",
        },
        "examples": [
            ("cat file.txt", "Xem nội dung file",
             "Hello World\nThis is line 2\nLine 3"),
            ("cat -n file.txt", "Xem + số dòng",
             "     1\tHello World\n     2\tThis is line 2\n     3\tLine 3"),
            ("cat file1.txt file2.txt > combined.txt",
             "Gộp nhiều file thành 1",
             "(tạo combined.txt chứa nội dung cả 2 file)"),
        ],
    },
    "less": {
        "desc": "Xem file từng trang (pager) — phím Space/PgUp/PgDn, q=thoát",
        "flags": {
            "-N": "Hiển thị số dòng",
            "-S": "Không xuống dòng (cuộn ngang)",
            "-i": "Tìm kiếm không phân biệt hoa/thường",
            "-F": "Thoát nếu file ngắn hơn 1 màn hình",
            "+F": "Theo dõi cuối file (giống tail -f), Ctrl+C để dừng",
        },
        "examples": [
            ("less /var/log/syslog", "Xem log file từng trang",
             "(mở trình pager — dùng Space để cuộn, q để thoát)"),
            ("less -N file.txt", "Xem với số dòng",
             "(hiển thị số dòng bên trái)"),
            ("less +F /var/log/syslog", "Theo dõi log realtime",
             "(tự động cuộn khi có log mới — Ctrl+C để dừng)"),
        ],
    },
    "head": {
        "desc": "Xem 10 dòng đầu file",
        "flags": {
            "-n 20": "Xem 20 dòng đầu (thay vì 10)",
            "-c 100": "Xem 100 byte đầu",
            "-q": "Không hiển thị tên file (khi nhiều file)",
        },
        "examples": [
            ("head file.txt", "Xem 10 dòng đầu",
             "Line 1\nLine 2\n...\nLine 10"),
            ("head -n 5 file.txt", "Xem 5 dòng đầu",
             "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"),
        ],
    },
    "tail": {
        "desc": "Xem 10 dòng cuối file",
        "flags": {
            "-n 20": "Xem 20 dòng cuối",
            "-f": "Theo dõi file → hiển thị khi file được ghi thêm",
            "-F": "Giống -f nhưng theo dõi cả khi file bị xoá/tạo lại",
            "-c 100": "Xem 100 byte cuối",
        },
        "examples": [
            ("tail file.txt", "Xem 10 dòng cuối",
             "...\nLine 95\n...\nLine 100"),
            ("tail -f /var/log/syslog", "Theo dõi log (Ctrl+C để thoát)",
             "Jul 22 14:00:01 host systemd[1]: Started..."),
            ("tail -n 2 file.txt", "Xem 2 dòng cuối",
             "Line 99\nLine 100"),
        ],
    },
    "echo": {
        "desc": "In chuỗi văn bản ra màn hình, thường dùng để hiển thị thông báo hoặc ghi vào file",
        "flags": {
            "-n": "Không xuống dòng ở cuối",
            "-e": "Bật diễn giải ký tự đặc biệt (\\n, \\t...)",
            "-E": "Tắt diễn giải ký tự đặc biệt (mặc định)",
        },
        "examples": [
            ("echo \"Xin chào\"", "In ra dòng chữ",
             "Xin chào"),
            ("echo -n \"Không xuống dòng\"", "Không có dấu xuống dòng ở cuối",
             "Không xuống dòng$ "),
            ("echo -e \"Dòng 1\\nDòng 2\"", "Diễn giải \\n thành xuống dòng thật",
             "Dòng 1\nDòng 2"),
            ("echo \"nội dung\" > file.txt", "Ghi đè nội dung vào file",
             "(tạo/ghi đè file.txt chứa 'nội dung')"),
            ("echo \"thêm dòng\" >> file.txt", "Nối thêm vào cuối file",
             "(giữ nguyên nội dung cũ, thêm dòng mới vào cuối)"),
        ],
    },
    "chmod": {
        "desc": "Thay đổi quyền truy cập file (change mode)",
        "flags": {
            "755": "rwxr-xr-x — thường dùng cho thư mục",
            "644": "rw-r--r-- — thường dùng cho file",
            "600": "rw------- — chỉ chủ sở hữu đọc/ghi",
            "777": "rwxrwxrwx — ai cũng làm được (không khuyến khích)",
            "+x": "Thêm quyền thực thi",
            "-x": "Bỏ quyền thực thi",
            "-R": "Áp dụng đệ quy cho thư mục con",
        },
        "examples": [
            ("chmod +x script.sh", "Thêm quyền chạy",
             "(file script.sh giờ có thể chạy: ./script.sh)"),
            ("chmod 755 folder/", "Thư mục: rwx cho chủ, rx cho nhóm/khác",
             "(thành công)"),
            ("chmod -R 644 public/", "Tất cả file trong public/ thành rw-r--r--",
             "(thành công — áp dụng cho toàn bộ cây thư mục)"),
            ("chmod 600 ~/.ssh/id_rsa", "File key SSH: chỉ chủ đọc/ghi",
             "(bảo mật — không ai khác đọc được private key)"),
        ],
    },
    "chown": {
        "desc": "Thay đổi chủ sở hữu file (change owner)",
        "flags": {
            "-R": "Áp dụng đệ quy cho thư mục con",
            "user:group": "Đổi cả user và group cùng lúc",
        },
        "examples": [
            ("sudo chown user file.txt", "Đổi chủ sở hữu",
             "(thành công — user mới là chủ)"),
            ("sudo chown -R www-data:www-data /var/www/",
             "Đổi user+group cho web folder",
             "(thành công — apache/nginx có quyền truy cập)"),
        ],
    },
    "tar": {
        "desc": "Nén/giải nén file tar (tape archive)",
        "flags": {
            "-c": "Tạo file nén mới (create)",
            "-x": "Giải nén (extract)",
            "-z": "Nén bằng gzip (.tar.gz)",
            "-j": "Nén bằng bzip2 (.tar.bz2)",
            "-v": "Hiển thị file đang xử lý",
            "-f": "Chỉ định tên file nén",
            "-t": "Xem nội dung file nén",
            "--exclude": "Loại trừ file/thư mục khi nén",
        },
        "examples": [
            ("tar -czvf archive.tar.gz /path/to/folder",
             "Nén thư mục thành .tar.gz",
             "folder/file1\nfolder/file2\nfolder/subfolder/file3"),
            ("tar -xzvf archive.tar.gz",
             "Giải nén .tar.gz ra thư mục hiện tại",
             "folder/file1\nfolder/file2\nfolder/subfolder/file3"),
            ("tar -tf archive.tar.gz",
             "Xem nội dung file nén (không giải nén)",
             "folder/file1\nfolder/file2"),
        ],
    },
    "gzip": {
        "desc": "Nén file .gz",
        "flags": {
            "-d": "Giải nén (decompress)",
            "-k": "Giữ file gốc (không xóa)",
            "-v": "Hiển thị tỉ lệ nén",
            "-r": "Nén đệ quy thư mục",
            "-1": "Nén nhanh (tốc độ cao, kích thước lớn)",
            "-9": "Nén tối đa (chậm nhất, nhỏ nhất)",
        },
        "examples": [
            ("gzip file.txt", "Nén file",
             "(tạo file.txt.gz, xóa file.txt)"),
            ("gzip -dk file.txt.gz", "Giải nén + giữ file gốc",
             "(tạo file.txt, giữ lại file.txt.gz)"),
        ],
    },
    "ssh": {
        "desc": "Kết nối SSH từ xa (secure shell)",
        "flags": {
            "-p 2222": "Cổng kết nối khác 22",
            "-i key.pem": "Dùng private key cụ thể",
            "-v": "Debug mode (verbose)",
            "-vvv": "Debug chi tiết (tìm lỗi kết nối)",
            "-X": "Chuyển tiếp X11 (GUI)",
            "-N": "Không thực thi lệnh — chỉ forward port",
            "-L 8080:localhost:80": "Forward cổng local",
            "-J jump_user@jump_host": "Kết nối qua jump host (proxy jump)",
        },
        "examples": [
            ("ssh user@192.168.1.100", "Kết nối cơ bản",
             "Welcome to Ubuntu 22.04 LTS\n...\nuser@server:~$"),
            ("ssh -p 2222 -i key.pem ubuntu@ec2-...",
             "Kết nối với key và cổng khác",
             "Welcome to Amazon Linux 2\n..."),
            ("ssh -vvv user@host", "Debug kết nối",
             "(output chi tiết: từng bước xác thực, từng gói tin)"),
        ],
    },
    "scp": {
        "desc": "Sao chép file qua SSH",
        "flags": {
            "-P 2222": "Cổng SSH (viết hoa P)",
            "-r": "Sao chép cả thư mục",
            "-C": "Nén dữ liệu khi truyền",
            "-i key.pem": "Dùng private key",
            "-q": "Im lặng — không hiển thị tiến trình",
        },
        "examples": [
            ("scp file.txt user@host:/tmp/", "Copy file lên server",
             "file.txt           100%  123KB  123KB/s   00:01"),
            ("scp -r user@host:/remote/ ./local/",
             "Copy cả thư mục từ server về",
             "remote/file1  100%  456KB  456KB/s\nremote/file2  100%  78KB ..."),
        ],
    },
    "rsync": {
        "desc": "Đồng bộ file (chỉ truyền phần khác biệt)",
        "flags": {
            "-a": "Archive mode — giữ nguyên thuộc tính",
            "-v": "Hiển thị chi tiết",
            "-z": "Nén khi truyền (tiết kiệm băng thông)",
            "-r": "Đệ quy — đồng bộ thư mục con",
            "-P": "Kết hợp --progress + --partial (tiếp tục nếu ngắt)",
            "--delete": "Xóa file ở đích nếu không còn ở nguồn",
            "--exclude": "Loại trừ file/thư mục",
            "--dry-run": "Chạy thử — xem sẽ làm gì, không thực sự chạy",
        },
        "examples": [
            ("rsync -av source/ dest/", "Đồng bộ local",
             "sending incremental file list\n./\nfile1.txt\nfile2.txt"),
            ("rsync -avz source/ user@host:dest/",
             "Đồng bộ qua SSH có nén",
             "sending incremental file list\n./\nfile1.txt"),
            ("rsync --delete -av source/ dest/",
             "Đồng bộ + xóa file thừa ở đích",
             "deleting old_file.txt\n./\nfile1.txt"),
        ],
    },
    "ps": {
        "desc": "Xem tiến trình đang chạy (process status)",
        "flags": {
            "aux": "Tất cả tiến trình của tất cả user (BSD style)",
            "-ef": "Tất cả tiến trình (standard style)",
            "-u user": "Tiến trình của user cụ thể",
            "-e": "Tất cả tiến trình",
            "-f": "Định dạng đầy đủ",
            "--sort=-%mem": "Sắp xếp theo memory (cao nhất trước)",
            "--sort=-%cpu": "Sắp xếp theo CPU (cao nhất trước)",
            "-eo pid,cmd,%mem,%cpu": "Chỉ hiển thị cột chọn lọc",
        },
        "examples": [
            ("ps aux", "Tất cả tiến trình",
             "USER   PID  %CPU  %MEM  COMMAND\n"
             "root     1   0.0   0.5  /sbin/init\n"
             "user  1234   2.3   1.2  /usr/bin/python3 app.py"),
            ("ps aux --sort=-%mem | head -5",
             "Top 5 tiến trình dùng nhiều RAM nhất",
             "USER   PID  %CPU  %MEM  COMMAND\n"
             "user  5678  10.2  25.3  /usr/bin/firefox\n"
             "user  1234   2.3   1.2  /usr/bin/python3"),
        ],
    },
    "kill": {
        "desc": "Gửi tín hiệu đến tiến trình (kết thúc, tạm dừng...)",
        "flags": {
            "-9": "SIGKILL — bắt buộc kết thúc ngay (không cleanup)",
            "-15": "SIGTERM — yêu cầu kết thúc an toàn (mặc định)",
            "-2": "SIGINT — giống Ctrl+C",
            "-1": "SIGHUP — reload cấu hình (áp dụng cho daemon)",
            "-3": "SIGQUIT — kết thúc + dump core (debug)",
            "-STOP": "Tạm dừng tiến trình",
            "-CONT": "Tiếp tục tiến trình đã tạm dừng",
        },
        "examples": [
            ("kill 1234", "Kết thúc tiến trình PID 1234 (SIGTERM)",
             "(thành công — tiến trình tự cleanup và thoát)"),
            ("kill -9 1234", "Bắt buộc kết thúc (SIGKILL)",
             "(tiến trình bị giết ngay lập tức, không cleanup)"),
            ("kill -HUP 1", "Reload init (SIGHUP)",
             "(systemd reload cấu hình — không dừng service)"),
        ],
    },
    "ping": {
        "desc": "Kiểm tra kết nối mạng đến host",
        "flags": {
            "-c 5": "Gửi 5 gói tin rồi dừng",
            "-i 2": "Gửi mỗi 2 giây (mặc định 1s)",
            "-s 100": "Kích thước gói tin 100 byte (mặc định 56)",
            "-t 10": "TTL = 10 (giới hạn số hop)",
            "-4": "Chỉ dùng IPv4",
            "-6": "Chỉ dùng IPv6",
        },
        "examples": [
            ("ping -c 4 google.com", "Ping 4 lần",
             "PING google.com (142.250.80.46) 56(84) bytes of data.\n"
             "64 bytes from ...: icmp_seq=1 ttl=115 time=12.3 ms\n"
             "64 bytes from ...: icmp_seq=2 ttl=115 time=11.8 ms\n"
             "64 bytes from ...: icmp_seq=3 ttl=115 time=13.1 ms\n"
             "64 bytes from ...: icmp_seq=4 ttl=115 time=12.0 ms\n"
             "--- google.com ping statistics ---\n"
             "4 packets transmitted, 4 received, 0% packet loss"),
        ],
    },
    "df": {
        "desc": "Báo cáo dung lượng ổ đĩa (disk free)",
        "flags": {
            "-h": "Dung lượng dễ đọc (G, M, K)",
            "-T": "Hiển thị loại filesystem",
            "-i": "Hiển thị inode (thay vì block)",
            "--total": "Hiển thị tổng cộng",
        },
        "examples": [
            ("df -h", "Dung lượng dễ đọc",
             "Filesystem      Size  Used Avail Use% Mounted on\n"
             "/dev/sda1       236G  120G  105G  54% /\n"
             "tmpfs            16G  2.3G   14G  15% /dev/shm"),
        ],
    },
    "du": {
        "desc": "Xem dung lượng thư mục/file (disk usage)",
        "flags": {
            "-h": "Dung lượng dễ đọc",
            "-s": "Chỉ hiển thị tổng (summary)",
            "-c": "Hiển thị tổng cộng",
            "--max-depth=1": "Giới hạn độ sâu hiển thị",
        },
        "examples": [
            ("du -sh *", "Dung lượng từng thư mục con",
             "12M\tDocuments\n4.2G\tVideos\n234M\tMusic\n856K\tNotes.txt"),
            ("du -h --max-depth=1 /home/user",
             "Cây thư mục con cấp 1",
             "4.0K\t/home/user/.ssh\n12M\t/home/user/Downloads\n..."),
        ],
    },
    "man": {
        "desc": "Xem hướng dẫn chi tiết lệnh (manual — gõ q để thoát)",
        "flags": {
            "-k": "Tìm kiếm trong mô tả (vd: man -k compress)",
            "-f": "Hiển thị section của lệnh (whatis)",
            "-w": "Đường dẫn đến file manual",
            "1": "Section 1: lệnh người dùng (mặc định)",
            "5": "Section 5: cấu hình file",
            "8": "Section 8: lệnh quản trị (root)",
        },
        "examples": [
            ("man ls", "Xem manual lệnh ls",
             "(mở pager — Space cuộn, / search, q thoát)"),
            ("man -k compress", "Tìm lệnh liên quan nén file",
             "compress (1) - compress files\n"
             "gzip (1) - compress files\n"
             "tar (1) - tape archive"),
        ],
    },
    "sudo": {
        "desc": "Chạy lệnh với quyền superuser (root)",
        "flags": {
            "-u user": "Chạy với tư cách user khác (không phải root)",
            "-i": "Đăng nhập shell root (giống su -)",
            "-s": "Shell root (giữ nguyên thư mục hiện tại)",
            "-l": "Liệt kê quyền sudo của user hiện tại",
            "-k": "Hết hiệu lực sudo (quên mật khẩu)",
        },
        "examples": [
            ("sudo apt update", "Cập nhật danh sách gói (root)",
             "[sudo] password for user:\nHit:1 http://archive.ubuntu.com jammy ..."),
            ("sudo -u www-data touch /var/www/test.txt",
             "Chạy với tư cách user www-data",
             "(tạo file với quyền của www-data)"),
        ],
    },
    "apt": {
        "desc": "Quản lý gói trên Ubuntu/Debian (advanced package tool)",
        "flags": {
            "update": "Cập nhật danh sách gói từ repositories",
            "upgrade": "Nâng cấp tất cả gói đã cài",
            "install": "Cài gói mới",
            "remove": "Gỡ gói (giữ file cấu hình)",
            "purge": "Gỡ gói + xóa cả cấu hình",
            "autoremove": "Gỡ gói không cần thiết (dependencies còn sót)",
            "search": "Tìm gói theo tên",
            "show": "Xem thông tin chi tiết gói",
            "list --installed": "Liệt kê gói đã cài",
        },
        "examples": [
            ("sudo apt update && sudo apt upgrade -y",
             "Cập nhật và nâng cấp tất cả",
             "Hit:1 http://archive.ubuntu.com jammy InRelease\n"
             "Reading package lists... Done\n"
             "0 upgraded, 0 newly installed, 0 to remove"),
            ("sudo apt install python3-pip -y",
             "Cài python3-pip",
             "Reading package lists... Done\n"
             "The following NEW packages will be installed:\n"
             "  python3-pip python3-setuptools...\n"
             "Setting up python3-pip (22.0.2+dfsg-1) ..."),
            ("apt search pdf editor", "Tìm gói",
             "okular - universal document viewer\n"
             "libreoffice-draw - LibreOffice drawing program"),
        ],
    },
    "systemctl": {
        "desc": "Quản lý service systemd",
        "flags": {
            "start": "Bật service",
            "stop": "Tắt service",
            "restart": "Khởi động lại",
            "reload": "Tải lại cấu hình (không dừng service)",
            "enable": "Tự động chạy khi khởi động",
            "disable": "Không chạy khi khởi động",
            "status": "Xem trạng thái + log gần đây",
            "is-active": "Kiểm tra đang chạy?",
            "list-units --type=service": "Liệt kê service",
            "daemon-reload": "Tải lại cấu hình systemd",
            "show": "Xem chi tiết unit",
        },
        "examples": [
            ("systemctl status sshd", "Trạng thái SSH daemon",
             "● sshd.service - OpenSSH Daemon\n"
             "   Loaded: loaded (/usr/lib/systemd/system/sshd.service; enabled)\n"
             "   Active: active (running) since Mon 2024-07-22 10:00:00 UTC"),
            ("sudo systemctl restart nginx", "Khởi động lại Nginx",
             "(không output — kiểm tra bằng systemctl status nginx)"),
        ],
    },
    "docker": {
        "desc": "Quản lý container Docker",
        "flags": {
            "ps": "Xem container đang chạy",
            "ps -a": "Xem tất cả container",
            "images": "Xem image đã tải",
            "pull": "Tải image từ registry",
            "run": "Chạy container từ image",
            "exec -it": "Vào container đang chạy",
            "stop": "Dừng container",
            "rm": "Xóa container",
            "rmi": "Xóa image",
            "logs": "Xem log container",
            "build": "Build image từ Dockerfile",
            "compose": "Quản lý multi-container (docker-compose)",
        },
        "examples": [
            ("docker ps", "Container đang chạy",
             "CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS   PORTS   NAMES\n"
             "a1b2c3d4e5f6   nginx     \"/...\"    2h ago    Up 2h    80/tcp  web"),
            ("docker run -d -p 8080:80 nginx",
             "Chạy Nginx, map cổng 8080→80",
             "a1b2c3d4e5f6...\n"
             "(truy cập http://localhost:8080)"),
            ("docker exec -it container_name bash",
             "Vào container (shell)",
             "root@a1b2c3d4e5f6:/#"),
        ],
    },
}


class ExplainDialog(QDialog):
    def __init__(self, storage=None, parent=None):
        super().__init__(parent)
        self.storage = storage
        self._ai_cache = load_cache()
        self._worker = None
        self.setWindowTitle("❓ Giải thích lệnh Linux")
        self.resize(640, 520)

        layout = QVBoxLayout()

        input_row = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("vd: grep -r -n 'pattern' /path")
        self.input_box.setStyleSheet("font-size: 22px; padding: 8px;")
        self.input_box.returnPressed.connect(self._search)
        input_row.addWidget(self.input_box)

        btn_search = QPushButton("🔍 Tra cứu")
        btn_search.setStyleSheet("font-size: 18px; padding: 8px;")
        btn_search.clicked.connect(self._search)
        input_row.addWidget(btn_search)
        layout.addLayout(input_row)
        self.btn_search = btn_search

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tab_explain = QWidget()
        self.explain_layout = QVBoxLayout(self.tab_explain)
        self.explain_scroll = QScrollArea()
        self.explain_scroll.setWidgetResizable(True)
        self.explain_inner = QWidget()
        self.explain_inner_layout = QVBoxLayout(self.explain_inner)
        self.explain_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.explain_scroll.setWidget(self.explain_inner)
        self.explain_layout.addWidget(self.explain_scroll)
        self.tabs.addTab(self.tab_explain, "🔍 Phân tích")

        self.tab_details = QWidget()
        self.details_layout = QVBoxLayout(self.tab_details)
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_inner = QWidget()
        self.details_inner_layout = QVBoxLayout(self.details_inner)
        self.details_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.details_scroll.setWidget(self.details_inner)
        self.details_layout.addWidget(self.details_scroll)
        self.tabs.addTab(self.tab_details, "📘 Cờ")

        self.tab_examples = QWidget()
        self.examples_layout = QVBoxLayout(self.tab_examples)
        self.examples_scroll = QScrollArea()
        self.examples_scroll.setWidgetResizable(True)
        self.examples_inner = QWidget()
        self.examples_inner_layout = QVBoxLayout(self.examples_inner)
        self.examples_inner_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.examples_scroll.setWidget(self.examples_inner)
        self.examples_layout.addWidget(self.examples_scroll)
        self.tabs.addTab(self.tab_examples, "📝 Ví dụ")

        close_btn = QPushButton("Đóng")
        close_btn.setStyleSheet("font-size: 18px; padding: 8px;")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

    def _clear(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _add_label(self, layout, text, style=""):
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        if style:
            lbl.setStyleSheet(style)
        layout.addWidget(lbl)
        return lbl

    def _search(self):
        cmd = self.input_box.text().strip()
        if not cmd:
            return
        self._clear(self.explain_inner_layout)
        self._clear(self.details_inner_layout)
        self._clear(self.examples_inner_layout)

        parts = cmd.split()
        name = parts[0]
        info = CMDS.get(name)

        if not info:
            matches = [k for k in CMDS if k.startswith(name)]
            if matches:
                name = matches[0]
                info = CMDS[name]

        if info:
            self.input_box.setText(name)
            self._build_explain(parts, info)
            self._build_flags(info)
            self._build_examples(info)
            self.tabs.setCurrentIndex(0)
            return

        # Không có trong danh sách dựng sẵn — thử cache AI đã tra trước đó
        cached = self._ai_cache.get(name)
        if cached:
            self._build_explain(parts, cached)
            self._build_flags(cached)
            self._build_examples(cached)
            self._add_label(self.explain_inner_layout, "")
            self._add_label(self.explain_inner_layout,
                            "🤖 (Kết quả từ AI, đã lưu lần tra trước)",
                            "font-size: 13px; color: #888;")
            self.tabs.setCurrentIndex(0)
            return

        # Chưa có ở đâu cả — thử hỏi AI nếu đã cấu hình API key
        api_key = (self.storage.config.get("groq_api_key", "") if self.storage else "").strip()
        if not api_key:
            self._add_label(self.explain_inner_layout,
                            f"Không có thông tin cho lệnh '{name}'.",
                            "font-size: 18px; color: #888;")
            self._add_label(self.explain_inner_layout,
                            "💡 Thêm Groq API key (miễn phí) trong Cài đặt để tự động "
                            "tra cứu AI cho các lệnh chưa có sẵn.",
                            "font-size: 14px; color: #ffa726;")
            self.tabs.setCurrentIndex(0)
            return

        self._add_label(self.explain_inner_layout,
                        f"🔍 Đang hỏi AI về lệnh '{name}'...",
                        "font-size: 18px; color: #42a5f5;")
        self.tabs.setCurrentIndex(0)
        self.btn_search.setEnabled(False)
        self.btn_search.setText("⏳ Đang tra cứu...")

        self._pending_parts = parts
        self._worker = AILookupWorker(name, api_key, self)
        self._worker.finished_ok.connect(self._on_ai_ok)
        self._worker.finished_err.connect(self._on_ai_err)
        self._worker.start()

    def _on_ai_ok(self, name, info):
        self.btn_search.setEnabled(True)
        self.btn_search.setText("🔍 Tra cứu")
        self._ai_cache[name] = info
        save_cache(self._ai_cache)

        self._clear(self.explain_inner_layout)
        self._clear(self.details_inner_layout)
        self._clear(self.examples_inner_layout)
        self.input_box.setText(name)
        parts = getattr(self, "_pending_parts", [name]) or [name]
        self._build_explain(parts, info)
        self._build_flags(info)
        self._build_examples(info)
        self._add_label(self.explain_inner_layout, "")
        self._add_label(self.explain_inner_layout,
                        "🤖 (Kết quả từ AI — có thể không hoàn toàn chính xác)",
                        "font-size: 13px; color: #888;")
        self.tabs.setCurrentIndex(0)

    def _on_ai_err(self, message):
        self.btn_search.setEnabled(True)
        self.btn_search.setText("🔍 Tra cứu")
        self._clear(self.explain_inner_layout)
        self._add_label(self.explain_inner_layout, f"❌ {message}",
                        "font-size: 16px; color: #f44336;")

    def _build_explain(self, parts, info):
        l = self.explain_inner_layout
        name = parts[0]
        self._add_label(l, f"📋 Lệnh: {name}", "font-size: 22px; font-weight: bold; color: #4caf50;")
        self._add_label(l, f"💡 {info['desc']}", "font-size: 18px; color: #42a5f5; padding-bottom: 8px;")
        self._add_label(l, "")

        args = parts[1:]
        for arg in args:
            if arg.startswith("-"):
                explanation = info["flags"].get(arg)
                if explanation:
                    self._add_label(l, f"  🔹 {arg}")
                    self._add_label(l, f"     → {explanation}", "font-size: 17px; color: #ccc;")
                else:
                    self._add_label(l, f"  🔹 {arg}  — (cờ không xác định, xem tab Cờ)", "color: #ffa726;")
            else:
                self._add_label(l, f"  📄 {arg}  — đối số", "color: #aaa;")
            self._add_label(l, "")

    def _build_flags(self, info):
        l = self.details_inner_layout
        flags = info.get("flags", {})
        if not flags:
            self._add_label(l, "Không có cờ đặc biệt.", "font-size: 18px; color: #888;")
            return

        self._add_label(l, f"📘 Các cờ (flags) của lệnh:", "font-size: 20px; font-weight: bold; padding-bottom: 8px;")
        self._add_label(l, "")
        for flag, desc in sorted(flags.items()):
            self._add_label(l, f"  {flag}")
            self._add_label(l, f"     → {desc}", "font-size: 17px; color: #bbb; padding-bottom: 4px;")

    def _build_examples(self, info):
        l = self.examples_inner_layout
        examples = info.get("examples", [])
        if not examples:
            self._add_label(l, "Không có ví dụ.", "font-size: 18px; color: #888;")
            return

        self._add_label(l, f"📝 Ví dụ sử dụng:", "font-size: 20px; font-weight: bold; padding-bottom: 8px;")
        for i, (cmd_example, desc, output) in enumerate(examples, 1):
            card = QWidget()
            card.setStyleSheet(
                "background-color: #1e1e2e; border: 1px solid #3a3a5a;"
                " border-radius: 8px; padding: 12px; margin: 6px 0;"
            )
            cl = QVBoxLayout(card)
            self._add_label(cl, f"Ví dụ {i}: {desc}", "font-size: 18px; font-weight: bold; color: #ffa726;")
            self._add_label(cl, "")
            self._add_label(cl, f"  $ {cmd_example}", "font-size: 17px; color: #80cbc4; font-family: monospace;")
            self._add_label(cl, "")
            self._add_label(cl, f"  Kết quả:", "font-size: 16px; color: #888;")
            self._add_label(cl, f"  {output}", "font-size: 16px; color: #aaa; font-family: monospace;")
            l.addWidget(card)
