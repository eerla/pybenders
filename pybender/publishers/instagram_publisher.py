"""
Instagram Video Uploader using instagrapi.

Follows best practices from:
https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html

Features:
- Session persistence to avoid repeated logins (never logs out manually)
- Automatic retry logic with delays
- Proper error handling and logging
- Random delays to mimic real user behavior
- Optional proxy support
"""
import logging
import shutil
import time
import json
import os
import sys
import random
import glob
from pathlib import Path
from typing import Optional, Dict, Any
from pybender.publishers.subject_captions import SUBJECT_CAPTIONS
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientError

logger = logging.getLogger("InstagramVideoUploader")


    
class InstagramVideoUploader:
    """
    Uploads videos (Reels) to Instagram following best practices.
    
    Best practices implemented:
    1. Session persistence - avoid repeated logins (never logs out manually)
    2. Delay ranges - mimic real user behavior
    3. Proxy support - optional IP rotation
    4. Error handling and logging
    5. Session validation before upload
    """
    
    def __init__(
        self,
        username: str = "YOUR_INSTAGRAM_USERNAME",
        password: str = "YOUR_INSTAGRAM_PASSWORD",
        profile_username: Optional[str] = None,
        session_file: Optional[Path] = None,
        proxy: Optional[str] = None,
        delay_range: list = [3, 6]
        ):
        """
        Initialize Instagram video uploader.
        
        Args:
            username: Instagram login username/email (placeholder by default)
            password: Instagram password (placeholder by default)
            profile_username: Instagram handle to use for profile/validation calls
            session_file: Path to store/load session JSON file (auto-generated if None)
            proxy: Optional proxy URL (e.g., "http://proxy:9137")
            delay_range: [min, max] delay in seconds between requests
                        Helps mimic real user behavior
        
        Example:
            uploader = InstagramVideoUploader(
                username="your_username",
                password="your_password",
                proxy="http://your_proxy:9137",
                delay_range=[2, 5]
            )
        """
        self.username = username
        # Use explicit profile handle if provided; otherwise fall back to login username
        self.profile_username = profile_username or username
        self.password = password
        
        # Generate username-specific session file if not provided
        if session_file is None:
            safe_username = username.replace('@', '_at_').replace('.', '_')
            session_file = Path(f"sessions/instagram_session_{safe_username}.json")
        
        self.session_file = Path(session_file)
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.proxy = proxy
        self.delay_range = delay_range
        
        # Initialize client
        self.cl = Client()
        
        # Set delays to mimic real user behavior
        self.cl.delay_range = delay_range
        
        # Subject-specific captions with relevant hashtags
        self.subject_captions = SUBJECT_CAPTIONS
        
        # Generic fallback captions for unknown subjects
        self.generic_captions = [
            "Can you crack this in 30 seconds? 🚀 #CodeChallenge #Programming",
            "Think you've got the answer? Prove it. ⚡ #DevQuiz #Coding",
            "One quick puzzle: what's your move? 🤔 #CodeChallenge #Programming",
            "Your turn—solve it before the timer ends. 🎯 #CodingQuiz #Tech",
            "Pause, solve, flex your brain. 🧠 #CodeChallenge #Programming"
        ]
        
        # Set proxy if provided
        if proxy:
            self._set_proxy(proxy)
        
        logger.info(
            f"Initialized InstagramVideoUploader for user: {username}"
            f" (profile: {self.profile_username})"
        )
        logger.info(f"Session file: {self.session_file}")
    
    def _set_proxy(self, proxy: str) -> None:
        """
        Set proxy for the client.
        
        Args:
            proxy: Proxy URL (e.g., "http://proxy:9137")
        """
        try:
            self.cl.set_proxy(proxy)
            logger.info(f"Proxy set to: {proxy}")
        except Exception as e:
            logger.error(f"Failed to set proxy: {e}")
            raise
    
    def _save_session(self) -> bool:
        """
        Save current session to file for later use.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cl.dump_settings(str(self.session_file))
            logger.info(f"Session saved to: {self.session_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False
    
    def _load_session(self) -> bool:
        """
        Load session from file if it exists.
        
        Returns:
            True if session loaded successfully, False otherwise
        """
        if not self.session_file.exists():
            logger.debug(f"Session file not found: {self.session_file}")
            return False
        
        try:
            session = self.cl.load_settings(str(self.session_file))
            self.cl.set_settings(session)
            logger.info(f"Session loaded from: {self.session_file}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            # Delete corrupted session file
            try:
                self.session_file.unlink()
                logger.info(f"Deleted corrupted session file: {self.session_file}")
            except:
                pass
            return False
    
    def _validate_session(self) -> bool:
        """
        Validate if current session is still active using lightweight operation.
        Uses user_info_by_username (lighter) instead of get_timeline_feed (heavier).
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Use lightweight user info lookup to validate session
            # This is less likely to trigger rate limits than timeline fetch
            self.cl.user_info_by_username(self.profile_username)
            logger.debug("✓ Session validation successful")
            return True
        except LoginRequired:
            logger.warning("Session is no longer valid (LoginRequired)")
            return False
        except Exception as e:
            error_str = str(e)
            # Check for explicit logout indicators
            if "user_has_logged_out" in error_str or "logout_reason" in error_str:
                logger.warning(f"Session logged out by Instagram: {e}")
                return False
            # For other errors, assume session might still be valid to avoid re-logins
            logger.debug(f"Session validation inconclusive (assuming valid): {e}")
            return True  # Give benefit of doubt
    
    def _clear_session(self) -> None:
        """
        Completely clear the session from memory and disk.
        """
        try:
            # Clear in-memory session
            self.cl.settings = {}
            self.cl.auth = None
            
            # Delete session file
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info(f"Cleared session from disk: {self.session_file}")
        except Exception as e:
            logger.warning(f"Error clearing session: {e}")
    
    def _get_caption(self, subject: str, question_title: str = "") -> str:
        """
        Generate a caption for Instagram post using subject-specific options.
        
        Args:
            subject: Programming subject/language
            question_title: Optional question title to include in caption
            
        Returns:
            Generated caption string
        """
        # Get captions for subject, fallback to python if not found
        captions = self.subject_captions.get(subject, self.subject_captions.get("python", []))
        
        if not captions:
            return f"Daily Dose of {subject.replace('_', ' ').title()}"
        
        # Pick a random caption
        caption = random.choice(captions)
        
        # Include question title if provided
        if question_title:
            caption = f"{question_title}\n\n{caption}"
        
        return caption
    
    def _human_delay(self, min_sec: float = 2.0, max_sec: float = 5.0) -> None:
        """
        Add a random delay to mimic human behavior.
        
        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds
        """
        delay = random.uniform(min_sec, max_sec)
        logger.debug(f"⏳ Human-like delay: {delay:.2f}s")
        time.sleep(delay)
    
    def _warmup_session(self) -> bool:
        """
        Perform lightweight discovery actions before uploading to appear human-like.
        
        This reduces bot detection risk by:
        - Researching hashtags (appears content-aware)
        
        NOTE: Skips profile lookup (instagrapi may use email) and suggestions
        (method may be unavailable on some builds).
        
        Returns:
            True if warmup succeeded or was skipped
        """
        logger.info("🔥 Warming up session with discovery actions...")
        
        # Decide which actions to perform (randomize for natural behavior)
        actions = ['hashtags']
        selected_actions = ['hashtags']  # Always run hashtag research (safest)
        
        success_count = 0
        
        # Action 1: Get hashtag info for common programming tags
        if 'hashtags' in selected_actions:
            try:
                self._human_delay(1.0, 2.0)
                hashtags = ['coding', 'programming', 'python', 'webdev']
                chosen_tag = random.choice(hashtags)
                tag_info = self.cl.hashtag_info(chosen_tag)
                logger.debug(f"✓ Researched #{chosen_tag}: {tag_info.media_count} posts")
                success_count += 1
            except Exception as e:
                logger.warning(f"⚠️  Could not retrieve hashtag info: {e}")
                # Don't fail - continue with upload
        
        logger.info(f"✅ Session warmup complete ({success_count}/{len(selected_actions)} actions successful)")
        return True
    
    def login(self) -> bool:
        """
        Login to Instagram with proper session persistence (instagrapi best practices).
        
        Strategy:
        1. Try to load saved session from file
        2. Wait 1s, then validate session with lightweight operation
        3. If validation passes, session is ready
        4. If validation fails, wait 3s then attempt fresh login
        5. After fresh login, wait 3s before saving session
        
        This approach:
        - Minimizes aggressive re-login attempts that trigger Instagram security
        - Uses lightweight validation (user_info_by_username not timeline fetch)
        - Includes strategic delays to avoid rate limiting
        - Reuses saved sessions across multiple runs
        - Never logs out manually (let session expire naturally)
        
        Returns:
            True if login successful, False otherwise
        """
        # Check for username/password placeholders
        if self.username == "YOUR_INSTAGRAM_USERNAME" or self.password == "YOUR_INSTAGRAM_PASSWORD":
            logger.error(
                "Please set actual Instagram credentials. "
                "Update username and password in the InstagramVideoUploader initialization."
            )
            return False
        
        # Try to use saved session first (preferred)
        if self._load_session():
            logger.info(f"✓ Loaded saved session for {self.username}")
            time.sleep(random.uniform(0.8, 1.5))  # Random delay before validation
            
            if self._validate_session():
                logger.info(f"✓ Session validation passed - reusing saved session")
                return True
            else:
                logger.warning(f"✗ Saved session invalid - will attempt fresh login")
                self._clear_session()
                time.sleep(random.uniform(2.5, 4.0))  # Random delay before fresh login
        else:
            logger.info(f"No saved session found at {self.session_file}")
            
        # Fresh login with credentials when no valid saved session
        try:
            logger.info(f"→ Performing fresh login as {self.username}...")
            
            # Ensure clean client state
            self._clear_session()
            time.sleep(random.uniform(0.8, 1.5))
            
            # Perform login
            self.cl.login(self.username, self.password)
            logger.info(f"✓ Fresh login successful")
            
            # Random delay after login before saving session
            time.sleep(random.uniform(2.5, 4.0))
            
            # Save session for future runs
            if self._save_session():
                logger.info(f"✓ Session persisted to file for future use")
                return True
            else:
                logger.warning("✗ Failed to save session, but login was successful")
                return True  # Login succeeded even if save failed
        
        except ClientError as e:
            # More specific error handling for Instagram API errors
            error_msg = str(e)
            if "challenge_required" in error_msg:
                logger.error(f"✗ Login failed: Account requires security challenge (2FA/verification)")
                logger.error(f"   Please log in via Instagram app/web first to complete verification")
            elif "Please wait a few minutes" in error_msg or "rate limit" in error_msg.lower():
                logger.error(f"✗ Login failed: Rate limited by Instagram. Wait 10-15 minutes and try again")
            elif "The password you entered is incorrect" in error_msg:
                logger.error(f"✗ Login failed: Incorrect password")
            elif "The username you entered" in error_msg:
                logger.error(f"✗ Login failed: Username not found")
            else:
                logger.error(f"✗ Login failed: {error_msg}")
            
            self._clear_session()
            return False

        except Exception as e:
            logger.error(f"✗ Login failed: {e}")
            logger.error(f"   This could be due to: incorrect credentials, 2FA required, or account restrictions")
            self._clear_session()
            return False
    
    def upload_reel(
        self,
        video_path: str,
        caption: str = "",
        thumbnail_path: Optional[str] = None,
        use_custom_thumbnail: bool = False,
        subject: str = "python"
        ) -> bool:
        """
        Upload a video as Instagram Reel (single attempt, no retries).
        
        Args:
            video_path: Path to video file (MP4, MOV, etc.)
            caption: Caption text for the reel (if empty, auto-generated from subject)
            thumbnail_path: Custom thumbnail image path (optional)
            use_custom_thumbnail: If True, use custom thumbnail. If False, auto-generate (safer).
                                 Note: Custom thumbnails may cause validation errors.
            subject: Subject/topic for caption selection (python, sql, javascript, etc.)
        
        Returns:
            True if upload successful, False otherwise
        """
        video_path = Path(video_path)
        
        # Auto-generate caption from subject if not provided
        if not caption:
            captions = self.subject_captions.get(subject, self.generic_captions)
            caption = random.choice(captions)
            logger.debug(f"Using {subject} caption: {caption[:60]}...")
        
        # Validate video file exists
        if not video_path.exists():
            logger.error(f"❌ Video file not found: {video_path}")
            return False
        
        if not video_path.is_file():
            logger.error(f"❌ Invalid video path (not a file): {video_path}")
            return False
        
        # Validate supported video format
        supported_formats = {'.mp4', '.mov', '.avi', '.mkv'}
        if video_path.suffix.lower() not in supported_formats:
            logger.warning(
                f"⚠️  Unsupported video format: {video_path.suffix}. "
                f"Supported: {supported_formats}"
            )
        
        # Validate custom thumbnail if provided
        if use_custom_thumbnail and thumbnail_path:
            thumbnail_path = Path(thumbnail_path)
            if not thumbnail_path.exists():
                logger.warning(f"⚠️  Thumbnail file not found: {thumbnail_path}, using auto-generated")
                use_custom_thumbnail = False
        
        logger.info(f"Starting reel upload: {video_path.name}")
        logger.info(f"Caption: {caption[:80]}...")
        
        # Human-like delay before upload
        self._human_delay(1.5, 3.5)
        
        try:
            if use_custom_thumbnail and thumbnail_path:
                # Use custom thumbnail (may cause validation errors)
                logger.info("⚠️  Using custom thumbnail (may cause validation errors)...")
                media = self.cl.clip_upload(
                    path=str(video_path),
                    caption=caption,
                    thumbnail=str(thumbnail_path)
                )
            else:
                # Auto-generate thumbnail (safer)
                logger.debug("Uploading with auto-generated thumbnail (safest option)...")
                media = self.cl.clip_upload(
                    path=str(video_path),
                    caption=caption
                )
            
            logger.info(f"✓ Successfully uploaded reel: {media.pk}")
            logger.info(f"✓ Reel URL: https://www.instagram.com/reel/{media.code}/")
            return True
            
        except ValueError as e:
            error_msg = str(e)
            if "audio_filter_infos" in error_msg:
                # This is a known instagrapi bug - reel was already created despite validation error
                logger.warning(
                    "⚠️  Pydantic validation error (audio_filter_infos) - known instagrapi bug. "
                    "✓ Reel may still be uploaded. Check your Instagram account."
                )
                return True  # Consider it success since reel was likely created
            else:
                logger.error(f"❌ Validation error: {e}")
                return False
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Upload failed: {error_msg}")
            
            if "user_has_logged_out" in error_msg:
                logger.warning("Session was logged out. You may need to re-login.")
            
            return False
    
    def upload_carousel(
        self,
        image_paths: list,
        caption: str = "",
        subject: str = "",
        retries: int = 3
        ) -> bool:
        """
        Upload multiple images as a carousel post.
        
        Args:
            image_paths: List of image file paths (PNG, JPG, etc.)
            caption: Caption text for the carousel
            subject: Subject for auto-generating caption if caption is empty
            retries: Number of retry attempts on failure
        
        Returns:
            True if upload successful, False otherwise
        """
        # Auto-generate caption from subject if not provided
        if not caption:
            captions = self.subject_captions.get(subject, self.generic_captions)
            caption = random.choice(captions)
            logger.debug(f"Using {subject} caption: {caption[:60]}...")
            
        # Validate all image files exist
        image_paths = [Path(img) for img in image_paths]
        
        for img_path in image_paths:
            if not img_path.exists():
                logger.error(f"Image file not found: {img_path}")
                return False
        
        logger.info(f"Starting carousel upload with {len(image_paths)} images")
        logger.info(f"Caption: {caption[:100]}...")
        
        # Retry loop
        for attempt in range(1, retries + 1):
            try:
                # Re-validate session before upload
                if not self._validate_session():
                    logger.warning("Session invalid before upload, attempting re-login")
                    if not self.login():
                        logger.error("Failed to re-login")
                        continue
                
                logger.info(f"Upload attempt {attempt}/{retries}")
                
                # Human-like delay before upload
                self._human_delay(1.5, 3.5)
                
                # Upload carousel
                media = self.cl.album_upload(
                    paths=[str(img) for img in image_paths],
                    caption=caption
                )
                
                logger.info(f"Successfully uploaded carousel: {media.pk}")
                logger.info(f"Post URL: https://www.instagram.com/p/{media.code}/")
                
                return True
                
            except Exception as e:
                logger.error(f"Upload attempt {attempt} failed: {e}")
                
                if attempt < retries:
                    delay = random.uniform(2 ** attempt, 2 ** attempt + 5)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} upload attempts failed")
        
        return False
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current account information.
        
        Returns:
            Account info dictionary or None if failed
        """
        try:
            account = self.cl.account_info()
            return {
                "username": getattr(account, 'username', 'N/A'),
                "pk": getattr(account, 'pk', 'N/A'),
                "full_name": getattr(account, 'full_name', 'N/A'),
                "biography": getattr(account, 'biography', 'N/A'),
                "follower_count": getattr(account, 'follower_count', 0),
                "following_count": getattr(account, 'following_count', 0),
            }
        except Exception as e:
            logger.error(f"⚠️  Failed to get account info: {e}")
            return None


def move_uploaded_files(
    carousel_data: Dict[str, Any],
    reel_data: list,
    uploaded_carousels: list,
    uploaded_reels: list,
    subject: str,
    run_date: str,
    project_root: Path
    ) -> Dict[str, Any]:
    """
    Move successfully uploaded files to organized folders.
    
    Args:
        carousel_data: Dictionary mapping question_id to carousel data with paths
        reel_data: List of dictionaries with reel video data
        uploaded_carousels: List of successfully uploaded carousel question IDs
        uploaded_reels: List of successfully uploaded reel video paths
        subject: Subject name (e.g., 'python', 'sql')
        run_date: Run date string (e.g., '2026-01-01_205914')
        project_root: Project root path
    
    Returns:
        Dictionary with move operation results
    """
    results = {
        'carousels_moved': 0,
        'reels_moved': 0,
        'errors': []
    }
    
    # Setup target directories
    uploaded_root = project_root / "uploaded" / subject / run_date
    carousel_dir = uploaded_root / "carousels"
    reel_dir = uploaded_root / "reels"
    
    try:
        carousel_dir.mkdir(parents=True, exist_ok=True)
        reel_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created upload directories: {uploaded_root}")
    except Exception as e:
        error_msg = f"Failed to create upload directories: {e}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        return results
    
    # Move successfully uploaded carousel images
    logger.info("📦 Moving uploaded carousel images...")
    for question_id in uploaded_carousels:
        if question_id not in carousel_data:
            continue
        
        try:
            carousel_info = carousel_data[question_id]
            image_paths = carousel_info['paths']
            
            # Create question-specific subfolder
            question_folder = carousel_dir / question_id
            question_folder.mkdir(parents=True, exist_ok=True)
            
            # Move all 6 carousel images
            for img_path in image_paths:
                try:
                    target_path = question_folder / img_path.name
                    shutil.move(str(img_path), str(target_path))
                    logger.debug(f"  ✓ Moved: {img_path.name} -> {question_folder.name}/")
                except Exception as e:
                    error_msg = f"Failed to move {img_path.name}: {e}"
                    logger.warning(f"  ⚠️  {error_msg}")
                    results['errors'].append(error_msg)
            
            results['carousels_moved'] += 1
            logger.info(f"  ✓ Moved carousel for {question_id}")
            
        except Exception as e:
            error_msg = f"Failed to move carousel {question_id}: {e}"
            logger.error(f"  ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    # Move successfully uploaded reel videos
    logger.info("📦 Moving uploaded reel videos...")
    for reel_path_str in uploaded_reels:
        try:
            reel_path = Path(reel_path_str)
            if not reel_path.exists():
                logger.warning(f"  ⚠️  Reel file not found (already moved?): {reel_path.name}")
                continue
            
            target_path = reel_dir / reel_path.name
            shutil.move(str(reel_path), str(target_path))
            logger.info(f"  ✓ Moved: {reel_path.name}")
            results['reels_moved'] += 1
            
        except Exception as e:
            error_msg = f"Failed to move reel {Path(reel_path_str).name}: {e}"
            logger.error(f"  ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    logger.info(f"📦 Move summary: {results['carousels_moved']} carousels, {results['reels_moved']} reels moved")
    if results['errors']:
        logger.warning(f"⚠️  {len(results['errors'])} errors occurred during move operations")
    
    return results


def upload_from_metadata(
    metadata_file_path: Path,
    username: str,
    password: str,
    profile_username: Optional[str] = None,
    session_dir: Optional[Path] = None,
    delay_between_uploads: int = 12
    ) -> Dict[str, Any]:
    """
    Unified function to upload both carousels and reels from metadata file to Instagram.
    
    Collects all carousel and reel image paths from metadata, then uploads both with delay.
    
    Args:
        metadata_file_path: Path to the metadata JSON file
        username: Instagram username
        password: Instagram password
        session_dir: Optional directory for session files (defaults to project_root/sessions)
        delay_between_uploads: Delay in seconds between carousel and reel uploads (default: 12)
    
    Returns:
        Dictionary with combined upload results
    """
    metadata_file_path = Path(metadata_file_path).resolve()
    logger.info(f"📤 Starting unified upload from: {metadata_file_path}")
    
    # Extract run_date from metadata filename (e.g., "2026-01-01_205914_metadata.json" -> "2026-01-01_205914")
    run_date = metadata_file_path.stem.replace('_metadata', '')
    logger.info(f"📅 Run date: {run_date}")
    
    # Setup paths
    project_root = metadata_file_path.parent.parent.parent.parent
    if session_dir is None:
        session_dir = project_root / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # Use username-specific session filename to support multiple accounts
    safe_username = username.replace('@', '_at_').replace('.', '_')
    session_file = session_dir / f"instagram_session_{safe_username}.json"

    logger.info(f"📂 Session file: {session_file}")
        
    # Load metadata
    try:
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load metadata file: {e}")
        return {
            'success': False,
            'carousel': {'uploaded_count': 0, 'failed_count': 0, 'uploaded': [], 'failed': []},
            'reel': {'uploaded_count': 0, 'failed_count': 0, 'uploaded': [], 'failed': []},
            'total_uploaded': 0,
            'total_failed': 0,
            'error': str(e)
        }
    
    # Collect carousel images
    carousel_images_by_question = {}
    reel_videos_with_metadata = []
    questions = metadata.get('questions', [])
    subject = metadata.get('subject', 'programming')
    
    for q in questions:
        question_id = q.get('question_id')
        title = q.get('title', '')
        content = q.get('content', {})
        assets = q.get('assets', {})
        carousel_images = assets.get('carousel_images', [])
        
        if carousel_images:
            # Resolve paths relative to project root
            valid_carousel_paths = []
            for img in carousel_images:
                img_path = project_root / img if not Path(img).is_absolute() else Path(img)
                if img_path.exists():
                    valid_carousel_paths.append(img_path.resolve())
                else:
                    logger.warning(f"Carousel image not found: {img_path}")
            
            if len(valid_carousel_paths) == 6:  # Need all 6 slides
                carousel_images_by_question[question_id] = {
                    'paths': valid_carousel_paths,
                    'title': title,
                    'subject': subject
                }
            else:
                logger.warning(f"Question {question_id}: expected 6 carousel images, found {len(valid_carousel_paths)}")
        
        # Collect reel video with metadata
        video_path = assets.get('combined_reel')
        question_image = assets.get('reel', {}).get('question_image')  # Thumbnail for reel (nested under reel)
        
        if video_path:
            vid_path = project_root / video_path if not Path(video_path).is_absolute() else Path(video_path)
            if vid_path.exists():
                # Resolve thumbnail path if available
                thumbnail_path = None
                if question_image:
                    thumb_path = project_root / question_image if not Path(question_image).is_absolute() else Path(question_image)
                    if thumb_path.exists():
                        thumbnail_path = thumb_path.resolve()
                        logger.debug(f"Found thumbnail for {question_id}: {thumb_path.name}")
                    else:
                        logger.warning(f"Question image thumbnail not found: {thumb_path}")
                
                reel_videos_with_metadata.append({
                    'path': vid_path.resolve(),
                    'title': title,
                    'subject': subject,
                    'thumbnail': thumbnail_path
                })
            else:
                logger.warning(f"Reel video not found: {vid_path}")
    
    logger.info(f"Found {len(carousel_images_by_question)} carousels with complete image sets")
    logger.info(f"Found {len(reel_videos_with_metadata)} reel videos")
    
    # Initialize uploader with consistent session file path
    uploader = InstagramVideoUploader(
        username=username,
        password=password,
        profile_username=profile_username or username,
        session_file=session_file
    )
    
    # Login
    if not uploader.login():
        logger.error("Failed to login to Instagram")
        return {
            'success': False,
            'carousel': {'uploaded_count': 0, 'failed_count': 0, 'uploaded': [], 'failed': []},
            'reel': {'uploaded_count': 0, 'failed_count': 0, 'uploaded': [], 'failed': []},
            'total_uploaded': 0,
            'total_failed': 0,
            'error': 'Login failed'
        }
    
    # Upload carousels
    logger.info("=" * 60)
    logger.info("🖼️  UPLOADING CAROUSELS")
    logger.info("=" * 60)
    
    carousel_uploaded = []
    carousel_failed = []
    
    # Warmup session before first upload (only if we have carousels to upload)
    if carousel_images_by_question:
        uploader._warmup_session()
        uploader._human_delay(2.0, 3.5)
    
    for question_id, carousel_data in carousel_images_by_question.items():
        try:
            image_paths = carousel_data['paths']
            title = carousel_data['title']
            subject = carousel_data['subject']
            
            logger.info(f"Uploading carousel for {question_id}: {title}")
            success = uploader.upload_carousel(image_paths, subject=subject)
            
            if success:
                carousel_uploaded.append(question_id)
            else:
                carousel_failed.append(question_id)
            
            # Random delay between uploads
            delay = random.uniform(10, 15)
            logger.debug(f"⏳ Waiting {delay:.1f}s before next upload...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Failed to upload carousel {question_id}: {e}")
            carousel_failed.append(question_id)
    
    logger.info(f"✅ Carousels: {len(carousel_uploaded)} uploaded, {len(carousel_failed)} failed")
    
    # Wait before uploading reels
    if carousel_uploaded:
        delay = random.uniform(delay_between_uploads, delay_between_uploads + 5)
        logger.info(f"⏳ Waiting {delay:.1f} seconds before uploading reels...")
        time.sleep(delay)
    
    # Upload reels
    logger.info("=" * 60)
    logger.info("🎬 UPLOADING REELS")
    logger.info("=" * 60)
    
    reel_uploaded = []
    reel_failed = []
    
    # Warmup session before first reel upload (only if we have reels to upload)
    if reel_videos_with_metadata:
        uploader._warmup_session()
        uploader._human_delay(2.0, 3.5)
    
    for reel_data in reel_videos_with_metadata:
        try:
            video_path = reel_data['path']
            title = reel_data['title']
            subject = reel_data['subject']
            thumbnail_path = reel_data.get('thumbnail')
            
            caption = f"{title}\n\n#{subject} #programming #coding #dailydoseofprogramming"
            logger.info(f"Uploading reel: {video_path.name} - {title}")
            
            success = False
            if thumbnail_path:
                logger.info(f"Using custom thumbnail: {thumbnail_path.name}")
                success = uploader.upload_reel(
                    video_path=video_path,
                    caption=caption,
                    thumbnail_path=str(thumbnail_path),
                    use_custom_thumbnail=True,
                    subject=subject
                )
            else:
                logger.info("Using auto-generated thumbnail")
                success = uploader.upload_reel(video_path, caption=caption, subject=subject)
            
            if success:
                reel_uploaded.append(str(video_path))
            else:
                reel_failed.append(str(video_path))
            
            # Random delay between uploads
            delay = random.uniform(10, 15)
            logger.debug(f"⏳ Waiting {delay:.1f}s before next upload...")
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Failed to upload reel {video_path.name}: {e}")
            reel_failed.append(str(video_path))
    
    logger.info(f"✅ Reels: {len(reel_uploaded)} uploaded, {len(reel_failed)} failed")
    
    # Move uploaded files to organized folders
    if carousel_uploaded or reel_uploaded:
        logger.info("=" * 60)
        logger.info("📦 ORGANIZING UPLOADED FILES")
        logger.info("=" * 60)
        
        move_results = move_uploaded_files(
            carousel_data=carousel_images_by_question,
            reel_data=reel_videos_with_metadata,
            uploaded_carousels=carousel_uploaded,
            uploaded_reels=reel_uploaded,
            subject=subject,
            run_date=run_date,
            project_root=project_root
        )
        
        logger.info(f"✅ File organization complete: {move_results['carousels_moved']} carousels, {move_results['reels_moved']} reels")
    
    # Note: We never logout - let session expire naturally for better persistence
    logger.info("Session kept active (no logout) - will be reused in next run")
    
    # Combine results
    combined_result = {
        'success': len(carousel_failed) == 0 and len(reel_failed) == 0,
        'carousel': {
            'uploaded_count': len(carousel_uploaded),
            'failed_count': len(carousel_failed),
            'uploaded': carousel_uploaded,
            'failed': carousel_failed
        },
        'reel': {
            'uploaded_count': len(reel_uploaded),
            'failed_count': len(reel_failed),
            'uploaded': reel_uploaded,
            'failed': reel_failed
        },
        'total_uploaded': len(carousel_uploaded) + len(reel_uploaded),
        'total_failed': len(carousel_failed) + len(reel_failed)
    }
    
    logger.info("=" * 60)
    logger.info("📊 UPLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Carousels: {combined_result['carousel']['uploaded_count']} uploaded, {combined_result['carousel']['failed_count']} failed")
    logger.info(f"Reels: {combined_result['reel']['uploaded_count']} uploaded, {combined_result['reel']['failed_count']} failed")
    logger.info(f"Total: {combined_result['total_uploaded']} uploaded, {combined_result['total_failed']} failed")
    logger.info(f"Status: {'✅ SUCCESS' if combined_result['success'] else '⚠️  PARTIAL'}")
    
    return combined_result

if __name__ == "__main__":
    import sys
    import glob

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Define paths
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    output_1_dir = project_root / "output_1"

    # Load .env if python-dotenv is available
    if load_dotenv:
        load_dotenv(project_root / ".env")

    # Parse CLI arguments
    metadata_override = None
    test_mode = "--test" in sys.argv
    
    if len(sys.argv) > 1:
        if sys.argv[1] != "--test":
            metadata_override = sys.argv[1]

    if metadata_override:
        metadata_file = Path(metadata_override).resolve()
        if not metadata_file.exists():
            logger.error(f"Metadata file not found: {metadata_file}")
            sys.exit(1)
    else:
        # Find the metadata JSON file in the python/runs directory
        metadata_pattern = output_1_dir / "python" / "runs" / "*_metadata.json"
        metadata_files = glob.glob(str(metadata_pattern))

        if not metadata_files:
            logger.error("No metadata JSON file found in output_1/python/runs/")
            sys.exit(1)

        # Use the most recent metadata file
        metadata_file = Path(sorted(metadata_files)[-1]).resolve()

    logger.info(f"Using metadata file: {metadata_file}")

    # Get credentials from environment variables
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')
    profile_username = os.getenv('INSTAGRAM_PROFILE_USERNAME', username)

    if not username or not password:
        logger.error("Missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD in environment variables")
        sys.exit(1)

    # Test mode: validate files without uploading
    if test_mode:
        logger.info("=" * 60)
        logger.info("🧪 TEST MODE: Validating carousel and reel files")
        logger.info("=" * 60)
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            project_root_actual = metadata_file.parent.parent.parent.parent
            questions = metadata.get('questions', [])
            subject = metadata.get('subject', 'programming')
            
            carousel_count = 0
            reel_count = 0
            
            for q in questions:
                assets = q.get('assets', {})
                carousel_images = assets.get('carousel_images', [])
                video_path = assets.get('combined_reel')
                
                # Check carousel
                if carousel_images:
                    valid_count = 0
                    for img in carousel_images:
                        img_path = project_root_actual / img if not Path(img).is_absolute() else Path(img)
                        if img_path.exists():
                            valid_count += 1
                            logger.info(f"✅ Carousel image found: {img_path.name}")
                        else:
                            logger.warning(f"❌ Carousel image missing: {img_path}")
                    
                    if valid_count == len(carousel_images):
                        carousel_count += 1
                
                # Check reel
                if video_path:
                    vid_path = project_root_actual / video_path if not Path(video_path).is_absolute() else Path(video_path)
                    if vid_path.exists():
                        logger.info(f"✅ Reel video found: {vid_path.name}")
                        reel_count += 1
                    else:
                        logger.warning(f"❌ Reel video missing: {vid_path}")
            
            logger.info("=" * 60)
            logger.info(f"📊 Test Results: {carousel_count} complete carousels, {reel_count} reel videos")
            logger.info("=" * 60)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Test mode error: {e}")
            sys.exit(1)

    # Upload both carousel and reels
    logger.info("=" * 60)
    logger.info("📤 STARTING UNIFIED UPLOAD (Carousel + Reels)")
    logger.info("=" * 60)
    
    result = upload_from_metadata(
        metadata_file_path=metadata_file,
        username=username,
        password=password,
        profile_username=profile_username
    )

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)