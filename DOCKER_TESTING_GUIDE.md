# 🐳 Docker Testing Guide pre AutoSubSync integráciu / Docker Testing Guide for AutoSubSync Integration

## 🇸🇰 Slovensky

### Prečo Docker?
- **Izolácia**: Nezávislé prostredie bez ovplyvnenia systému
- **Reprodukovateľnosť**: Rovnaké prostredie na každom systéme  
- **Jednoduchosť**: Automatická inštalácia všetkých dependencies
- **Testovanie**: Bezpečné testovanie bez rizikovanie produkčného systému

### Predpoklady
```bash
# Nainštaluj Docker
# Ubuntu/Debian:
sudo apt install docker.io docker-compose

# macOS:
brew install docker docker-compose

# Windows: Docker Desktop z https://docker.com
```

### Rýchle spustenie
```bash
# 1. Rýchly integration test
./docker-test.sh test

# 2. Spusti Bazarr s AutoSubSync
./docker-test.sh start

# 3. Otvor v browseri: http://localhost:6767
```

### Detailné kroky

#### 1. Integration Test
```bash
# Testuje iba základnú funkcionalitu
./docker-test.sh test

# Očakávaný výstup:
# ✅ AutoSubSync library is available
# ✅ FFmpeg available  
# ✅ Integration test passed!
```

#### 2. Spustenie Bazarr
```bash
# Build a spustí Bazarr container
./docker-test.sh start

# Bazarr bude dostupný na: http://localhost:6767
```

#### 3. Konfigurácia v Bazarr UI
1. Otvor http://localhost:6767
2. Choď do **Settings → Subtitles**
3. Zapni "**Automatic Subtitles Audio Synchronization**"
4. V "**Sync Method**" vyber "**AutoSubSync**"
5. Nastav thresholds podľa potreby
6. **Save**

#### 4. Test s reálnymi súbormi
```bash
# Vytvor test_media priečinok a vlož súbory
mkdir -p test_media
cp /path/to/your/movie.mp4 test_media/
cp /path/to/your/movie.srt test_media/

# Reštartuj container aby videl súbory
./docker-test.sh restart
```

#### 5. Monitorovanie
```bash
# Pozri logy v realtime
./docker-test.sh logs

# Hľadaj AutoSubSync aktivity
docker exec bazarr-autosubsync-test tail -f /app/data/log/bazarr.log | grep -i autosubsync
```

### Príkazy

```bash
# Všetky dostupné príkazy
./docker-test.sh help

# Príkazy:
./docker-test.sh test      # Integration test iba
./docker-test.sh start     # Spusti Bazarr
./docker-test.sh stop      # Zastav containers
./docker-test.sh logs      # Ukáž logy
./docker-test.sh restart   # Reštartuj
./docker-test.sh clean     # Vymaž všetko vrátane volumes
```

---

## 🇬🇧 English

### Why Docker?
- **Isolation**: Independent environment without affecting your system
- **Reproducibility**: Same environment on every system
- **Simplicity**: Automatic installation of all dependencies
- **Testing**: Safe testing without risking production system

### Prerequisites
```bash
# Install Docker
# Ubuntu/Debian:
sudo apt install docker.io docker-compose

# macOS:
brew install docker docker-compose

# Windows: Docker Desktop from https://docker.com
```

### Quick Start
```bash
# 1. Quick integration test
./docker-test.sh test

# 2. Start Bazarr with AutoSubSync
./docker-test.sh start

# 3. Open in browser: http://localhost:6767
```

### Detailed Steps

#### 1. Integration Test
```bash
# Tests only basic functionality
./docker-test.sh test

# Expected output:
# ✅ AutoSubSync library is available
# ✅ FFmpeg available  
# ✅ Integration test passed!
```

#### 2. Starting Bazarr
```bash
# Build and start Bazarr container
./docker-test.sh start

# Bazarr will be available at: http://localhost:6767
```

#### 3. Configuration in Bazarr UI
1. Open http://localhost:6767
2. Go to **Settings → Subtitles**
3. Enable "**Automatic Subtitles Audio Synchronization**"
4. In "**Sync Method**" select "**AutoSubSync**"
5. Configure thresholds as needed
6. **Save**

