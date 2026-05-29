import os

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
    return os.path.dirname(os.path.abspath(__file__))

def get_save_path():
    return os.path.join(get_base_dir(), "ba_guides.json")

def get_students_path():
    return os.path.join(get_base_dir(), "ba_students.json")

def get_custom_dict_path():
    return os.path.join(get_base_dir(), "ba_custom_dict.json")

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
        "s_title": "설정", "s_prev": "이전 단축키:", "s_next": "다음 단축키:",
        "s_margin": "상단 고정 (몇 번째 줄):", "s_color": "하이라이트 색상:",
        "s_size": "글자 크기:", "s_icon_size": "이미지 크기:", "s_lang": "언어 (Language):", "s_opacity": "배경 투명도 (%):",
        "s_save": "저장", "s_cancel": "취소", "auto": "자동 감지 (Auto)",
        "s_custom_dict": "통상 명칭 관리",
        "cd_title": "통상 명칭 사전 관리",
        "cd_alias": "통상 명칭 (예: 드레스히나)", "cd_student": "학생 이름 (예: 드히나)",
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
        "s_title": "Settings", "s_prev": "Prev Hotkey:", "s_next": "Next Hotkey:",
        "s_margin": "Top Margin (Lines):", "s_color": "Highlight Color:",
        "s_size": "Font Size:", "s_icon_size": "Icon Size:", "s_lang": "Language:", "s_opacity": "Opacity (%):",
        "s_save": "Save", "s_cancel": "Cancel", "auto": "Auto Detect",
        "s_custom_dict": "Alias Manager",
        "cd_title": "Custom Alias Manager",
        "cd_alias": "Alias (e.g. drhina)", "cd_student": "Student Name (e.g. Hina)",
        "cd_add": "Add", "cd_delete": "Delete Selected", "cd_close": "Close",
        "cd_err_empty": "Please enter both alias and student name.",
        "cd_err_dup": "This alias is already registered.",
        "loading_done": "Student data loaded",
        "loading_fail": "Student data load failed (using cache)",
        "updating": "Updating student data...",
        "img_downloading": "Downloading icons...",
    },
}
for _lang in ("ja", "zh"):
    TRANSLATIONS[_lang] = TRANSLATIONS["en"].copy()
