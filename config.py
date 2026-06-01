import os
import sys

REG_PATH          = r"Software\BATacticHelper"
ICON_URL_TEMPLATE = "https://schaledb.com/images/student/icon/{}.webp"
ICON_SIZE         = (36, 36)
MAX_SLOTS         = 50
SLOTS_VISIBLE     = 5

STUDENTS_URLS = {
    "ko": "https://schaledb.com/data/kr/students.min.json",
    "en": "https://schaledb.com/data/en/students.min.json",
    "ja": "https://schaledb.com/data/jp/students.min.json",
    "zh": "https://schaledb.com/data/cn/students.min.json",
}

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_save_path():
    return os.path.join(get_base_dir(), "ba_guides.json")

def get_students_path():
    return os.path.join(get_base_dir(), "ba_students.json")

def get_custom_dict_path():
    return os.path.join(get_base_dir(), "ba_custom_dict.json")

def get_custom_skills_path():
    return os.path.join(get_base_dir(), "ba_custom_skills.json")

def get_config_path():
    return os.path.join(get_base_dir(), "ba_config.json")

def get_images_dir():
    d = os.path.join(get_base_dir(), "images")
    os.makedirs(d, exist_ok=True)
    return d

def get_icon_path(student_id):
    return os.path.join(get_images_dir(), f"{student_id}.webp")