#### 4. Test with Real Files
```bash
# Create test_media folder and add files
mkdir -p test_media
cp /path/to/your/movie.mp4 test_media/
cp /path/to/your/movie.srt test_media/

# Restart container to see files
./docker-test.sh restart
```

#### 5. Monitoring
```bash
# Watch logs in realtime
./docker-test.sh logs

# Look for AutoSubSync activities
docker exec bazarr-autosubsync-test tail -f /app/data/log/bazarr.log | grep -i autosubsync
```

### Commands

```bash
# All available commands
./docker-test.sh help

# Commands:
./docker-test.sh test      # Integration test only
./docker-test.sh start     # Start Bazarr
./docker-test.sh stop      # Stop containers
./docker-test.sh logs      # Show logs
./docker-test.sh restart   # Restart
./docker-test.sh clean     # Remove everything including volumes
```

---

## 🔧 Pokročilé testovanie / Advanced Testing

### Manual Docker Commands
```bash
# Manuálny build
docker-compose build bazarr-autosubsync

# Spustenie s debug output
docker-compose up bazarr-autosubsync

# Exec do running container
docker exec -it bazarr-autosubsync-test bash

# Test AutoSubSync v containeri
docker exec bazarr-autosubsync-test python3 -c "
import autosubsync
print('AutoSubSync version:', getattr(autosubsync, '__version__', 'unknown'))
result = autosubsync.synchronize('/test.mp4', '/test.srt', '/output.srt')
print('API test result:', result)
"
```

### Volume Mapping
```bash
# Mount vlastné media files
docker run -it --rm \
  -p 6767:6767 \
  -v /path/to/your/media:/media \
  -v bazarr_config:/app/data/config \
  bazarr-autosubsync-test
```

### Environment Variables
```bash
# Nastav environment variables
docker-compose up -e PYTHONPATH=/app -e DEBUG=1 bazarr-autosubsync
```

## 🐛 Troubleshooting

### Container sa nespúšťa
```bash
# Pozri build logy
docker-compose build --no-cache bazarr-autosubsync

# Pozri startup logy
docker-compose logs bazarr-autosubsync

# Debug v interactive mode
docker run -it --rm bazarr-autosubsync-test bash
```

### AutoSubSync nefunguje
```bash
# Test v containeri
docker exec bazarr-autosubsync-test python3 -c "
try:
    import autosubsync
    print('✅ AutoSubSync imported successfully')
except ImportError as e:
    print('❌ AutoSubSync import failed:', e)

import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
    print('✅ FFmpeg available' if result.returncode == 0 else '❌ FFmpeg failed')
except:
    print('❌ FFmpeg not found')
"
```

### Port konflikty
```bash
# Používaj iný port
docker-compose up -e PORT=6768 bazarr-autosubsync
# Alebo v docker-compose.yml zmeň: "6768:6767"
```

### Pamäťové problémy
```bash
# Pridaj memory limits do docker-compose.yml
services:
  bazarr-autosubsync:
    mem_limit: 2g
    mem_reservation: 1g
```

## 📊 Výsledky testovania / Test Results

### ✅ Úspešné testy
- Container sa spustí bez chyby
- Bazarr UI dostupné na http://localhost:6767
- AutoSubSync option v Settings → Subtitles
- Logy obsahujú "AutoSubSync synchronization"
- Titulky sa úspešne synchronizujú

### 📈 Performance metriky
- Build time: ~2-5 minút
- Startup time: ~30 sekúnd  
- Memory usage: ~500MB (bez sync), ~2GB (počas sync)
- CPU usage: Vysoké počas ML procesingu

### 🎯 Test scenáre
1. **Basic integration test** - Overí dostupnosť dependencies
2. **UI configuration test** - Overí dostupnosť v settings
3. **Real media test** - Test s reálnymi video/subtitle súbormi
4. **Performance test** - Memory a CPU monitoring
5. **Error handling test** - Test s corrupted súbormi

---

## 🏁 Záver / Conclusion

Docker setup poskytuje:
- ✅ Izolované testovanie bez vplyvua na systém
- ✅ Automatickú inštaláciu všetkých dependencies
- ✅ Reprodukovateľné prostredie
- ✅ Jednoduché spustenie jedným príkazom
- ✅ Bezpečné testovanie s reálnymi súbormi

**Ready to test!** 🚀