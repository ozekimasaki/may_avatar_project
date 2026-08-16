# Session tracking

人間が Inochi Session + カメラ Calibration を行う。エージェントは CSV を解析するだけ。

最低ラベル:

- neutral 10s
- blink 10
- look L/R
- look U/D
- mouth_closed
- mouth_small / mouth_normal / mouth_loud

保存先: `05_session/tracking_raw.csv`

列: timestamp,label,eye_open_l,eye_open_r,mouth_open,head_x,head_y,head_z,eye_ball_x,eye_ball_y

その後:

```
python -m scripts.calibrate_tracking
```
