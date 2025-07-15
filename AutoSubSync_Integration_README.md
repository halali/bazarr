# AutoSubSync Integration for Bazarr

This document describes the integration of AutoSubSync as an alternative subtitle synchronization method in Bazarr.

## Overview

AutoSubSync is a machine learning-based subtitle synchronization tool created by Otto Seiskari (oseiskar) that provides superior accuracy compared to FFSubSync. It combines FPS shift detection with machine learning-based speech detection to achieve excellent synchronization results.

## Features

- **Machine Learning-based Speech Detection**: Uses logistic regression for speech detection instead of WebRTC VAD
- **FPS Shift Detection**: Handles frame rate mismatches automatically
- **High Accuracy**: Typical synchronization accuracy ~0.15 seconds
- **Quality Validation**: Combines optimal FPS shift with highest scoring offset
- **Language Agnostic**: Works with any language in the audio (though primarily tested with English)

## Installation

AutoSubSync requires the following dependencies:
- Python 3.7+
- FFmpeg (required for audio processing)
- NumPy
- SoundFile
- Scipy
- Scikit-learn

To install AutoSubSync:
```bash
pip install autosubsync
```

## Configuration

### Backend Configuration

The AutoSubSync integration adds a new configuration option:

```python
# In bazarr/app/config.py
Validator('subsync.sync_method', must_exist=True, default='ffsubsync', is_type_of=str, 
          is_in=['ffsubsync', 'autosubsync']),
```

### Frontend Configuration

The frontend settings page includes a new selector:

```javascript
// In frontend/src/types/settings.d.ts
interface Subsync {
  use_subsync: boolean;
  use_subsync_threshold: boolean;
  subsync_threshold: number;
  use_subsync_movie_threshold: boolean;
  subsync_movie_threshold: number;
  sync_method: string;  // New option
  // ... other existing options
}
```

## Usage

### Automatic Synchronization

When enabled, AutoSubSync will be used automatically for subtitle synchronization based on the configured sync method:

1. Go to Settings → Subtitles
2. Enable "Automatic Subtitles Audio Synchronization"
3. Select "AutoSubSync" from the "Sync Method" dropdown
4. Configure threshold settings as needed

### Manual Synchronization

AutoSubSync can also be used for manual subtitle synchronization through the subtitle management interface.

## Architecture

### Core Components

1. **AutoSubSyncer Class** (`bazarr/subtitles/tools/autosubsyncer.py`)
   - Main synchronization logic
   - Handles file I/O and error management
   - Integrates with Bazarr's logging and history systems

2. **Integration Layer** (`bazarr/subtitles/sync.py`)
   - Chooses between FFSubSync and AutoSubSync based on configuration
   - Handles progress reporting and error recovery

3. **API Integration** (`bazarr/api/subtitles/subtitles.py`)
   - Supports manual synchronization via REST API
   - Maintains compatibility with existing API endpoints

### Key Features

- **Graceful Degradation**: Falls back to FFSubSync if AutoSubSync is not available
- **Error Handling**: Comprehensive error handling and logging
- **Progress Tracking**: Real-time progress updates in the UI
- **File Type Support**: Supports both SRT and ASS subtitle formats
- **Debug Mode**: Preserves original files when debug mode is enabled

## API Reference

### AutoSubSyncer.sync()

```python
def sync(self, video_path, srt_path, srt_lang, hi, forced,
         sonarr_series_id=None, sonarr_episode_id=None, radarr_id=None):
    """
    Synchronize subtitles using autosubsync library.
    
    Args:
        video_path: Path to the video file
        srt_path: Path to the subtitle file
        srt_lang: Language code for subtitles
        hi: Hearing impaired flag
        forced: Forced subtitles flag
        sonarr_series_id: Sonarr series ID (optional)
        sonarr_episode_id: Sonarr episode ID (optional)
        radarr_id: Radarr movie ID (optional)
    
    Returns:
        ProcessSubtitlesResult object on success, None on failure
    """
```

## Comparison with FFSubSync

| Feature | FFSubSync | AutoSubSync |
|---------|-----------|-------------|
| Speech Detection | WebRTC VAD | Machine Learning (Logistic Regression) |
| Accuracy | ~0.5 seconds | ~0.15 seconds |
| FPS Correction | Golden Section Search | Automatic FPS shift + ML validation |
| Speed | Faster | Slower (~3 minutes for full movie) |
| Memory Usage | Lower | Higher (~1.5GB for full movie) |
| Language Support | Good | Good (tested with fewer languages) |
| Dependency Size | Smaller | Larger (includes ML libraries) |

## Testing

The integration includes comprehensive unit tests:

### AutoSubSyncer Tests (`tests/test_autosubsyncer.py`)
- Initialization and configuration
- FFmpeg availability checks
- Successful synchronization scenarios
- Error handling and edge cases
- File extension preservation
- Debug mode functionality

### Integration Tests (`tests/test_sync_integration.py`)
- Sync method selection
- Threshold-based synchronization
- Progress reporting
- Exception handling
- Episode vs. movie handling

Run tests:
```bash
python -m pytest tests/test_autosubsyncer.py
python -m pytest tests/test_sync_integration.py
```

## Performance Considerations

- AutoSubSync is significantly slower than FFSubSync due to ML processing
- Memory usage is higher (~1.5GB for full-length movies)
- CPU usage is higher during synchronization
- Consider using for high-priority content where accuracy is paramount

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'autosubsync'**
   - Solution: Install autosubsync with `pip install autosubsync`

2. **FFmpeg not found**
   - Solution: Install FFmpeg and ensure it's in the system PATH

3. **Memory errors during synchronization**
   - Solution: Ensure sufficient RAM is available (>2GB recommended)

4. **Slow synchronization**
   - Expected behavior: AutoSubSync prioritizes accuracy over speed

### Debug Mode

Enable debug mode to preserve original files and generate detailed logs:
1. Go to Settings → Subtitles
2. Enable "Debug" under the sync options
3. Check logs for detailed synchronization information

## Dependencies

The following dependencies are added to `requirements.txt`:
```
autosubsync
```

AutoSubSync itself depends on:
- numpy
- soundfile
- scipy
- scikit-learn
- ffmpeg (system dependency)

## License

AutoSubSync is released under the MIT License. This integration maintains compatibility with Bazarr's existing license.

## Credits

- **AutoSubSync**: Otto Seiskari (oseiskar) - https://github.com/oseiskar/autosubsync
- **Integration**: This integration was developed to provide Bazarr users with a higher-accuracy subtitle synchronization option

## Future Enhancements

- **Performance Optimization**: Investigate options for reducing memory usage
- **Additional Configuration**: Expose more AutoSubSync parameters in the UI
- **Batch Processing**: Optimize for processing multiple subtitles efficiently
- **Quality Metrics**: Display synchronization quality scores in the UI