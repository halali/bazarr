# coding=utf-8

import logging
import os
import gc

from utilities.binaries import get_binary
from radarr.history import history_log_movie
from sonarr.history import history_log
from subtitles.processing import ProcessSubtitlesResult
from languages.get_languages import language_from_alpha2
from utilities.path_mappings import path_mappings
from app.config import settings
from app.get_args import args


class AutoSubSyncer:
    def __init__(self):
        self.reference = None
        self.srtin = None
        self.srtout = None
        self.log_dir_path = os.path.join(args.config_dir, 'log')

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
        """
        self.reference = video_path
        self.srtin = srt_path
        
        # Determine output file extension
        if self.srtin.casefold().endswith('.ass'):
            extension = '.ass'
        else:
            extension = '.srt'
        
        self.srtout = f'{os.path.splitext(self.srtin)[0]}.synced{extension}'
        
        # Check if ffmpeg is available (required by autosubsync)
        ffmpeg_exe = get_binary('ffmpeg')
        if not ffmpeg_exe:
            logging.debug('BAZARR FFmpeg not found! AutoSubSync requires FFmpeg.')
            return
        else:
            logging.debug('BAZARR FFmpeg used is %s', ffmpeg_exe)
        
        try:
            # Import autosubsync - this will fail if not installed
            import autosubsync
            
            # Clean up any existing synced file
            if os.path.isfile(self.srtout):
                os.remove(self.srtout)
                logging.debug('BAZARR deleted the previous subtitles synchronization attempt file.')
            
            # Perform synchronization
            logging.debug('BAZARR starting autosubsync synchronization for: %s', self.srtin)
            
            # Call autosubsync.synchronize() with the video and subtitle paths
            # Based on the documentation, the API is:
            # autosubsync.synchronize(video_file, srt_file, synced_srt_file)
            result = autosubsync.synchronize(
                self.reference,
                self.srtin,
                self.srtout
            )
            
            # Check if synchronization was successful
            if os.path.isfile(self.srtout):
                if not settings.subsync.debug:
                    # Replace original file with synced version
                    os.remove(self.srtin)
                    os.rename(self.srtout, self.srtin)
                
                # Create success message
                # Note: autosubsync doesn't provide detailed offset/framerate info like ffsubsync
                # so we'll provide a generic success message
                message = f"{language_from_alpha2(srt_lang)} subtitles synchronized successfully using AutoSubSync."
                
                # Determine path mapping function
                if sonarr_series_id:
                    prr = path_mappings.path_replace_reverse
                else:
                    prr = path_mappings.path_replace_reverse_movie
                
                # Create result object
                result_obj = ProcessSubtitlesResult(
                    message=message,
                    reversed_path=prr(self.reference),
                    downloaded_language_code2=srt_lang,
                    downloaded_provider=None,
                    score=None,
                    forced=forced,
                    subtitle_id=None,
                    reversed_subtitles_path=prr(self.srtin),
                    hearing_impaired=hi
                )
                
                # Log to history
                if sonarr_episode_id:
                    history_log(action=5, sonarr_series_id=sonarr_series_id, 
                              sonarr_episode_id=sonarr_episode_id, result=result_obj)
                else:
                    history_log_movie(action=5, radarr_id=radarr_id, result=result_obj)
                
                return result_obj
            else:
                logging.error(f'BAZARR AutoSubSync failed to sync subtitles: {self.srtin}')
                return None
                
        except ImportError as e:
            logging.error('BAZARR AutoSubSync library not found. Please install it with: pip install autosubsync')
            logging.debug('Import error details: %s', str(e))
            return None
        except Exception as e:
            logging.exception(f'BAZARR AutoSubSync encountered an error during synchronization: {self.srtin}')
            logging.debug('AutoSubSync error details: %s', str(e))
            return None
        finally:
            # Clean up memory
            gc.collect()