TRANSLATIONS = {
    "ko": {
        "title": "블아 택틱 도우미 v2", "hotkey_on": "단축키 켜기", "hotkey_active": "단축키 켜짐 (수정불가)",
        "first": "⏪ 처음", "last": "마지막 ⏩", "settings": "⚙️ 설정",
        "img_toggle_off": "🖼 이미지 OFF", "img_toggle_on": "🖼 이미지 ON",
        "placeholder": "여기에 공략을 복사해서 붙여넣으세요.\n(Ctrl+V)\n\n클릭하면 해당 순서로 이동합니다.",
        "error_title": "오류", "error_msg": "잘못된 단축키 형식입니다.",
        "s_title": "설정",
        "s_margin": "상단 고정 (몇 번째 줄):", "s_color": "하이라이트 색상:",
        "s_fg_color": "글자 색상:", "s_bg_color": "배경 색상:", "s_size": "글자 크기:", "s_icon_size": "이미지 크기:", "s_icon_pad": "이미지 패딩:", "s_lang": "언어 (Language):", "s_opacity": "배경 투명도 (%):", "s_debug": "디버그 콘솔 표시",
        "s_hotkeys": "단축키 설정 열기...", "hk_title": "단축키 설정", "hk_prev": "이전 줄 이동", "hk_next": "다음 줄 이동", "hk_ex": "EX 스킬", "hk_support": "지원 스킬", "hk_custom_add": "+ 커스텀 추가", "hk_waiting": "키보드 누르세요... (Esc: 취소)",
        "s_save": "저장", "s_cancel": "취소", "auto": "자동 감지 (Auto)",
        "s_custom_dict": "통상 명칭 관리",
        "cd_title": "통상 명칭 사전 관리",
        "cd_alias": "통상 명칭 (예: 딸랑구)", "cd_student": "학생 이름 (예: 히나)",
        "cd_add": "추가", "cd_delete": "선택 삭제", "cd_close": "닫기",
        "cd_err_empty": "통상 명칭과 학생 이름을 모두 입력하세요.",
        "cd_err_dup": "이미 등록된 통상 명칭입니다.",
        "loading_done": "학생 데이터 로드 완료",
        "loading_fail": "학생 데이터 로드 실패 (캐시 사용)",
        "updating": "학생 데이터 업데이트 중...",
        "img_downloading": "아이콘 다운로드 중...",
    },
    "en": {
        "title": "BA Tactic Helper v2", "hotkey_on": "Hotkeys OFF", "hotkey_active": "Hotkeys ON (Read-Only)",
        "first": "⏪ First", "last": "Last ⏩", "settings": "⚙️ Settings",
        "img_toggle_off": "🖼 Image OFF", "img_toggle_on": "🖼 Image ON",
        "placeholder": "Paste your guide here.\n(Ctrl+V)\n\nClick to move.",
        "error_title": "Error", "error_msg": "Invalid hotkey format.",
        "s_title": "Settings",
        "s_margin": "Top Margin (Lines):", "s_color": "Highlight Color:",
        "s_fg_color": "Text Color:", "s_bg_color": "Background Color:", "s_size": "Font Size:", "s_icon_size": "Icon Size:", "s_icon_pad": "Icon Padding:", "s_lang": "Language:", "s_opacity": "Opacity (%):", "s_debug": "Show Debug Console",
        "s_hotkeys": "Open Hotkeys Settings...", "hk_title": "Hotkey Settings", "hk_prev": "Previous Line", "hk_next": "Next Line", "hk_ex": "EX Skill", "hk_support": "Support Skill", "hk_custom_add": "+ Add Custom", "hk_waiting": "Press any key... (Esc: Cancel)",
        "s_save": "Save", "s_cancel": "Cancel", "auto": "Auto Detect",
        "s_custom_dict": "Alias Manager",
        "cd_title": "Custom Alias Manager",
        "cd_alias": "Alias (e.g. Daughtie)", "cd_student": "Student Name (e.g. Hina)",
        "cd_add": "Add", "cd_delete": "Delete Selected", "cd_close": "Close",
        "cd_err_empty": "Please enter both alias and student name.",
        "cd_err_dup": "This alias is already registered.",
        "loading_done": "Student data loaded",
        "loading_fail": "Student data load failed (using cache)",
        "updating": "Updating student data...",
        "img_downloading": "Downloading icons...",
    },
    "ja": {
        "title": "BAタクティクスヘルパー v2", "hotkey_on": "ホットキー OFF", "hotkey_active": "ホットキー ON (読み取り専用)",
        "first": "⏪ 最初", "last": "最後 ⏩", "settings": "⚙️ 設定",
        "img_toggle_off": "🖼 画像 OFF", "img_toggle_on": "🖼 画像 ON",
        "placeholder": "攻略をここに貼り付けてください。\n(Ctrl+V)\n\nクリックで移動します。",
        "error_title": "エラー", "error_msg": "無効なホットキー形式です。",
        "s_title": "設定",
        "s_margin": "上部余白 (行数):", "s_color": "ハイライト色:",
        "s_fg_color": "文字色:", "s_bg_color": "背景色:", "s_size": "フォントサイズ:", "s_icon_size": "アイコンサイズ:", "s_icon_pad": "アイコン余白:", "s_lang": "言語 (Language):", "s_opacity": "背景透明度 (%):", "s_debug": "デバッグコンソール表示",
        "s_hotkeys": "ホットキー設定を開く...", "hk_title": "ホットキー設定", "hk_prev": "前の行へ", "hk_next": "次の行へ", "hk_ex": "EX スキル", "hk_support": "支援スキル", "hk_custom_add": "+ カスタム追加", "hk_waiting": "キーを入力... (Esc: キャンセル)",
        "s_save": "保存", "s_cancel": "キャンセル", "auto": "自動検出 (Auto)",
        "s_custom_dict": "通称管理",
        "cd_title": "通称辞書管理",
        "cd_alias": "通称 (例: 娘ちゃん)", "cd_student": "生徒名 (例: ヒナ)",
        "cd_add": "追加", "cd_delete": "選択削除", "cd_close": "閉じる",
        "cd_err_empty": "通称と生徒名を両方入力してください。",
        "cd_err_dup": "この通称はすでに登録されています。",
        "loading_done": "生徒データ読み込み完了",
        "loading_fail": "生徒データ読み込み失敗 (キャッシュ使用)",
        "updating": "生徒データを更新中...",
        "img_downloading": "アイコンをダウンロード中...",
    },
    "zh": {
        "title": "BA战术助手 v2", "hotkey_on": "快捷键 OFF", "hotkey_active": "快捷键 ON (只读)",
        "first": "⏪ 最前", "last": "最后 ⏩", "settings": "⚙️ 设置",
        "img_toggle_off": "🖼 图片 OFF", "img_toggle_on": "🖼 图片 ON",
        "placeholder": "请将攻略粘贴到此处。\n(Ctrl+V)\n\n点击可跳转到对应位置。",
        "error_title": "错误", "error_msg": "快捷键格式无效。",
        "s_title": "设置",
        "s_margin": "顶部边距 (行数):", "s_color": "高亮颜色:",
        "s_fg_color": "文字颜色:", "s_bg_color": "背景颜色:", "s_size": "字体大小:", "s_icon_size": "图标大小:", "s_icon_pad": "图标内边距:", "s_lang": "语言 (Language):", "s_opacity": "背景透明度 (%):", "s_debug": "显示调试控制台",
        "s_hotkeys": "打开快捷键设置...", "hk_title": "快捷键设置", "hk_prev": "上一行", "hk_next": "下一行", "hk_ex": "EX 技能", "hk_support": "支援技能", "hk_custom_add": "+ 添加自定义", "hk_waiting": "请按下任意键... (Esc: 取消)",
        "s_save": "保存", "s_cancel": "取消", "auto": "自动检测 (Auto)",
        "s_custom_dict": "别名管理",
        "cd_title": "别名词典管理",
        "cd_alias": "别名 (例: 闺女)", "cd_student": "学生名 (例: 日奈)",
        "cd_add": "添加", "cd_delete": "删除选中", "cd_close": "关闭",
        "cd_err_empty": "请同时输入别名和学生名。",
        "cd_err_dup": "该别名已注册。",
        "loading_done": "学生数据加载完成",
        "loading_fail": "学生数据加载失败 (使用缓存)",
        "updating": "正在更新学生数据...",
        "img_downloading": "正在下载图标...",
    },
}
