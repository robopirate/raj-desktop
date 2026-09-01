import sys

path = r'C:\Users\itsom\OneDrive\Documents\GitHub\raj-desktop\engine.py'

with open(path, 'r') as f:
    lines = f.readlines()

# Lines 117-121 (1-indexed) = indices 116-120 (0-indexed) are corrupted
# Replace them with the correct closing of csr-wsl-5 + new csr sequence
new_block = '''            10: {
                "proposal_2nd": "https://drive.google.com/file/d/15-EuEcwci8olOSnm0V50laK3gVKCUCe-/view?usp=drive_link"
            }
        }
    },
    "csr": {
        "days": [1, 3, 5, 7, 10],
        "template_prefix": "CSR EMAIL ",
        "audience": "csr",
        "persona": "csr",
        "assets": {
            1: {
                "brochure": "https://drive.google.com/file/d/18jbIdKcZtHy6_yMFUF0C9c8MpNhp9lVA/view?usp=drive_link",
                "video_wsl": "https://www.instagram.com/p/DTDBcsdk9FI/",
                "video_abp": "https://youtu.be/FJ2_W53WjmA"
            },
            3: {
                "report_vbv": "https://drive.google.com/file/d/1d7EEtC8YitbSj7U6ivHf_6WtUGuylT-B/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA"
            },
            5: {
                "report_1st_wsl": "https://drive.google.com/file/d/1qiWBhOiklPpwU5NaVkqnfjA6v9q3YumS/view?usp=drive_link"
            },
            7: {
                "report_sangli1": "https://drive.google.com/file/d/1MUlsC87vRbhFaoW0XcX146WBLKYBk448/view?usp=drive_link",
                "video_abp": "https://youtu.be/FJ2_W53WjmA?si=ZFAr_bp_xU2Sduwr",
                "video_star": "https://www.youtube.com/watch?v=iziKPBSfGKU",
                "video_bandhuta": "https://www.youtube.com/watch?v=xVmaBnPyg9A",
                "video_sbn": "https://www.youtube.com/watch?v=d-TsgUkhIu0",
                "video_we": "https://www.instagram.com/reel/DMe2HzqofAk/?igsh=c201ZGxsOGFlMjJj"
            },
            10: {
                "plans": "https://drive.google.com/file/d/1p2CyHVZK_giZj0KNDGTTs_-s7HxVnQ_C/view?usp=drive_link"
            }
        }
    }
}

EMAIL_NUM_TO_DAY = {1: 1, 2: 3, 3: 5, 4: 7, 5: 10}
DAY_TO_EMAIL_NUM = {1: 1, 3: 2, 5: 3, 7: 4, 10: 5}
'''

# Replace lines 116-125 (0-indexed) with new block
# First find where SEQUENCES dict ends
lines[116:126] = [new_block]

with open(path, 'w') as f:
    f.writelines(lines)

print("Fixed engine.py SEQUENCES dict")
