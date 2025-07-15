# coding=utf-8

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, call

from bazarr.subtitles.tools.autosubsyncer import AutoSubSyncer


class TestAutoSubSyncer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.video_path = os.path.join(self.test_dir, 'test_video.mp4')
        self.srt_path = os.path.join(self.test_dir, 'test_subtitles.srt')
        self.ass_path = os.path.join(self.test_dir, 'test_subtitles.ass')
        self.srt_lang = 'en'
        
        # Create dummy files
        with open(self.video_path, 'w') as f:
            f.write('dummy video content')
        with open(self.srt_path, 'w') as f:
            f.write('dummy srt content')
        with open(self.ass_path, 'w') as f:
            f.write('dummy ass content')
        
        self.autosubsyncer = AutoSubSyncer()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    def test_init(self, mock_get_binary):
        """Test AutoSubSyncer initialization"""
        syncer = AutoSubSyncer()
        self.assertIsNone(syncer.reference)
        self.assertIsNone(syncer.srtin)
        self.assertIsNone(syncer.srtout)
        self.assertIsNotNone(syncer.log_dir_path)

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    def test_sync_no_ffmpeg(self, mock_get_binary):
        """Test sync when ffmpeg is not available"""
        mock_get_binary.return_value = None
        
        result = self.autosubsyncer.sync(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            hi=False,
            forced=False
        )
        
        self.assertIsNone(result)

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile')
    def test_sync_autosubsync_not_installed(self, mock_isfile, mock_get_binary):
        """Test sync when autosubsync is not installed"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        mock_isfile.return_value = False
        
        with patch('bazarr.subtitles.tools.autosubsyncer.autosubsync', side_effect=ImportError):
            result = self.autosubsyncer.sync(
                video_path=self.video_path,
                srt_path=self.srt_path,
                srt_lang=self.srt_lang,
                hi=False,
                forced=False
            )
        
        self.assertIsNone(result)

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.remove')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.rename')
    @patch('bazarr.subtitles.tools.autosubsyncer.settings')
    @patch('bazarr.subtitles.tools.autosubsyncer.path_mappings')
    @patch('bazarr.subtitles.tools.autosubsyncer.language_from_alpha2')
    @patch('bazarr.subtitles.tools.autosubsyncer.history_log_movie')
    def test_sync_success_movie(self, mock_history_log, mock_lang_from_alpha2, mock_path_mappings,
                                mock_settings, mock_rename, mock_remove, mock_isfile, mock_get_binary):
        """Test successful sync for movie"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        mock_isfile.side_effect = lambda x: x.endswith('.synced.srt')
        mock_settings.subsync.debug = False
        mock_lang_from_alpha2.return_value = 'English'
        mock_path_mappings.path_replace_reverse_movie.return_value = '/mapped/path'
        
        # Mock autosubsync module
        mock_autosubsync = MagicMock()
        mock_autosubsync.synchronize.return_value = {'success': True}
        
        with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
            result = self.autosubsyncer.sync(
                video_path=self.video_path,
                srt_path=self.srt_path,
                srt_lang=self.srt_lang,
                hi=False,
                forced=False,
                radarr_id=123
            )
        
        self.assertIsNotNone(result)
        mock_autosubsync.synchronize.assert_called_once()
        mock_history_log.assert_called_once()

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.remove')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.rename')
    @patch('bazarr.subtitles.tools.autosubsyncer.settings')
    @patch('bazarr.subtitles.tools.autosubsyncer.path_mappings')
    @patch('bazarr.subtitles.tools.autosubsyncer.language_from_alpha2')
    @patch('bazarr.subtitles.tools.autosubsyncer.history_log')
    def test_sync_success_episode(self, mock_history_log, mock_lang_from_alpha2, mock_path_mappings,
                                  mock_settings, mock_rename, mock_remove, mock_isfile, mock_get_binary):
        """Test successful sync for episode"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        mock_isfile.side_effect = lambda x: x.endswith('.synced.srt')
        mock_settings.subsync.debug = False
        mock_lang_from_alpha2.return_value = 'English'
        mock_path_mappings.path_replace_reverse.return_value = '/mapped/path'
        
        # Mock autosubsync module
        mock_autosubsync = MagicMock()
        mock_autosubsync.synchronize.return_value = {'success': True}
        
        with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
            result = self.autosubsyncer.sync(
                video_path=self.video_path,
                srt_path=self.srt_path,
                srt_lang=self.srt_lang,
                hi=False,
                forced=False,
                sonarr_series_id=456,
                sonarr_episode_id=789
            )
        
        self.assertIsNotNone(result)
        mock_autosubsync.synchronize.assert_called_once()
        mock_history_log.assert_called_once()

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile')
    @patch('bazarr.subtitles.tools.autosubsyncer.settings')
    def test_sync_debug_mode(self, mock_settings, mock_isfile, mock_get_binary):
        """Test sync in debug mode"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        mock_isfile.side_effect = lambda x: x.endswith('.synced.srt')
        mock_settings.subsync.debug = True
        
        # Mock autosubsync module
        mock_autosubsync = MagicMock()
        mock_autosubsync.synchronize.return_value = {'success': True}
        
        with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
            with patch('bazarr.subtitles.tools.autosubsyncer.os.remove') as mock_remove:
                with patch('bazarr.subtitles.tools.autosubsyncer.os.rename') as mock_rename:
                    result = self.autosubsyncer.sync(
                        video_path=self.video_path,
                        srt_path=self.srt_path,
                        srt_lang=self.srt_lang,
                        hi=False,
                        forced=False
                    )
                    
                    # In debug mode, files should not be removed/renamed
                    mock_remove.assert_not_called()
                    mock_rename.assert_not_called()

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    @patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile')
    def test_sync_failed_no_output(self, mock_isfile, mock_get_binary):
        """Test sync when no output file is generated"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        mock_isfile.return_value = False
        
        # Mock autosubsync module
        mock_autosubsync = MagicMock()
        mock_autosubsync.synchronize.return_value = {'success': False}
        
        with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
            result = self.autosubsyncer.sync(
                video_path=self.video_path,
                srt_path=self.srt_path,
                srt_lang=self.srt_lang,
                hi=False,
                forced=False
            )
        
        self.assertIsNone(result)

    @patch('bazarr.subtitles.tools.autosubsyncer.get_binary')
    def test_sync_exception_handling(self, mock_get_binary):
        """Test sync exception handling"""
        mock_get_binary.return_value = '/usr/bin/ffmpeg'
        
        # Mock autosubsync module to raise exception
        mock_autosubsync = MagicMock()
        mock_autosubsync.synchronize.side_effect = Exception("Test exception")
        
        with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
            result = self.autosubsyncer.sync(
                video_path=self.video_path,
                srt_path=self.srt_path,
                srt_lang=self.srt_lang,
                hi=False,
                forced=False
            )
        
        self.assertIsNone(result)

    def test_ass_file_extension(self):
        """Test that ASS files preserve their extension"""
        self.autosubsyncer.srtin = self.ass_path
        expected_output = os.path.splitext(self.ass_path)[0] + '.synced.ass'
        
        with patch('bazarr.subtitles.tools.autosubsyncer.get_binary') as mock_get_binary:
            mock_get_binary.return_value = '/usr/bin/ffmpeg'
            
            # Mock autosubsync module
            mock_autosubsync = MagicMock()
            mock_autosubsync.synchronize.return_value = {'success': True}
            
            with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
                with patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile') as mock_isfile:
                    mock_isfile.return_value = False
                    
                    self.autosubsyncer.sync(
                        video_path=self.video_path,
                        srt_path=self.ass_path,
                        srt_lang=self.srt_lang,
                        hi=False,
                        forced=False
                    )
                    
                    self.assertEqual(self.autosubsyncer.srtout, expected_output)

    def test_srt_file_extension(self):
        """Test that SRT files preserve their extension"""
        self.autosubsyncer.srtin = self.srt_path
        expected_output = os.path.splitext(self.srt_path)[0] + '.synced.srt'
        
        with patch('bazarr.subtitles.tools.autosubsyncer.get_binary') as mock_get_binary:
            mock_get_binary.return_value = '/usr/bin/ffmpeg'
            
            # Mock autosubsync module
            mock_autosubsync = MagicMock()
            mock_autosubsync.synchronize.return_value = {'success': True}
            
            with patch.dict('sys.modules', {'autosubsync': mock_autosubsync}):
                with patch('bazarr.subtitles.tools.autosubsyncer.os.path.isfile') as mock_isfile:
                    mock_isfile.return_value = False
                    
                    self.autosubsyncer.sync(
                        video_path=self.video_path,
                        srt_path=self.srt_path,
                        srt_lang=self.srt_lang,
                        hi=False,
                        forced=False
                    )
                    
                    self.assertEqual(self.autosubsyncer.srtout, expected_output)


if __name__ == '__main__':
    unittest.main()