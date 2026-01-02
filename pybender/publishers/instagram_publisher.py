"""
Instagram Video Uploader using instagrapi.

Follows best practices from:
https://subzeroid.github.io/instagrapi/usage-guide/best-practices.html

Features:
- Session persistence to avoid repeated logins
- Automatic retry logic with delays
- Proper error handling and logging
- Configurable delays to mimic real user behavior
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
    1. Session persistence - avoid repeated logins
    2. Delay ranges - mimic real user behavior
    3. Proxy support - optional IP rotation
    4. Error handling and logging
    5. Session validation before upload
    """
    
    def __init__(
        self,
        username: str = "YOUR_INSTAGRAM_USERNAME",
        password: str = "YOUR_INSTAGRAM_PASSWORD",
        session_file: str = "instagram_session.json",
        proxy: Optional[str] = None,
        delay_range: list = [1, 3]
        ):
        """
        Initialize Instagram video uploader.
        
        Args:
            username: Instagram username (placeholder by default)
            password: Instagram password (placeholder by default)
            session_file: Path to store/load session JSON file
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
        self.password = password
        self.session_file = Path(session_file)
        self.proxy = proxy
        self.delay_range = delay_range
        
        # Initialize client
        self.cl = Client()
        
        # Set delays to mimic real user behavior
        self.cl.delay_range = delay_range
        
        # Subject-specific captions with relevant hashtags
        self.subject_captions = {
            "python": [
                "Can you crack this in 30 seconds? 🚀 #Python #CodeChallenge #PythonTips #Programming",
                "Think you've got the answer? Prove it. ⚡ #Python #DevQuiz #PythonProgramming #Coding",
                "One quick puzzle: what's your move? 🤔 #Python #CodeChallenge #PythonDev #Programming",
                "Your turn—solve it before the timer ends. 🎯 #Python #CodingQuiz #PythonCoding #Tech",
                "Pause, solve, flex your brain. 🧠 #Python #CodeChallenge #PythonTricks #Programming"
            ],
            "sql": [
                "Can you crack this in 30 seconds? 🚀 #SQL #Database #DataEngineering #SQLQuery",
                "Think you've got the answer? Prove it. ⚡ #SQL #DatabaseDesign #DataScience #SQLServer",
                "One quick puzzle: what's your move? 🤔 #SQL #DataEngineering #DatabaseDev #SQLQueries",
                "Your turn—solve it before the timer ends. 🎯 #SQL #DataAnalytics #DatabaseAdmin #SQLChallenge",
                "Pause, solve, flex your brain. 🧠 #SQL #Database #DataEngineering #SQLTips"
            ],
            "javascript": [
                "Can you crack this in 30 seconds? 🚀 #JavaScript #WebDev #JS #Frontend",
                "Think you've got the answer? Prove it. ⚡ #JavaScript #WebDevelopment #JSCode #Coding",
                "One quick puzzle: what's your move? 🤔 #JavaScript #FrontendDev #JSProgramming #WebDev",
                "Your turn—solve it before the timer ends. 🎯 #JavaScript #JSChallenge #WebDevelopment #Frontend",
                "Pause, solve, flex your brain. 🧠 #JavaScript #WebDev #JSTricks #Programming"
            ],
            "rust": [
                "Can you crack this in 30 seconds? 🚀 #RustLang #SystemsProgramming #Rust #Programming",
                "Think you've got the answer? Prove it. ⚡ #RustLang #RustProgramming #SystemsCode #Coding",
                "One quick puzzle: what's your move? 🤔 #RustLang #RustDev #LowLevel #Programming",
                "Your turn—solve it before the timer ends. 🎯 #RustLang #RustCode #SystemsProgramming #Tech",
                "Pause, solve, flex your brain. 🧠 #RustLang #Rust #SafeSystems #Programming"
            ],
            "golang": [
                "Can you crack this in 30 seconds? 🚀 #Golang #Go #Backend #CloudNative",
                "Think you've got the answer? Prove it. ⚡ #Golang #GoDev #BackendDev #Programming",
                "One quick puzzle: what's your move? 🤔 #Golang #GoLang #Microservices #CloudNative",
                "Your turn—solve it before the timer ends. 🎯 #Golang #Go #BackendDevelopment #DevOps",
                "Pause, solve, flex your brain. 🧠 #Golang #GoProgramming #Backend #CloudNative"
            ],
            "linux": [
                "Can you crack this in 30 seconds? 🚀 #Linux #SysAdmin #DevOps #Terminal",
                "Think you've got the answer? Prove it. ⚡ #Linux #SystemAdmin #BashScripting #DevOps",
                "One quick puzzle: what's your move? 🤔 #Linux #CommandLine #SysAdmin #OpenSource",
                "Your turn—solve it before the timer ends. 🎯 #Linux #DevOps #SystemAdministration #Terminal",
                "Pause, solve, flex your brain. 🧠 #Linux #SysAdmin #BashCommands #DevOps"
            ],
            "regex": [
                "Can you crack this in 30 seconds? 🚀 #Regex #RegularExpressions #Programming #TextProcessing",
                "Think you've got the answer? Prove it. ⚡ #Regex #RegExp #PatternMatching #Coding",
                "One quick puzzle: what's your move? 🤔 #Regex #RegularExpressions #TextParsing #Programming",
                "Your turn—solve it before the timer ends. 🎯 #Regex #PatternMatching #Programming #DataValidation",
                "Pause, solve, flex your brain. 🧠 #Regex #RegularExpressions #StringManipulation #Programming"
            ],
            "docker_k8s": [
                "Can you crack this in 30 seconds? 🚀 #Docker #Kubernetes #DevOps #CloudNative",
                "Think you've got the answer? Prove it. ⚡ #Docker #K8s #ContainerOrchestration #DevOps",
                "One quick puzzle: what's your move? 🤔 #Docker #Kubernetes #Containers #CloudNative",
                "Your turn—solve it before the timer ends. 🎯 #Docker #K8s #DevOps #CloudComputing",
                "Pause, solve, flex your brain. 🧠 #Docker #Kubernetes #Containerization #DevOps"
            ],
            "system_design": [
                "Can you crack this in 30 seconds? 🚀 #SystemDesign #Architecture #SoftwareEngineering #ScalableSystems",
                "Think you've got the answer? Prove it. ⚡ #SystemDesign #SoftwareArchitecture #Engineering #Scalability",
                "One quick puzzle: what's your move? 🤔 #SystemDesign #Architecture #DistributedSystems #Engineering",
                "Your turn—solve it before the timer ends. 🎯 #SystemDesign #SoftwareEngineering #Architecture #Tech",
                "Pause, solve, flex your brain. 🧠 #SystemDesign #Architecture #Scalability #SoftwareEngineering"
            ]
        }
        
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
        
        logger.info(f"Initialized InstagramVideoUploader for user: {username}")
    
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
        Validate if current session is still active.
        
        Returns:
            True if session is valid, False otherwise
        """
        try:
            # Try to fetch timeline to validate session
            self.cl.get_timeline_feed()
            logger.debug("Session validation successful")
            return True
        except LoginRequired:
            logger.warning("Session is no longer valid (LoginRequired)")
            return False
        except Exception as e:
            if "user_has_logged_out" in str(e):
                logger.warning(f"Session logged out by Instagram: {e}")
                return False
            logger.warning(f"Session validation failed: {e}")
            return False
    
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
    
    def login(self) -> bool:
        """
        Login to Instagram with proper session handling.
        
        Follows best practices:
        1. Try to load and validate existing session
        2. If valid, use it
        3. If invalid, do fresh login with credentials
        4. Save session for future use
        
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
        
        # Try to use saved session first
        if self._load_session():
            logger.info("Attempting to validate saved session...")
            time.sleep(2)  # Brief delay before validation
            
            if self._validate_session():
                logger.info("✓ Successfully logged in using saved session")
                return True
            else:
                logger.info("✗ Saved session is invalid, clearing and attempting fresh login...")
                self._clear_session()
                time.sleep(2)  # Delay before new login
        
        # Fresh login with credentials
        try:
            logger.info(f"Attempting fresh login with credentials for: {self.username}")
            
            # Ensure clean state
            self._clear_session()
            time.sleep(1)
            
            # Login
            self.cl.login(self.username, self.password)
            logger.info("✓ Fresh login successful")
            
            # Brief delay before saving/validating
            time.sleep(2)
            
            # Validate the fresh login
            if not self._validate_session():
                logger.error("Fresh login failed validation")
                self._clear_session()
                return False
            
            # Save session for future use
            if self._save_session():
                logger.info("✓ Login successful and session saved")
                return True
            else:
                logger.warning("Login successful but failed to save session")
                return True  # Login was successful even if save failed
                
        except Exception as e:
            logger.error(f"✗ Login failed: {e}")
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
        
        Example:
            uploader = InstagramVideoUploader(username="user", password="pass")
            uploader.login()
            
            # Option 1: Auto-generate thumbnail (safer)
            success = uploader.upload_reel(
                video_path="path/to/video.mp4",
                caption="Check out this amazing reel! 🚀"
            )
            
            # Option 2: Use custom thumbnail (may have validation errors)
            success = uploader.upload_reel(
                video_path="path/to/video.mp4",
                caption="Check out this amazing reel! 🚀",
                thumbnail_path="path/to/custom_thumbnail.png",
                use_custom_thumbnail=True
            )
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
            retries: Number of retry attempts on failure
        
        Returns:
            True if upload successful, False otherwise
        
        Example:
            images = ["path/to/image1.png", "path/to/image2.png"]
            success = uploader.upload_carousel(
                image_paths=images,
                caption="Swipe to see more! 📸"
            )
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
                    delay = min(2 ** attempt, 30)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} upload attempts failed")
        
        return False
    
    def logout(self) -> None:
        """Logout from Instagram."""
        try:
            self.cl.logout()
            logger.info("Logged out from Instagram")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
    
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


def upload_from_metadata(
    metadata_file_path: Path,
    username: str,
    password: str,
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
        session_dir: Optional directory for session files (defaults to output_1/sessions)
        delay_between_uploads: Delay in seconds between carousel and reel uploads (default: 12)
    
    Returns:
        Dictionary with combined upload results:
        {
            'success': bool,
            'carousel': {'uploaded_count': int, 'failed_count': int, 'uploaded': list, 'failed': list},
            'reel': {'uploaded_count': int, 'failed_count': int, 'uploaded': list, 'failed': list},
            'total_uploaded': int,
            'total_failed': int
        }
    """
    metadata_file_path = Path(metadata_file_path).resolve()
    logger.info(f"📤 Starting unified upload from: {metadata_file_path}")
    
    # Setup paths
    project_root = metadata_file_path.parent.parent.parent.parent
    if session_dir is None:
        session_dir = metadata_file_path.parent.parent.parent / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "instagram_session.json"
    
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
        question_image = assets.get('question_image')  # Thumbnail for reel
        
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
    
    # Initialize uploader
    uploader = InstagramVideoUploader(
        username=username,
        password=password,
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
    
    for question_id, carousel_data in carousel_images_by_question.items():
        try:
            image_paths = carousel_data['paths']
            title = carousel_data['title']
            subject = carousel_data['subject']
            
            # caption = f"{title}\n\n#{subject} #programming #coding #dailydoseofprogramming" # dynaically generated
            logger.info(f"Uploading carousel for {question_id}: {title}")
            uploader.upload_carousel(image_paths, subject=subject)
            carousel_uploaded.append(question_id)
            time.sleep(random.uniform(10, 15))  # Rate limiting between uploads
        except Exception as e:
            logger.error(f"Failed to upload carousel {question_id}: {e}")
            carousel_failed.append(question_id)
    
    logger.info(f"✅ Carousels: {len(carousel_uploaded)} uploaded, {len(carousel_failed)} failed")
    
    # Wait before uploading reels
    if carousel_uploaded:
        logger.info(f"⏳ Waiting {delay_between_uploads} seconds before uploading reels...")
        time.sleep(delay_between_uploads)
    
    # Upload reels
    logger.info("=" * 60)
    logger.info("🎬 UPLOADING REELS")
    logger.info("=" * 60)
    
    reel_uploaded = []
    reel_failed = []
    
    for reel_data in reel_videos_with_metadata:
        try:
            video_path = reel_data['path']
            title = reel_data['title']
            subject = reel_data['subject']
            thumbnail_path = reel_data.get('thumbnail')
            
            caption = f"{title}\n\n#{subject} #programming #coding #dailydoseofprogramming"
            logger.info(f"Uploading reel: {video_path.name} - {title}")
            
            if thumbnail_path:
                logger.info(f"Using custom thumbnail: {thumbnail_path.name}")
                uploader.upload_reel(
                    video_path=video_path,
                    caption=caption,
                    thumbnail_path=str(thumbnail_path),
                    use_custom_thumbnail=True,
                    subject=subject
                )
            else:
                logger.info("Using auto-generated thumbnail")
                uploader.upload_reel(video_path, caption=caption, subject=subject)
            
            reel_uploaded.append(str(video_path))
            time.sleep(random.uniform(10, 15))  # Rate limiting between uploads
        except Exception as e:
            logger.error(f"Failed to upload reel {video_path.name}: {e}")
            reel_failed.append(str(video_path))
    
    logger.info(f"✅ Reels: {len(reel_uploaded)} uploaded, {len(reel_failed)} failed")
    
    # # Logout
    # try:
    #     uploader.logout()
    # except Exception as e:
    #     logger.warning(f"Logout warning: {e}")
    
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
    # metadata generated at: pybenders\output_1\python\runs\2026-01-01_083340_metadata.json
    # publisher pybenders\pybender\publishers\instagram_publisher.py

    # Define paths
    script_dir = Path(__file__).resolve().parent # pybenders/output_1
    project_root = script_dir.parent.parent # pybenders
    output_1_dir = project_root / "output_1" # pybenders/output_1

    # Load .env if python-dotenv is available
    if load_dotenv:
        load_dotenv(project_root / ".env")

    # Parse CLI arguments
    # Usage: python instagram_publisher.py <metadata_file>
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

    # Get credentials from environment variables (no defaults)
    username = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

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

    # Upload both carousel and reels with unified function
    logger.info("=" * 60)
    logger.info("📤 STARTING UNIFIED UPLOAD (Carousel + Reels)")
    logger.info("=" * 60)
    # print(carousel_images)
    # print(video_path)
    result = upload_from_metadata(
        metadata_file_path=metadata_file,
        username=username,
        password=password
    )

    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)
