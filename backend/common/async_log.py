import logging
from logging.handlers import RotatingFileHandler
import sys
import asyncio
import os
from common import WORK_DIR

# Optional: Use asyncio-friendly formatter
class AsyncFormatter(logging.Formatter):
    def format(self, record):
        # Add current task name if in asyncio context
        try:
            loop = asyncio.get_running_loop()
            current_task = asyncio.current_task(loop)
            if current_task:
                task_name = current_task.get_name()
                record.taskname = f"[{task_name}]"
            else:
                record.taskname = "[ASYNC]"
        except RuntimeError:
            # No running loop
             record.taskname = "[SYNC]"
        
        return super().format(record)

# Optional: Async-safe file handler using thread pool (for high throughput)
# Uncomment if logging 1000s of messages/sec and notice blocking
# from concurrent.futures import ThreadPoolExecutor
# executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="log_writer")
# 
# class AsyncFileHandler(logging.Handler):
#     def __init__(self, filename, executor):
#         super().__init__()
#         self.filename = filename
#         self.executor = executor
#         self.formatter = formatter
#     
#     def emit(self, record):
#         try:
#             msg = self.format(record)
#             loop = asyncio.get_running_loop()
#             loop.run_in_executor(self.executor, self._write_log, msg)
#         except Exception:
#             self.handleError(record)
#     
#     def _write_log(self, msg):
#         with open(self.filename, 'a', encoding='utf-8') as f:
#             f.write(msg + '\n')


class AsyncLogger:
    """Async-safe Log class with info, debug, error methods"""
    def __init__(self) -> None:
        self.prefix = ''
        self.log_sqlalchemy = ''
        self.log_folder = os.path.join(WORK_DIR, 'logs')
        self.logger = None

    def init(self, prefix: str, log_sqlalchemy: str | None = None) -> None:
        self.prefix = prefix
        if log_sqlalchemy is not None:
            self.log_sqlalchemy = log_sqlalchemy
        self.logger = None
        os.makedirs(self.log_folder, exist_ok=True)

        self.formatter = AsyncFormatter(f'%(asctime)s - %(levelname)s {self.prefix} %(taskname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        # Create handlers for each log level
        log_path__info = os.path.join(self.log_folder, f'{self.prefix}.info.log')
        self.info_handler = RotatingFileHandler(log_path__info, mode='a', encoding='utf-8', maxBytes=10_000_000, backupCount=2)
        self.info_handler.setLevel(logging.INFO)
        self.info_handler.setFormatter(self.formatter)

        log_path__debug = os.path.join(self.log_folder, f'{self.prefix}.debug.log')
        self.debug_handler = RotatingFileHandler(log_path__debug, mode='a', encoding='utf-8', maxBytes=10_000_000, backupCount=2)
        self.debug_handler.setLevel(logging.DEBUG)
        self.debug_handler.setFormatter(self.formatter)

        log_path__error = os.path.join(self.log_folder, f'{self.prefix}.error.log')
        self.error_handler = RotatingFileHandler(log_path__error, mode='a', encoding='utf-8', maxBytes=10_000_000, backupCount=2)
        self.error_handler.setLevel(logging.ERROR)
        self.error_handler.setFormatter(self.formatter)

        # Console handler
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(logging.INFO)
        self.console_handler.setFormatter(self.formatter)

        # Create main logger
        self.logger = logging.getLogger(f'{self.prefix}_logger')
        self.logger.setLevel(logging.DEBUG)

        # Add handlers
        self.logger.addHandler(self.info_handler)
        self.logger.addHandler(self.debug_handler)
        self.logger.addHandler(self.error_handler)
        self.logger.addHandler(self.console_handler)
        self.logger.propagate = False

        if self.log_sqlalchemy:
            self.enable_sqlalchemy_logging(level_str=self.log_sqlalchemy)

    def enable_sqlalchemy_logging(self, level_str: str):
        """Enable SQLAlchemy logging for async or sync engines"""
        sqlalchemy_loggers = [
            'sqlalchemy.engine',
            'sqlalchemy.pool',
            'sqlalchemy.dialects',
            'sqlalchemy.orm',
            'sqlalchemy.engine.Engine',
        ]
        log_level = {
            'NOTSET': logging.NOTSET,
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.FATAL
            
        }.get(level_str, logging.INFO)
        
        for name in sqlalchemy_loggers:
            sa_logger = logging.getLogger(name)
            sa_logger.setLevel(log_level)
            sa_logger.propagate = False
            sa_logger.handlers.clear()
            sa_logger.addHandler(self.info_handler)
            sa_logger.addHandler(self.debug_handler)
            sa_logger.addHandler(self.error_handler)
            sa_logger.addHandler(self.console_handler)

    # Optional: Set task names for better async debugging
    async def set_task_name(self, name: str):
        """Helper to set current task name for logging"""
        try:
            current_task = asyncio.current_task()
            if current_task:
                current_task.set_name(name)
        except Exception:
            pass

    def info(self, msg: str, *args, **kwargs):
        if not self.logger:
            print(msg)
            return
        try:
            self.logger.info(msg, *args, **kwargs)
        except Exception:
            print(msg)
    
    def debug(self, msg: str, *args, **kwargs):
        if not self.logger:
            return
        try:
            self.logger.debug(msg, *args, **kwargs)
        except Exception:
            pass
    
    def error(self, msg: str, *args, **kwargs):
        if not self.logger:
            print(msg)
            return
        try:
            self.logger.error(msg, *args, **kwargs)
        except Exception:
            pass
