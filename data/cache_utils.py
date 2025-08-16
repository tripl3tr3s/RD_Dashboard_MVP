import streamlit as st
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable
from functools import wraps

def cache_data(ttl: int = 3600):
    """
    Decorator for caching function results with TTL (Time To Live)
    
    Args:
        ttl: Time to live in seconds (default 300 = 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = f"{func.__name__}_{str(args)}_{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Check if we have cached data
            if hasattr(st.session_state, f"cache_{cache_key}"):
                cached_item = getattr(st.session_state, f"cache_{cache_key}")
                
                # Check if cache is still valid
                if datetime.now() < cached_item['expires_at']:
                    return cached_item['data']
            
            # Cache miss or expired, call the function
            try:
                result = func(*args, **kwargs)
                
                # Store in cache with expiration time
                cache_item = {
                    'data': result,
                    'created_at': datetime.now(),
                    'expires_at': datetime.now() + timedelta(seconds=ttl)
                }
                
                setattr(st.session_state, f"cache_{cache_key}", cache_item)
                return result
                
            except Exception as e:
                # If function fails and we have expired cache, return it anyway
                if hasattr(st.session_state, f"cache_{cache_key}"):
                    cached_item = getattr(st.session_state, f"cache_{cache_key}")
                    print(f"Using expired cache due to error: {e}")
                    return cached_item['data']
                raise e
        
        return wrapper
    return decorator

def clear_cache(pattern: str = None):
    """
    Clear cached data
    
    Args:
        pattern: If provided, only clear cache keys containing this pattern
    """
    keys_to_remove = []
    
    for key in st.session_state.keys():
        if key.startswith('cache_'):
            if pattern is None or pattern in key:
                keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

def get_cache_info() -> dict:
    """
    Get information about current cache state
    
    Returns:
        Dictionary with cache statistics
    """
    cache_keys = [key for key in st.session_state.keys() if key.startswith('cache_')]
    
    total_items = len(cache_keys)
    expired_items = 0
    
    for key in cache_keys:
        cached_item = getattr(st.session_state, key)
        if datetime.now() > cached_item['expires_at']:
            expired_items += 1
    
    return {
        'total_items': total_items,
        'active_items': total_items - expired_items,
        'expired_items': expired_items
    }

# Streamlit cache decorators for specific use cases
@st.cache_data(ttl=300, show_spinner=False)
def cached_api_call(url: str, params: dict = None, headers: dict = None) -> Any:
    """
    Generic cached API call function
    
    Args:
        url: API endpoint URL
        params: Query parameters
        headers: Request headers
        
    Returns:
        API response data
    """
    import requests
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API call failed: {e}")
        return None