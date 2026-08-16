# TRACK-OK / OBS-OK / RELEASE

## TRACK-OK
- [ ] tracking_raw.csv に neutral / blink / look / mouth 区間
- [ ] silent mouth 95 percentile deadzone
- [ ] Blink raw open/closed median → 1/0
- [ ] 感覚調整だけの変更は FAIL

## OBS-OK
- [ ] face / mouth / eyes / flower / full スクショ
- [ ] 顔 bbox がフレーム内
- [ ] crop/scale 破綻なし

## RELEASE-v0.1
- [ ] 30分録画
- [ ] 2秒に1枚の contact sheet
- [ ] stream_review.json
- [ ] 予算 cap 6 以内
- [ ] 手描きなし

## RELEASE-v0.2
- [ ] 新規画像 0
- [ ] BodyX / Breath / Ahoge / Hair / Ribbon Physics
- [ ] 10分スモーク

## RELEASE-v0.3
- [ ] 表情は Brows + EyeOpen + Mouth
- [ ] Expression Atlas は不足時 ×1 まで

## RELEASE-v1.0
- [ ] 08_repro/pins.yaml
- [ ] scripts/repro_check.py が通る
