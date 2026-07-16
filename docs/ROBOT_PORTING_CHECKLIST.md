# 不同机器人适配清单

本清单只覆盖软件、模型、动作、语音、姿态和节奏资源的适配。

硬件方面不做任何改变：所有硬件连接方式都按现有项目默认配置使用，不在本清单中调整。

## 1. 必须修改

| 项目 | 文件/位置 | 要改什么 | 影响 |
| --- | --- | --- | --- |
| 热词模型 | `main.py` 的 `model = "model/YiFeng2025.pmdl"` | 换成新机器人的 `.pmdl` 文件路径，并把模型放入 `model/` | 决定唤醒词 |
| 动作文件名前缀 | `action_neo.py` 中 `DataPackageConverter('scw' + action_keyword + ".bin/.odr")` | 确认下位机动作文件是否仍使用 `scw` 前缀 | 决定下位机能否找到动作文件 |
| 回位/准备动作 | `action_neo.py` 中 `scwadapt.bin`、`scwreturn.bin` | 换成新机器人对应的准备/回位动作文件名 | 姿态识别前后动作 |
| 姿态分类器 | `posture_recognition/static_recognition.py` 的 `YiFeng_pose_recognizer.pickle` | 换成新机器人/新姿态集合训练出的分类器 | 决定能识别哪些姿态 |
| Vosk 模型 | `speech_recog.py` 的 `vosk.Model("model")` | 如果语音模型目录变化，需要同步路径 | 决定语音识别可用性 |
| 自启动路径 | `deployment/killjoy.desktop` | 修改 `/home/pi/Desktop/start.sh` 为实际启动脚本路径 | 决定开机自启动 |

## 2. 新增语音动作

新增一个“语音直接控制动作”时，需要同步这些内容：

1. 修改 `speech_train.json`：

```json
"动作中文名": {
  "name": "ActionName",
  "list": ["可能识别出来的关键词1", "可能识别出来的关键词2"]
}
```

2. 新增反馈音频：

```text
resources/ActionName.MP3
```

3. 新增或确认下位机动作文件：

```text
scwActionName.bin
scwActionName.odr
```

4. 如果这个动作属于移动类动作，需要检查 `action_neo.py` 中使用 `.odr` 的动作列表：

```python
if action in ["左移", "右移", "向左转", "向右转", "前进", "后退"]:
```

移动类动作通常走 `.odr`，普通姿态/单动作通常走 `.bin`。

## 3. 新增姿态识别动作

新增一个姿态类别时，需要同步这些内容：

| 内容 | 位置 | 说明 |
| --- | --- | --- |
| 采集图片类别 | `scripts/capture_to_image_folder.py` 的 `CLASSES` | 加入新姿态类别名 |
| 训练图片 | `image/<PoseName>/` | 用采集脚本生成 |
| 姿态分类器 | `posture_recognition/output/<robot>_pose_recognizer.pickle` | 重新训练后替换 |
| 姿态标签音频 | `resources/<PoseName>.MP3` | `action_neo.py` 会按识别结果拼接播放 |
| 下位机动作文件 | `scw<PoseName>.bin` | `action_neo.py` 会按识别结果拼接发送 |

注意：`action_neo.py` 中姿态识别分支使用：

```python
play_audio("resources/" + pose + ".MP3")
DataPackageConverter("scw" + pose + ".bin")
```

所以姿态分类器输出的标签、音频文件名、下位机动作文件名必须一致。

## 4. 新增节奏/歌曲识别

新增一首用于节奏识别的歌曲时，需要同步这些内容：

1. 把训练音频放入：

```text
rhythm_train/
```

2. 运行训练脚本生成数据库：

```bash
python3 rhythm_train/rhythm_train.py
```

3. 确认生成或更新：

```text
beatDatabase1.npy
```

4. 准备运行时播放资源：

```text
resources/<song file>
resources/index<song file>
```

例如当前 `choice.mp3` 对应：

```text
resources/choice.mp3
resources/indexchoice.mp3
```

5. 如果新歌曲需要不同舞蹈动作，修改 `action_neo.py` 的节奏分支：

```python
if matched_song == "choice.mp3":
    movements = DataPackageConverter("scwDance2.odr").hex_output
else:
    movements = DataPackageConverter("scwDance1.odr").hex_output
```

## 5. 新增提示音/系统音

这些提示音被代码直接引用，换机器人或换语音包时要保持文件名不变，或同步改代码：

| 文件 | 用途 |
| --- | --- |
| `resources/ding.wav` | 开始录音/启动提示 |
| `resources/dong.wav` | 结束录音/开始识别提示 |
| `resources/sorry.MP3` | 未识别或失败 |
| `resources/pose.MP3` | 进入姿态识别 |
| `resources/rhythm.MP3` | 进入节奏识别 |
| `resources/finish.MP3` | 节奏录音结束 |
| `resources/please_speak.MP3` | 连续语音模式提示 |
| `resources/exit.MP3` | 退出连续语音模式 |
| `resources/timeout.MP3` | 姿态识别超时 |
| `resources/stop.MP3` | 识别到停止姿态 |

## 6. 部署前检查

换机器人后至少跑一遍：

```bash
python3 speech_recog.py
python3 posture_recognition/static_recognition.py
python3 rhythm_train/rhythm_train.py
python3 main.py
```

软件和资源检查：

- 热词模型路径正确。
- Vosk 模型目录可加载。
- 姿态分类器 pickle 文件存在。
- `mplayer` 可播放 `resources/` 下音频。
- 下位机动作文件名与 `DataPackageConverter(...)` 生成的文件名一致。
- `deployment/killjoy.desktop` 指向真实启动脚本。
