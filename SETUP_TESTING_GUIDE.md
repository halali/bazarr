# 🧪 Návod na testovanie AutoSubSync integrácie / Testing Guide

## 🇸🇰 Slovensky

### 1. Inštalácia dependencies
```bash
# Nainštaluj autosubsync
pip install autosubsync

# Nainštaluj FFmpeg (ak ho nemáš)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Stiahni z https://ffmpeg.org/download.html
```

### 2. Rýchly test
```bash
python3 test_autosubsync_integration.py
```

### 3. Testovanie v Bazarr

#### Príprava:
```bash
# Choď do Bazarr priečinka
cd /path/to/bazarr

# Nainštaluj Bazarr dependencies
pip install -r requirements.txt

# Spusti Bazarr
python3 bazarr.py
```

#### V Bazarr UI:
1. Choď do **Settings → Subtitles**
2. Zapni "**Automatic Subtitles Audio Synchronization**"
3. V "**Sync Method**" vyber "**AutoSubSync**"
4. Nastav threshold podľa potreby
5. Uložiť nastavenia

#### Test s reálnymi súbormi:
1. Majaj video súbor (napr. `movie.mp4`)
2. Majaj nesynchronizované titulky (napr. `movie.srt`)
3. V Bazarr klikni na titulky → "Sync"
4. AutoSubSync bude použitý namiesto FFSubSync

### 4. Kontrola logov
```bash
# Pozri Bazarr logy pre autosubsync aktivity
tail -f /path/to/bazarr/log/bazarr.log | grep -i autosubsync
```

---

## 🇬🇧 English

### 1. Install dependencies
```bash
# Install autosubsync
pip install autosubsync

# Install FFmpeg (if not already installed)
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: Download from https://ffmpeg.org/download.html
```

### 2. Quick test
```bash
python3 test_autosubsync_integration.py
```

### 3. Testing in Bazarr

#### Setup:
```bash
# Go to Bazarr directory
cd /path/to/bazarr

# Install Bazarr dependencies
pip install -r requirements.txt

# Start Bazarr
python3 bazarr.py
```

#### In Bazarr UI:
1. Go to **Settings → Subtitles**
2. Enable "**Automatic Subtitles Audio Synchronization**"
3. In "**Sync Method**" select "**AutoSubSync**"
4. Configure thresholds as needed
5. Save settings

#### Test with real files:
1. Have a video file (e.g., `movie.mp4`)
2. Have unsynchronized subtitles (e.g., `movie.srt`)
3. In Bazarr click on subtitles → "Sync"
4. AutoSubSync will be used instead of FFSubSync

### 4. Check logs
```bash
# Watch Bazarr logs for autosubsync activity
tail -f /path/to/bazarr/log/bazarr.log | grep -i autosubsync
```

---

## 🎯 Očakávané výsledky / Expected Results

### ✅ Úspešný test / Successful test:
- AutoSubSync library sa načíta bez chyby
- FFmpeg je dostupný
- V Bazarr UI je dostupná "AutoSubSync" možnosť
- Logy obsahujú "starting autosubsync synchronization"
- Titulky sa úspešne zosynchronizujú s vyššou presnosťou

### ❌ Možné problémy / Possible issues:
- `ImportError: No module named 'autosubsync'` → Nainštaluj `pip install autosubsync`
- `FFmpeg not found` → Nainštaluj FFmpeg
- Pomalé spracovanie → Normálne, AutoSubSync je pomalší ale presnejší
- Vysoké využitie pamäte → Normálne, AutoSubSync potrebuje viac RAM

## 🔧 Debugging

### Zapni debug mode:
1. V Bazarr Settings → Subtitles
2. Zapni "Debug" checkbox
3. AutoSubSync vytvorí debug súbory vedľa video súboru

### Test s command line:
```bash
# Priamy test autosubsync
autosubsync video.mp4 subtitles.srt output_synced.srt

# Alebo cez Python
python3 -c "
import autosubsync
result = autosubsync.synchronize('video.mp4', 'input.srt', 'output.srt')
print('Result:', result)
"
```

## 📊 Porovnanie výkonu / Performance Comparison

| Vlastnosť | FFSubSync | AutoSubSync |
|-----------|-----------|-------------|
| Presnosť | ~0.5s | ~0.15s |
| Rýchlosť | Rýchly | Pomalý (~3min) |
| Pamäť | Nízka | Vysoká (~1.5GB) |
| Metóda | WebRTC VAD | Machine Learning |

---

## 🎉 Hotovo!

Ak všetko funguje, budeš mať v Bazarr dostupnú vyššiu presnosť synchronizácie titulkov pomocou machine learning namiesto tradičnej WebRTC metódy!