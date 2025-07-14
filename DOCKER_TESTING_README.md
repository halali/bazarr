# 🐳 Docker Testing - AutoSubSync Integration

## 🚀 Rýchly štart

```bash
# 1. Udeľ spúšťacie práva test scriptu
chmod +x docker-test.sh

# 2. Spusti test
./docker-test.sh
```

**To je všetko!** Script automaticky:
- Vytvorí Docker image s AutoSubSync
- Spustí Bazarr v kontajneri
- Otestuje, že všetko funguje
- Otvorí Bazarr v prehliadači na `http://localhost:6767`

## 📋 Čo sa testuje

✅ **AutoSubSync inštalácia** - Overí, že autosubsync knižnica je nainštalovaná  
✅ **FFmpeg dostupnosť** - Skontroluje, že FFmpeg je k dispozícii  
✅ **Bazarr spustenie** - Bazarr sa úspešne spustí  
✅ **API funkčnosť** - Bazarr API odpovedá  
✅ **AutoSubSync integrácia** - AutoSubSyncer trieda sa importuje  
✅ **UI dostupnosť** - Web interface je prístupný  

## 🎯 Manuálne testovanie

Po spustení `./docker-test.sh`:

1. **Otvor Bazarr:** http://localhost:6767
2. **Choď do Settings → Subtitles**
3. **Zapni** "Automatic Subtitles Audio Synchronization"
4. **Vyber** "AutoSubSync" z "Sync Method" dropdown
5. **Ulož nastavenia**

### Test s reálnymi súbormi:
```bash
# Skopíruj svoje video a subtitle súbory do test-media/
cp /path/to/your/movie.mp4 test-media/
cp /path/to/your/movie.srt test-media/

# Bazarr ich uvidí v /test-media/ adresári
```

## 📁 Štruktúra súborov

```
workspace/
├── Dockerfile.autosubsync          # Docker image pre testovanie
├── docker-compose.autosubsync.yml  # Docker Compose konfigurácia
├── docker-test.sh                  # Automatický test script
├── docker-data/                    # Perzistentné dáta
│   ├── config/                     # Bazarr konfigurácia
│   ├── logs/                       # Logy
│   ├── movies/                     # Movies directory
│   └── tv/                         # TV shows directory
└── test-media/                     # Test médiá
    ├── test_movie.mp4              # Auto-generovaný test video
    └── test_movie.srt              # Auto-generovaný test titulky
```

## 🔧 Užitočné príkazy

### Základné Docker operácie:
```bash
# Spusti kontajnery
docker-compose -f docker-compose.autosubsync.yml up -d

# Pozri logy
docker-compose -f docker-compose.autosubsync.yml logs -f bazarr-autosubsync

# Zastav kontajnery
docker-compose -f docker-compose.autosubsync.yml down

# Zmaž všetko (vrátane volumes)
docker-compose -f docker-compose.autosubsync.yml down -v
docker rmi $(docker images -q "*autosubsync*")
```

### Debugging v kontajneri:
```bash
# Vstúp do kontajnera
docker exec -it bazarr-autosubsync-test bash

# Test AutoSubSync v kontajneri
docker exec -it bazarr-autosubsync-test python3 -c "
import autosubsync
print('AutoSubSync:', autosubsync.__version__)
"

# Test Bazarr integrácie
docker exec -it bazarr-autosubsync-test python3 -c "
import sys
sys.path.append('/app/bazarr')
from bazarr.subtitles.tools.autosubsyncer import AutoSubSyncer
print('AutoSubSyncer import OK')
"
```

### Monitoring:
```bash
# CPU a pamäť
docker stats bazarr-autosubsync-test

# Procesy v kontajneri
docker exec bazarr-autosubsync-test ps aux
```

## 🌐 Prístupy

| Služba | URL | Popis |
|--------|-----|-------|
| Bazarr | http://localhost:6767 | Hlavný Bazarr interface |
| Health Check | http://localhost:6767/api/system/status | API status |
| Test Media | http://localhost:8080 | Nginx server s test súbormi |

## 🐛 Troubleshooting

### Problém: Kontajner sa nespustí
```bash
# Pozri logy
docker-compose -f docker-compose.autosubsync.yml logs bazarr-autosubsync

# Skontroluj resources
docker system df
docker system prune  # Vyčisti nepoužívané resources
```

### Problém: AutoSubSync nie je dostupný
```bash
# Zkontroluj inštaláciu v kontajneri
docker exec bazarr-autosubsync-test pip list | grep autosubsync

# Reinstall ak treba
docker exec bazarr-autosubsync-test pip install --upgrade autosubsync
```

### Problém: FFmpeg nefunguje
```bash
# Test FFmpeg v kontajneri
docker exec bazarr-autosubsync-test ffmpeg -version

# Skontroluj system packages
docker exec bazarr-autosubsync-test apt list --installed | grep ffmpeg
```

### Problém: Port 6767 je obsadený
```bash
# Skontroluj čo používa port
lsof -i :6767

# Zmeň port v docker-compose.autosubsync.yml
# ports:
#   - "6768:6767"  # Použij iný port
```

## 📊 Performance monitoring

### Pamäť a CPU počas sync:
```bash
# Sleduj resources počas synchronizácie
watch -n 1 'docker stats bazarr-autosubsync-test --no-stream'
```

### Logy synchronizácie:
```bash
# Sleduj AutoSubSync aktivity
docker exec bazarr-autosubsync-test tail -f /logs/bazarr.log | grep -i autosubsync
```

## 🎛️ Konfigurácia

### Environment variables:
```yaml
# V docker-compose.autosubsync.yml
environment:
  - PUID=1000              # User ID
  - PGID=1000              # Group ID  
  - TZ=Europe/Bratislava   # Timezone
  - BAZARR_CONFIG_DIR=/config
  - BAZARR_LOG_DIR=/logs
```

### Volumes:
```yaml
volumes:
  - ./docker-data/config:/config      # Bazarr config
  - ./docker-data/logs:/logs          # Logy
  - ./test-media:/test-media           # Test súbory
  # Pridaj svoje média:
  - /your/movies:/movies
  - /your/tv:/tv
```

## 🧹 Cleanup

### Kompletné vyčistenie:
```bash
# Zastav a zmaž kontajnery
docker-compose -f docker-compose.autosubsync.yml down -v

# Zmaž image
docker rmi $(docker images "*autosubsync*" -q)

# Zmaž test dáta (voliteľné)
rm -rf docker-data/ test-media/
```

## 🎉 Úspešný test

Ak vidíš toto, všetko funguje:

```
🎉 AutoSubSync integration test completed successfully!

📋 Test Results:
✅ Docker containers are running
✅ Bazarr is accessible at http://localhost:6767
✅ AutoSubSync library is installed
✅ FFmpeg is available
✅ AutoSubSync integration class is working
✅ Test media server at http://localhost:8080
```

**Môžeš teraz testovať AutoSubSync v Bazarr na http://localhost:6767** 🚀