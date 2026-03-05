import os
import re

files_to_update = [
    'src/views/user/Detection.vue'
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    replacements = {
        r"Drop image here or <em>click to upload</em>": "{{ $t('detection.dropOrClick') }}",
        r"Supported formats: JPG, PNG, GIF \(Max 10MB\)": "{{ $t('detection.supportedFormats') }}",
        r"Start Detection\n\s*</el-button>": "{{ $t('dashboard.startDetection') }}\n              </el-button>",
        r">\s*Cancel\s*</el-button>": ">{{ $t('common.cancel') }}</el-button>",
        r">\s*New Detection\s*</el-button>": ">{{ $t('detection.newDetection') }}</el-button>",
        r">\s*Verify Certification\s*</el-button>": ">{{ $t('detection.verifyCert') }}</el-button>",
        r">\s*View Traceability\s*</el-button>": ">{{ $t('detection.viewTraceability') }}</el-button>",
    }

    for pattern, repl in replacements.items():
        content = re.sub(pattern, repl, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Fixed buttons detection")
