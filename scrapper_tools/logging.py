import sys
from pathlib import Path
from typing import  Union, TextIO, Text
from dataclasses import dataclass, InitVar, asdict
from loguru import logger

LOG_LEVEL=[
    'TRACE',
    'DEBUG',
    'INFO',
    'SUCCESS',
    'WARNING',
    'ERROR',
    'CRITICAL'
    ]

@dataclass
class LogConfig(object):
    level: InitVar[str]='DEBUG'
    format: str='<green>{time}</green> <level>{message}</level>'
    file: Union[Text, Path, TextIO]=None
    colorize: bool=True
    serialize: bool=False

    def __post_init__(self, level):
        if level in LOG_LEVEL:
            self.level = level
        else:
            self.level = 'DEBUG' # fallback to default

    def config(self):
        d = dict( handlers=[
                    dict(
                        sink=self.file or sys.stdout,
                        level=self.level,
                        format=self.format,
                        colorize=self.colorize,
                        serialize=self.serialize,
                    ),
                  ])
        return d

    def __repr__(self):
        d = ( f"LogConfig(sink={self.file}"
              f", level={self.level}"
              f", format={self.format}"
              f", colorize={self.colorize}"
              f", serialize={self.serialize}"
              )
        return d
