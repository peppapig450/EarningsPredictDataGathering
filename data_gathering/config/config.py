from datetime import date
import yaml
import threading
import argparse
import os

class Config:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                cls._instance = super().__new__(cls)
                cls._instance._config = cls._load_config()
                cls._instance._parse_args()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        