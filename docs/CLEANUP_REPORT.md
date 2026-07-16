# 项目减法清单

## 已清理

以下内容属于缓存、编辑器临时文件、系统元数据、运行产物或确认无引用的重复副本，已从工作区删除：

- `__pycache__/`
- `.action_neo.py.swo`
- `.action_neo.py.swp`
- `snowboydecoder.pyc`
- `.DS_Store` / `._*`
- `YiFeng2025.pmdl`
- `beatDatabase.npy`
- `resources/choice.wav`
- `resources/beatDatabase.npy`
- `tracker/beatDatabase.npy`
- `temp_record/*.wav`
- `temp_record/*.MP3`
- `result.txt`
- `last_result.jpg`
- `speech.txt`
- `.idea/`

## 结构调整

- `PROJECT_OVERVIEW.md` -> `docs/PROJECT_OVERVIEW.md`
- `CLEANUP_REPORT.md` -> `docs/CLEANUP_REPORT.md`
- `1` -> `deployment/killjoy.desktop`
- `1.py` -> `archive/legacy/rhythm_recog_absolute_path_legacy.py`
- `try.py` -> `archive/legacy/action_neo_experimental.py`
- `capture_to_image_folder.py` -> `scripts/capture_to_image_folder.py`
- `rhythm_recog.py` -> `archive/legacy/rhythm_recog.py`
- `onsetDatabase.npy` -> `archive/legacy/onsetDatabase.npy`
- `action_mapping.json` -> `archive/legacy/action_mapping.json`
- `rhythm_db.npy` -> `archive/legacy/rhythm_db.npy`
- `word.txt` -> `archive/legacy/word.txt`
- `README.md` -> `archive/legacy/README_legacy.md`，并重建根目录 README 作为项目入口索引
- `ml/` -> `archive/legacy/tflite_pose/ml/`
- `tracker/` -> `archive/legacy/tflite_pose/tracker/`

## 已整理的代码路径

- `rhythm_train/rhythm_train.py`：训练输出已改为 `beatDatabase1.npy`，与 `rhythm_recog1.py` 读取路径一致。
- `rhythm_recog1.py`：补上 `beatDatabase1.npy` 的实际加载语句，避免 `all_data` 未定义。
- `speech_recog.py`、`rhythm_recog1.py`：写入录音文件前会自动创建 `temp_record/`。
- `scripts/capture_to_image_folder.py`：移动到 `scripts/` 后补充项目根目录导入路径，仍可用 `python3 scripts/capture_to_image_folder.py` 运行。
- `ml/` 和 `tracker/`：归档为备用 TFLite MoveNet/PoseNet 姿态估计实现；当前主流程使用 `posture_recognition/static_recognition.py` 的 MediaPipe 实现。

## 内容完全相同但暂未删除

| 重复组 | 路径 | 当前判断 |
| --- | --- | --- |
| 语音动作音频 | `resources/BothHandsUp.MP3`、`resources/handsup.MP3` | `speech_train.json` 使用 `BothHandsUp`，采集工具使用 `handsup` 作为图片类别名。两个文件语义不同，虽然内容相同，不直接删除。 |
| SWIG 接口文件 | `swig/Python/snowboy-detect-swig.i`、`swig/Python3/snowboy-detect-swig.i` | Python2/Python3 构建目录各自引用，暂不删除。 |

## 后续建议

1. 判断 `resources/BothHandsUp.MP3` 和 `resources/handsup.MP3` 是否允许用同一个规范名替代。
2. 如果只部署树莓派，可继续裁剪 `lib/` 和 `swig/`，例如只保留 `lib/rpi`、`swig/Python3` 及运行所需 `.so`。
3. 补充 `requirements.txt` 或安装脚本，降低新树莓派部署成本。
