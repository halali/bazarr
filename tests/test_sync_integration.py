# coding=utf-8

import unittest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from bazarr.subtitles.sync import sync_subtitles


class TestSyncIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.video_path = os.path.join(self.test_dir, 'test_video.mp4')
        self.srt_path = os.path.join(self.test_dir, 'test_subtitles.srt')
        self.srt_lang = 'en'
        
        # Create dummy files
        with open(self.video_path, 'w') as f:
            f.write('dummy video content')
        with open(self.srt_path, 'w') as f:
            f.write('dummy srt content')

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    @patch('bazarr.subtitles.sync.settings')
    def test_sync_disabled(self, mock_settings):
        """Test sync when subsync is disabled"""
        mock_settings.subsync.use_subsync = False
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50
        )
        
        self.assertFalse(result)

    @patch('bazarr.subtitles.sync.settings')
    def test_sync_forced_subtitles(self, mock_settings):
        """Test sync with forced subtitles (should be skipped)"""
        mock_settings.subsync.use_subsync = True
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=True,
            hi=False,
            percent_score=50
        )
        
        self.assertFalse(result)

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.AutoSubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_autosubsync_success(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                      mock_autosubsyncer_class, mock_settings):
        """Test successful sync with autosubsync"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = False
        mock_settings.subsync.sync_method = 'autosubsync'
        
        mock_autosubsyncer = MagicMock()
        mock_autosubsyncer_class.return_value = mock_autosubsyncer
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50
        )
        
        self.assertTrue(result)
        mock_autosubsyncer_class.assert_called_once()
        mock_autosubsyncer.sync.assert_called_once()
        mock_show_progress.assert_called()
        mock_gc.collect.assert_called_once()

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.SubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_ffsubsync_success(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                    mock_subsyncer_class, mock_settings):
        """Test successful sync with ffsubsync"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = False
        mock_settings.subsync.sync_method = 'ffsubsync'
        mock_settings.subsync.max_offset_seconds = 60
        mock_settings.subsync.no_fix_framerate = True
        mock_settings.subsync.gss = True
        
        mock_subsyncer = MagicMock()
        mock_subsyncer_class.return_value = mock_subsyncer
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50
        )
        
        self.assertTrue(result)
        mock_subsyncer_class.assert_called_once()
        mock_subsyncer.sync.assert_called_once()
        mock_show_progress.assert_called()
        mock_gc.collect.assert_called_once()

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.AutoSubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_autosubsync_exception(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                        mock_autosubsyncer_class, mock_settings):
        """Test sync with autosubsync when exception occurs"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = False
        mock_settings.subsync.sync_method = 'autosubsync'
        
        mock_autosubsyncer = MagicMock()
        mock_autosubsyncer.sync.side_effect = Exception("Test exception")
        mock_autosubsyncer_class.return_value = mock_autosubsyncer
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50
        )
        
        self.assertTrue(result)
        mock_hide_progress.assert_called()
        mock_gc.collect.assert_called_once()

    @patch('bazarr.subtitles.sync.settings')
    def test_sync_threshold_skip_episode(self, mock_settings):
        """Test sync threshold skip for episodes"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = True
        mock_settings.subsync.subsync_threshold = 80
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=85,  # Above threshold
            sonarr_episode_id=123
        )
        
        self.assertFalse(result)

    @patch('bazarr.subtitles.sync.settings')
    def test_sync_threshold_skip_movie(self, mock_settings):
        """Test sync threshold skip for movies"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_movie_threshold = True
        mock_settings.subsync.subsync_movie_threshold = 70
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=75,  # Above threshold
            radarr_id=456
        )
        
        self.assertFalse(result)

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.AutoSubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_with_episode_ids(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                   mock_autosubsyncer_class, mock_settings):
        """Test sync with episode IDs"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = False
        mock_settings.subsync.sync_method = 'autosubsync'
        
        mock_autosubsyncer = MagicMock()
        mock_autosubsyncer_class.return_value = mock_autosubsyncer
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50,
            sonarr_series_id=123,
            sonarr_episode_id=456
        )
        
        self.assertTrue(result)
        
        # Check that the sync was called with episode IDs
        call_args = mock_autosubsyncer.sync.call_args
        self.assertEqual(call_args[1]['sonarr_series_id'], 123)
        self.assertEqual(call_args[1]['sonarr_episode_id'], 456)

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.AutoSubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_with_movie_id(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                mock_autosubsyncer_class, mock_settings):
        """Test sync with movie ID"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_movie_threshold = False
        mock_settings.subsync.sync_method = 'autosubsync'
        
        mock_autosubsyncer = MagicMock()
        mock_autosubsyncer_class.return_value = mock_autosubsyncer
        
        result = sync_subtitles(
            video_path=self.video_path,
            srt_path=self.srt_path,
            srt_lang=self.srt_lang,
            forced=False,
            hi=False,
            percent_score=50,
            radarr_id=789
        )
        
        self.assertTrue(result)
        
        # Check that the sync was called with movie ID
        call_args = mock_autosubsyncer.sync.call_args
        self.assertEqual(call_args[1]['radarr_id'], 789)

    @patch('bazarr.subtitles.sync.settings')
    @patch('bazarr.subtitles.sync.AutoSubSyncer')
    @patch('bazarr.subtitles.sync.show_progress')
    @patch('bazarr.subtitles.sync.hide_progress')
    @patch('bazarr.subtitles.sync.gc')
    def test_sync_default_method(self, mock_gc, mock_hide_progress, mock_show_progress, 
                                 mock_autosubsyncer_class, mock_settings):
        """Test sync when sync_method is not configured (should default to ffsubsync)"""
        mock_settings.subsync.use_subsync = True
        mock_settings.subsync.use_subsync_threshold = False
        mock_settings.subsync.max_offset_seconds = 60
        mock_settings.subsync.no_fix_framerate = True
        mock_settings.subsync.gss = True
        
        # Mock getattr to return None (attribute not found)
        with patch('bazarr.subtitles.sync.getattr', return_value='ffsubsync'):
            with patch('bazarr.subtitles.sync.SubSyncer') as mock_subsyncer_class:
                mock_subsyncer = MagicMock()
                mock_subsyncer_class.return_value = mock_subsyncer
                
                result = sync_subtitles(
                    video_path=self.video_path,
                    srt_path=self.srt_path,
                    srt_lang=self.srt_lang,
                    forced=False,
                    hi=False,
                    percent_score=50
                )
                
                self.assertTrue(result)
                mock_subsyncer_class.assert_called_once()
                mock_autosubsyncer_class.assert_not_called()


if __name__ == '__main__':
    unittest.main()