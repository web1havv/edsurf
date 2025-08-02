"""
MoviePy Version Compatibility Layer
Handles different MoviePy API versions automatically
"""
import moviepy
import logging

logger = logging.getLogger(__name__)

# Log the MoviePy version being used
logger.info(f"🎬 MoviePy version: {moviepy.__version__}")

def safe_resize(clip, size):
    """Safely resize a clip regardless of MoviePy version"""
    try:
        if hasattr(clip, 'resized'):
            return clip.resized(size)
        elif hasattr(clip, 'resize'):
            return clip.resize(size)
        else:
            logger.error(f"❌ No resize method found on {type(clip).__name__}")
            raise AttributeError(f"No resize method available on {type(clip).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to resize clip: {str(e)}")
        raise

def safe_set_duration(clip, duration):
    """Safely set duration regardless of MoviePy version"""
    try:
        if hasattr(clip, 'with_duration'):
            return clip.with_duration(duration)
        elif hasattr(clip, 'set_duration'):
            return clip.set_duration(duration)
        else:
            logger.error(f"❌ No duration method found on {type(clip).__name__}")
            raise AttributeError(f"No duration method available on {type(clip).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to set duration: {str(e)}")
        raise

def safe_set_start(clip, start_time):
    """Safely set start time regardless of MoviePy version"""
    try:
        if hasattr(clip, 'with_start'):
            return clip.with_start(start_time)
        elif hasattr(clip, 'set_start'):
            return clip.set_start(start_time)
        else:
            logger.error(f"❌ No start method found on {type(clip).__name__}")
            raise AttributeError(f"No start method available on {type(clip).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to set start time: {str(e)}")
        raise

def safe_set_position(clip, position):
    """Safely set position regardless of MoviePy version"""
    try:
        if hasattr(clip, 'with_position'):
            return clip.with_position(position)
        elif hasattr(clip, 'set_position'):
            return clip.set_position(position)
        else:
            logger.error(f"❌ No position method found on {type(clip).__name__}")
            raise AttributeError(f"No position method available on {type(clip).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to set position: {str(e)}")
        raise

def safe_set_audio(clip, audio):
    """Safely set audio regardless of MoviePy version"""
    try:
        if hasattr(clip, 'with_audio'):
            return clip.with_audio(audio)
        elif hasattr(clip, 'set_audio'):
            return clip.set_audio(audio)
        else:
            logger.error(f"❌ No audio method found on {type(clip).__name__}")
            raise AttributeError(f"No audio method available on {type(clip).__name__}")
    except Exception as e:
        logger.error(f"❌ Failed to set audio: {str(e)}")
        raise

def check_moviepy_compatibility():
    """Check MoviePy compatibility and log available methods"""
    try:
        from moviepy import VideoFileClip, ImageClip
        
        # Test with a simple clip
        import numpy as np
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image_clip = ImageClip(test_frame, duration=1)
        
        logger.info("🔍 MoviePy Compatibility Check:")
        logger.info(f"  Version: {moviepy.__version__}")
        
        # Check available methods
        methods_to_check = ['resize', 'resized', 'set_duration', 'with_duration', 
                           'set_start', 'with_start', 'set_position', 'with_position',
                           'set_audio', 'with_audio']
        
        available_methods = []
        for method in methods_to_check:
            if hasattr(test_image_clip, method):
                available_methods.append(method)
        
        logger.info(f"  Available methods: {available_methods}")
        
        # Test our compatibility functions
        logger.info("✅ MoviePy compatibility layer loaded successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ MoviePy compatibility check failed: {str(e)}")
        return False

# Run compatibility check when module is imported
check_moviepy_compatibility()