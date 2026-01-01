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


def upload_reels_from_metadata(
    metadata_file_path: Path,
    username: str,
    password: str,
    session_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
    """
    Upload all reels from a metadata JSON file to Instagram.
    
    Args:
        metadata_file_path: Path to the metadata JSON file
        username: Instagram username
        password: Instagram password
        session_dir: Optional directory for session files (defaults to output_1/sessions)
    
    Returns:
        Dictionary with upload results:
        {
            'success': bool,
            'uploaded_count': int,
            'failed_count': int,
            'uploaded_reels': List[str],
            'failed_reels': List[str]
        }
    """
    logger.info(f"📤 Starting Instagram upload from metadata: {metadata_file_path}")
    
    # Setup paths - resolve metadata path once
    metadata_file_path = Path(metadata_file_path).resolve()
    # Metadata at: .../pybenders/output_1/python/runs/metadata_*.json
    # Go up 4 levels to project root: runs -> python -> output_1 -> pybenders
    project_root = metadata_file_path.parent.parent.parent.parent
    
    logger.info(f"🔍 Project root: {project_root}")
    logger.info(f"🔍 Metadata file: {metadata_file_path}")
    
    # Use session directory in output_1 (where metadata lives) for consistency
    if session_dir is None:
        session_dir = metadata_file_path.parent.parent.parent / "sessions"  # output_1/sessions
    
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "instagram_session.json"
    logger.info(f"🔍 Session file: {session_file}")
    
    # Load metadata
    try:
        with open(metadata_file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load metadata file: {e}")
        return {
            'success': False,
            'uploaded_count': 0,
            'failed_count': 0,
            'uploaded_reels': [],
            'failed_reels': [],
            'error': str(e)
        }
    
    # Extract questions
    questions = metadata.get('questions', [])
    if not questions:
        logger.info("No questions found in metadata. Nothing to upload.")
        return {
            'success': True,
            'uploaded_count': 0,
            'failed_count': 0,
            'uploaded_reels': [],
            'failed_reels': []
        }
    
    logger.info(f"Found {len(questions)} reels to upload")
    
    # Initialize uploader
    uploader = InstagramVideoUploader(
        username=username,
        password=password,
        session_file=str(session_file),
        delay_range=[5, 10]
    )
    
    # Login
    if not uploader.login():
        logger.error("Failed to login to Instagram")
        return {
            'success': False,
            'uploaded_count': 0,
            'failed_count': len(questions),
            'uploaded_reels': [],
            'failed_reels': [q.get('question_id', 'unknown') for q in questions],
            'error': 'Login failed'
        }
    
    # Get account info
    account_info = uploader.get_account_info()
    if account_info:
        logger.info(f"✓ Logged in as: {account_info['username']}")
    
    # Track results
    uploaded_reels = []
    failed_reels = []
    
    # Extract subject from metadata for caption selection
    subject = metadata.get('subject', 'python')
    logger.info(f"Using subject for captions: {subject}")
    
    # Upload each reel
    for idx, question in enumerate(questions, 1):
        question_id = question.get('question_id', 'unknown')
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing reel {idx}/{len(questions)}: {question_id}")
        logger.info(f"{'='*60}")
        
        # Get reel path from metadata
        combined_reel = question.get('assets', {}).get('combined_reel', '')
        if not combined_reel:
            logger.warning(f"No combined_reel found for question: {question_id}")
            failed_reels.append(question_id)
            continue
        
        # Convert relative path to absolute path
        # combined_reel is like "output_1\python\reels\file.mp4"
        reel_path = project_root / combined_reel.replace('\\', '/')
        
        logger.debug(f"Reel path resolved to: {reel_path}")
        
        if not reel_path.exists():
            logger.warning(f"Reel file not found: {reel_path}")
            failed_reels.append(question_id)
            continue
        
        # Get thumbnail path from metadata
        question_image = question.get('assets', {}).get('question_image', '')
        thumbnail_path = project_root / question_image.replace('\\', '/') if question_image else None
        
        if thumbnail_path and not thumbnail_path.exists():
            logger.warning(f"Thumbnail file not found: {thumbnail_path}")
            thumbnail_path = None
        
        # Upload the reel with subject-specific caption
        success = uploader.upload_reel(
            video_path=str(reel_path),
            caption="",  # Auto-generate from subject
            thumbnail_path=str(thumbnail_path) if thumbnail_path else None,
            use_custom_thumbnail=True if thumbnail_path else False,
            subject=subject
        )
        
        if success:
            uploaded_reels.append(question_id)
            logger.info(f"✓ Successfully uploaded: {question_id}")
            
            # Post-upload cleanup and archiving
            try:
                # Create uploaded folder structure with date
                subject = metadata.get('subject', 'python')
                uploaded_dir = project_root / "uploaded" / subject
                current_date = time.strftime("%Y-%m-%d")
                date_folder = uploaded_dir / current_date
                date_folder.mkdir(parents=True, exist_ok=True)
                
                # Remove temporary thumbnail if it exists
                tmp_thumbnail_path = str(reel_path) + '.jpg'
                if os.path.exists(tmp_thumbnail_path):
                    os.remove(tmp_thumbnail_path)
                    logger.debug(f"Removed temporary thumbnail: {tmp_thumbnail_path}")
                
                # Move the uploaded reel to archive with aggressive exponential backoff retry
                destination = date_folder / reel_path.name
                max_retries = 7
                retry_delays = [5, 10, 15, 20, 30, 45, 60]  # Longer exponential backoff in seconds
                archive_success = False
                
                for attempt in range(1, max_retries + 1):
                    try:
                        # Initial longer wait before first attempt to ensure all handles are released
                        if attempt == 1:
                            logger.info("Waiting 20s before archiving to ensure all file handles are released...")
                            time.sleep(20)
                        
                        logger.debug(f"Attempting to archive reel (attempt {attempt}/{max_retries})...")
                        shutil.move(str(reel_path), str(destination))
                        logger.info(f"✓ Archived reel to: {destination}")
                        archive_success = True
                        break
                        
                    except (PermissionError, OSError, FileNotFoundError) as e:
                        if attempt < max_retries:
                            delay = retry_delays[attempt - 1]
                            logger.warning(
                                f"File locked (attempt {attempt}/{max_retries}), "
                                f"retrying in {delay}s: {type(e).__name__}"
                            )
                            time.sleep(delay)
                        else:
                            # All retries exhausted
                            logger.error(
                                f"Failed to archive reel after {max_retries} attempts. "
                                f"File may still be in use by system processes. "
                                f"Manual archive may be needed: {reel_path} -> {destination}"
                            )
                            # Don't crash - upload was successful even if archive failed
                            archive_success = False
                
            except Exception as e:
                logger.error(f"Failed to archive reel: {e}")
        else:
            failed_reels.append(question_id)
            logger.error(f"✗ Failed to upload: {question_id}")
        
        # Delay between uploads to avoid rate limiting
        if idx < len(questions):
            logger.info("⏳ Waiting before next upload...")
            time.sleep(10)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("📊 UPLOAD SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total reels: {len(questions)}")
    logger.info(f"✓ Uploaded: {len(uploaded_reels)}")
    logger.info(f"✗ Failed: {len(failed_reels)}")
    
    if uploaded_reels:
        logger.info(f"\nUploaded reels:")
        for reel_id in uploaded_reels:
            logger.info(f"  ✓ {reel_id}")
    
    if failed_reels:
        logger.info(f"\nFailed reels:")
        for reel_id in failed_reels:
            logger.info(f"  ✗ {reel_id}")
    
    return {
        'success': len(failed_reels) == 0,
        'uploaded_count': len(uploaded_reels),
        'failed_count': len(failed_reels),
        'uploaded_reels': uploaded_reels,
        'failed_reels': failed_reels
    }


# if __name__ == "__main__":
#     import sys
#     import glob

#     # Configure logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
#     # metadata generated at: pybenders\output_1\python\runs\2026-01-01_083340_metadata.json
#     # publisher pybenders\pybender\publishers\instagram_publisher.py

#     # Define paths
#     script_dir = Path(__file__).resolve().parent # pybenders/output_1
#     project_root = script_dir.parent.parent # pybenders
#     output_1_dir = project_root / "output_1" # pybenders/output_1

#     # Load .env if python-dotenv is available
#     if load_dotenv:
#         load_dotenv(project_root / ".env")

#     # Optional override: CLI arg or env METADATA_FILE
#     metadata_override = sys.argv[1] if len(sys.argv) > 1 else os.getenv("METADATA_FILE")

#     if metadata_override:
#         metadata_file = Path(metadata_override).resolve()
#         if not metadata_file.exists():
#             logger.error(f"Metadata file not found: {metadata_file}")
#             sys.exit(1)
#     else:
#         # Find the metadata JSON file in the python/runs directory
#         metadata_pattern = output_1_dir / "python" / "runs" / "*_metadata.json"
#         metadata_files = glob.glob(str(metadata_pattern))

#         if not metadata_files:
#             logger.error("No metadata JSON file found in output_1/python/runs/")
#             sys.exit(1)

#         # Use the most recent metadata file
#         metadata_file = Path(sorted(metadata_files)[-1]).resolve()

#     logger.info(f"Using metadata file: {metadata_file}")

#     # Get credentials from environment variables (no defaults)
#     username = os.getenv('INSTAGRAM_USERNAME')
#     password = os.getenv('INSTAGRAM_PASSWORD')

#     if not username or not password:
#         logger.error("Missing INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD in environment variables")
#         sys.exit(1)

#     # Upload reels
#     result = upload_reels_from_metadata(
#         metadata_file_path=metadata_file,
#         username=username,
#         password=password
#     )

#     # Exit with appropriate code
#     sys.exit(0 if result['success'] else 1)
