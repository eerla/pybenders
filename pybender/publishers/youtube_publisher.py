"""
YouTube Video Uploader using Google API.

Features:
- OAuth2 session persistence to avoid repeated authentications
- Automatic retry logic with exponential backoff
- Proper error handling and logging
- Random delays to mimic real user behavior
- Session warmup with discovery actions (anti-bot)
- Support for both Shorts and regular videos
"""
import logging
import shutil
import time
import json
import os
import sys
import random
import glob
import pickle
from pathlib import Path
from typing import Optional, Dict, Any, List
from pybender.publishers.subject_captions import SUBJECT_CAPTIONS

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload
except ImportError:
    raise ImportError(
        "Google API client not installed. Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2"
    )

logger = logging.getLogger("YouTubeVideoUploader")

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube.readonly']


class YouTubeVideoUploader:
    """
    Uploads videos to YouTube following best practices.
    
    Best practices implemented:
    1. OAuth2 session persistence - avoid repeated authentications
    2. Delay ranges - mimic real user behavior
    3. Error handling and logging
    4. Session validation before upload
    5. Discovery actions for anti-bot (warmup session)
    6. Exponential backoff on retries
    """
    
    def __init__(
        self,
        client_secrets_file: str = "client_secrets.json",
        credentials_file: Optional[Path] = None,
        delay_range: list = [2, 5]
    ):
        """
        Initialize YouTube video uploader.
        
        Args:
            client_secrets_file: Path to OAuth2 client secrets JSON file
            credentials_file: Path to store/load credentials (auto-generated if None)
            delay_range: [min, max] delay in seconds between requests
        
        Example:
            uploader = YouTubeVideoUploader(
                client_secrets_file="client_secrets.json",
                delay_range=[2, 5]
            )
        """
        self.client_secrets_file = Path(client_secrets_file)
        
        # Generate credentials file if not provided
        if credentials_file is None:
            credentials_file = Path("sessions/youtube_credentials.pickle")
        
        self.credentials_file = Path(credentials_file)
        self.credentials_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.delay_range = delay_range
        self.youtube = None
        self.credentials = None
        
        # Subject-specific descriptions and tags
        self.subject_captions = SUBJECT_CAPTIONS
        
        # Generic fallback for unknown subjects
        self.generic_tags = [
            "programming", "coding", "tutorial", "developer", "software",
            "tech", "computer science", "learn to code"
        ]
        
        logger.info(f"Initialized YouTubeVideoUploader")
        logger.info(f"Credentials file: {self.credentials_file}")
        logger.info(f"Client secrets: {self.client_secrets_file}")
    
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
        - Getting channel info (validates credentials)
        - Listing playlists (appears content-aware)
        - Searching videos (mimics discovery behavior)
        
        Returns:
            True if warmup succeeded or was skipped
        """
        if not self.youtube:
            logger.warning("⚠️  YouTube service not initialized, skipping warmup")
            return False
        
        logger.info("🔥 Warming up session with discovery actions...")
        
        # Decide which actions to perform (randomize for natural behavior)
        actions = ['channel', 'playlists', 'search']
        selected_actions = random.sample(actions, random.randint(1, 3))
        
        success_count = 0
        
        # Action 1: Get channel info
        if 'channel' in selected_actions:
            try:
                self._human_delay(1.0, 2.0)
                request = self.youtube.channels().list(
                    part="snippet,statistics",
                    mine=True
                )
                response = request.execute()
                if response.get('items'):
                    channel = response['items'][0]
                    stats = channel.get('statistics', {})
                    logger.debug(f"✓ Retrieved channel: {channel['snippet']['title']} "
                               f"({stats.get('subscriberCount', 0)} subscribers)")
                success_count += 1
            except Exception as e:
                logger.warning(f"⚠️  Could not retrieve channel info: {e}")
        
        # Action 2: List playlists
        if 'playlists' in selected_actions:
            try:
                self._human_delay(1.0, 2.0)
                request = self.youtube.playlists().list(
                    part="snippet",
                    mine=True,
                    maxResults=5
                )
                response = request.execute()
                playlist_count = len(response.get('items', []))
                logger.debug(f"✓ Retrieved {playlist_count} playlists")
                success_count += 1
            except Exception as e:
                logger.warning(f"⚠️  Could not retrieve playlists: {e}")
        
        # Action 3: Search for programming videos
        if 'search' in selected_actions:
            try:
                self._human_delay(1.0, 2.0)
                search_terms = ['python tutorial', 'coding challenge', 'programming', 'web development']
                query = random.choice(search_terms)
                request = self.youtube.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=5
                )
                response = request.execute()
                result_count = len(response.get('items', []))
                logger.debug(f"✓ Searched '{query}': {result_count} results")
                success_count += 1
            except Exception as e:
                logger.warning(f"⚠️  Could not perform search: {e}")
        
        logger.info(f"✅ Session warmup complete ({success_count}/{len(selected_actions)} actions successful)")
        return True
    
    def _load_credentials(self) -> bool:
        """
        Load saved OAuth2 credentials from file.
        
        Returns:
            True if credentials loaded successfully
        """
        if not self.credentials_file.exists():
            logger.debug(f"Credentials file not found: {self.credentials_file}")
            return False
        
        try:
            with open(self.credentials_file, 'rb') as token:
                self.credentials = pickle.load(token)
            logger.info(f"✓ Loaded saved credentials from: {self.credentials_file}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load credentials: {e}")
            # Delete corrupted credentials
            try:
                self.credentials_file.unlink()
                logger.info(f"Deleted corrupted credentials file")
            except:
                pass
            return False
    
    def _save_credentials(self) -> bool:
        """
        Save OAuth2 credentials to file for later use.
        
        Returns:
            True if successful
        """
        try:
            with open(self.credentials_file, 'wb') as token:
                pickle.dump(self.credentials, token)
            logger.info(f"✓ Credentials saved to: {self.credentials_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False
    
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube using OAuth2.
        
        Strategy:
        1. Try to load saved credentials
        2. If expired, refresh them
        3. If no credentials, initiate OAuth2 flow
        4. Save credentials for future use
        
        Returns:
            True if authentication successful
        """
        # Load saved credentials if available
        if self._load_credentials():
            time.sleep(random.uniform(0.8, 1.5))
            
            # Check if credentials are valid
            if self.credentials and self.credentials.valid:
                logger.info("✓ Credentials are valid")
                self.youtube = build('youtube', 'v3', credentials=self.credentials)
                return True
            
            # Refresh expired credentials
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    logger.info("→ Refreshing expired credentials...")
                    time.sleep(random.uniform(0.8, 1.5))
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    logger.info("✓ Credentials refreshed successfully")
                    self.youtube = build('youtube', 'v3', credentials=self.credentials)
                    return True
                except Exception as e:
                    logger.warning(f"✗ Could not refresh credentials: {e}")
                    self.credentials = None
        
        # No valid credentials - initiate OAuth2 flow
        if not self.client_secrets_file.exists():
            logger.error(f"✗ Client secrets file not found: {self.client_secrets_file}")
            logger.error("   Download from Google Cloud Console: https://console.cloud.google.com/apis/credentials")
            return False
        
        try:
            logger.info("→ Starting OAuth2 authentication flow...")
            time.sleep(random.uniform(0.8, 1.5))
            
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secrets_file),
                SCOPES
            )
            self.credentials = flow.run_local_server(port=0)
            
            logger.info("✓ OAuth2 authentication successful")
            time.sleep(random.uniform(1.5, 3.0))
            
            # Save credentials
            self._save_credentials()
            
            # Build YouTube service
            self.youtube = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            logger.error(f"✗ Authentication failed: {e}")
            return False
    
    def _get_video_metadata(
        self,
        title: str,
        description: str,
        tags: List[str],
        category_id: str = "28",  # Science & Technology
        privacy_status: str = "public",
        is_short: bool = False
    ) -> Dict[str, Any]:
        """
        Prepare video metadata for upload.
        
        Args:
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (28 = Science & Technology)
            privacy_status: 'public', 'private', or 'unlisted'
            is_short: Whether this is a YouTube Short
        
        Returns:
            Metadata dictionary
        """
        # Add #Shorts hashtag for YouTube Shorts
        if is_short and '#Shorts' not in description:
            description = f"{description}\n\n#Shorts"
        
        return {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str = "",
        tags: List[str] = None,
        category_id: str = "28",
        privacy_status: str = "public",
        is_short: bool = False,
        retries: int = 3
    ) -> Optional[str]:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: 'public', 'private', or 'unlisted'
            is_short: Whether this is a YouTube Short (< 60 seconds)
            retries: Number of retry attempts on failure
        
        Returns:
            Video ID if successful, None otherwise
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            logger.error(f"❌ Video file not found: {video_path}")
            return None
        
        if tags is None:
            tags = self.generic_tags
        
        logger.info(f"Starting {'Short' if is_short else 'video'} upload: {video_path.name}")
        logger.info(f"Title: {title}")
        
        # Prepare metadata
        body = self._get_video_metadata(
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status,
            is_short=is_short
        )
        
        # Retry loop
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Upload attempt {attempt}/{retries}")
                
                # Human-like delay before upload
                self._human_delay(*self.delay_range)
                
                # Create media upload
                media = MediaFileUpload(
                    str(video_path),
                    chunksize=1024 * 1024,  # 1MB chunks
                    resumable=True
                )
                
                # Execute upload
                request = self.youtube.videos().insert(
                    part=",".join(body.keys()),
                    body=body,
                    media_body=media
                )
                
                response = None
                while response is None:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        logger.info(f"  Upload progress: {progress}%")
                
                video_id = response['id']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                logger.info(f"✓ Successfully uploaded: {video_id}")
                logger.info(f"✓ Video URL: {video_url}")
                
                return video_id
                
            except HttpError as e:
                logger.error(f"Upload attempt {attempt} failed: {e}")
                
                if e.resp.status in [500, 502, 503, 504]:
                    # Retriable HTTP errors
                    if attempt < retries:
                        delay = random.uniform(2 ** attempt, 2 ** attempt + 5)
                        logger.info(f"Retrying in {delay:.1f} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {retries} upload attempts failed")
                else:
                    # Non-retriable error
                    logger.error(f"Non-retriable error: {e.resp.status}")
                    return None
                    
            except Exception as e:
                logger.error(f"Upload attempt {attempt} failed: {e}")
                
                if attempt < retries:
                    delay = random.uniform(2 ** attempt, 2 ** attempt + 5)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {retries} upload attempts failed")
        
        return None
    
    def get_channel_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current channel information.
        
        Returns:
            Channel info dictionary or None if failed
        """
        if not self.youtube:
            logger.error("YouTube service not initialized")
            return None
        
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics,contentDetails",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                return {
                    "id": channel['id'],
                    "title": channel['snippet']['title'],
                    "description": channel['snippet']['description'],
                    "subscriber_count": channel['statistics'].get('subscriberCount', 0),
                    "video_count": channel['statistics'].get('videoCount', 0),
                    "view_count": channel['statistics'].get('viewCount', 0)
                }
            return None
        except Exception as e:
            logger.error(f"⚠️  Failed to get channel info: {e}")
            return None


def move_uploaded_files(
    video_data: List[Dict[str, Any]],
    uploaded_videos: List[str],
    subject: str,
    run_date: str,
    project_root: Path
) -> Dict[str, Any]:
    """
    Move successfully uploaded files to organized folders.
    
    Args:
        video_data: List of dictionaries with video data
        uploaded_videos: List of successfully uploaded video paths
        subject: Subject name (e.g., 'python', 'sql')
        run_date: Run date string (e.g., '2026-01-09_173142')
        project_root: Project root path
    
    Returns:
        Dictionary with move operation results
    """
    results = {
        'videos_moved': 0,
        'errors': []
    }
    
    # Setup target directory
    uploaded_root = project_root / "uploaded" / subject / run_date
    video_dir = uploaded_root / "youtube_videos"
    
    try:
        video_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Created upload directory: {uploaded_root}")
    except Exception as e:
        error_msg = f"Failed to create upload directories: {e}"
        logger.error(error_msg)
        results['errors'].append(error_msg)
        return results
    
    # Move successfully uploaded videos
    logger.info("📦 Moving uploaded videos...")
    for video_path_str in uploaded_videos:
        try:
            video_path = Path(video_path_str)
            if not video_path.exists():
                logger.warning(f"  ⚠️  Video file not found (already moved?): {video_path.name}")
                continue
            
            target_path = video_dir / video_path.name
            shutil.move(str(video_path), str(target_path))
            logger.info(f"  ✓ Moved: {video_path.name}")
            results['videos_moved'] += 1
            
        except Exception as e:
            error_msg = f"Failed to move video {Path(video_path_str).name}: {e}"
            logger.error(f"  ✗ {error_msg}")
            results['errors'].append(error_msg)
    
    logger.info(f"📦 Move summary: {results['videos_moved']} videos moved")
    if results['errors']:
        logger.warning(f"⚠️  {len(results['errors'])} errors occurred during move operations")
    
    return results


def upload_from_metadata(
    metadata_file_path: Path,
    client_secrets_file: str = "client_secrets.json",
    session_dir: Optional[Path] = None,
    delay_between_uploads: int = 15,
    privacy_status: str = "public"
) -> Dict[str, Any]:
    """
    Upload videos to YouTube from metadata file.
    
    Args:
        metadata_file_path: Path to the metadata JSON file
        client_secrets_file: Path to OAuth2 client secrets
        session_dir: Optional directory for credentials (defaults to project_root/sessions)
        delay_between_uploads: Delay in seconds between uploads (default: 15)
        privacy_status: Video privacy status ('public', 'private', 'unlisted')
    
    Returns:
        Dictionary with upload results
    """
    metadata_file_path = Path(metadata_file_path).resolve()
    logger.info(f"📤 Starting YouTube upload from: {metadata_file_path}")
    
    # Extract run_date from metadata filename
    run_date = metadata_file_path.stem.replace('_metadata', '')
    logger.info(f"📅 Run date: {run_date}")
    
    # Setup paths
    project_root = metadata_file_path.parent.parent.parent.parent
    if session_dir is None:
        session_dir = project_root / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    
    credentials_file = session_dir / "youtube_credentials.pickle"
    logger.info(f"📂 Credentials file: {credentials_file}")
    
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
            'uploaded': [],
            'failed': [],
            'error': str(e)
        }
    
    # Collect videos from metadata
    videos_to_upload = []
    questions = metadata.get('questions', [])
    subject = metadata.get('subject', 'programming')
    
    for q in questions:
        question_id = q.get('question_id')
        title = q.get('title', '')
        content = q.get('content', {})
        assets = q.get('assets', {})
        
        # Get reel/short video
        video_path = assets.get('combined_reel')
        if video_path:
            vid_path = project_root / video_path if not Path(video_path).is_absolute() else Path(video_path)
            if vid_path.exists():
                # Generate description
                question_text = content.get('question', '')
                explanation = content.get('explanation', '')
                description = f"{title}\n\n{question_text}\n\n{explanation}\n\n#programming #{subject} #coding #shorts"
                
                # Get tags
                tags = ['programming', 'coding', subject, 'tutorial', 'shorts', 'tech']
                
                videos_to_upload.append({
                    'path': vid_path.resolve(),
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': tags,
                    'is_short': True,  # Assume reels are shorts
                    'question_id': question_id
                })
            else:
                logger.warning(f"Video not found: {vid_path}")
    
    logger.info(f"Found {len(videos_to_upload)} videos to upload")
    
    # Initialize uploader
    uploader = YouTubeVideoUploader(
        client_secrets_file=client_secrets_file,
        credentials_file=credentials_file
    )
    
    # Authenticate
    if not uploader.authenticate():
        logger.error("Failed to authenticate with YouTube")
        return {
            'success': False,
            'uploaded_count': 0,
            'failed_count': 0,
            'uploaded': [],
            'failed': [],
            'error': 'Authentication failed'
        }
    
    # Warmup session before uploads
    if videos_to_upload:
        uploader._warmup_session()
        uploader._human_delay(2.0, 4.0)
    
    # Upload videos
    logger.info("=" * 60)
    logger.info("🎬 UPLOADING VIDEOS TO YOUTUBE")
    logger.info("=" * 60)
    
    uploaded = []
    failed = []
    
    for video_data in videos_to_upload:
        try:
            video_path = video_data['path']
            title = video_data['title']
            description = video_data['description']
            tags = video_data['tags']
            is_short = video_data['is_short']
            
            logger.info(f"Uploading: {video_path.name} - {title}")
            
            video_id = uploader.upload_video(
                video_path=str(video_path),
                title=title,
                description=description,
                tags=tags,
                privacy_status=privacy_status,
                is_short=is_short
            )
            
            if video_id:
                uploaded.append(str(video_path))
            else:
                failed.append(str(video_path))
            
            # Delay between uploads
            if video_data != videos_to_upload[-1]:  # Not the last video
                delay = random.uniform(delay_between_uploads, delay_between_uploads + 5)
                logger.info(f"⏳ Waiting {delay:.1f}s before next upload...")
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"Failed to upload {video_path.name}: {e}")
            failed.append(str(video_path))
    
    logger.info(f"✅ Videos: {len(uploaded)} uploaded, {len(failed)} failed")
    
    # Move uploaded files
    if uploaded:
        logger.info("=" * 60)
        logger.info("📦 ORGANIZING UPLOADED FILES")
        logger.info("=" * 60)
        
        move_results = move_uploaded_files(
            video_data=videos_to_upload,
            uploaded_videos=uploaded,
            subject=subject,
            run_date=run_date,
            project_root=project_root
        )
        
        logger.info(f"✅ File organization complete: {move_results['videos_moved']} videos moved")
    
    # Combine results
    result = {
        'success': len(failed) == 0,
        'uploaded_count': len(uploaded),
        'failed_count': len(failed),
        'uploaded': uploaded,
        'failed': failed
    }
    
    logger.info("=" * 60)
    logger.info("📊 UPLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Videos: {result['uploaded_count']} uploaded, {result['failed_count']} failed")
    logger.info(f"Status: {'✅ SUCCESS' if result['success'] else '⚠️  PARTIAL'}")
    
    return result


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
    privacy_status = "public"  # Default to public
    
    # Check for privacy status flag
    if "--private" in sys.argv:
        privacy_status = "private"
    elif "--unlisted" in sys.argv:
        privacy_status = "unlisted"
    
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg not in ["--test", "--private", "--unlisted"]:
            metadata_override = first_arg
    
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
    logger.info(f"Privacy status: {privacy_status}")
    
    # Test mode: validate files without uploading
    if test_mode:
        logger.info("=" * 60)
        logger.info("🧪 TEST MODE: Validating video files")
        logger.info("=" * 60)
        
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            project_root_actual = metadata_file.parent.parent.parent.parent
            questions = metadata.get('questions', [])
            
            video_count = 0
            for q in questions:
                assets = q.get('assets', {})
                video_path = assets.get('combined_reel')
                
                if video_path:
                    vid_path = project_root_actual / video_path if not Path(video_path).is_absolute() else Path(video_path)
                    if vid_path.exists():
                        logger.info(f"✅ Video found: {vid_path.name}")
                        video_count += 1
                    else:
                        logger.warning(f"❌ Video missing: {vid_path}")
            
            logger.info("=" * 60)
            logger.info(f"📊 Test Results: {video_count} videos found")
            logger.info("=" * 60)
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Test mode error: {e}")
            sys.exit(1)
    
    # Upload videos
    logger.info("=" * 60)
    logger.info("📤 STARTING YOUTUBE UPLOAD")
    logger.info("=" * 60)
    
    # Check for client secrets file
    client_secrets = project_root / "client_secrets.json"
    if not client_secrets.exists():
        logger.error(f"Client secrets file not found: {client_secrets}")
        logger.error("Download from: https://console.cloud.google.com/apis/credentials")
        sys.exit(1)
    
    result = upload_from_metadata(
        metadata_file_path=metadata_file,
        client_secrets_file=str(client_secrets),
        privacy_status=privacy_status
    )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)
