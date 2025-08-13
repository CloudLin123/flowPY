"""
文档加载器组件集合
此模块包含各种文档格式的加载器组件
"""

from .pdf_loader import PDFLoaderComponent
from .word_loader import WordLoaderComponent

__all__ = [
    "PDFLoaderComponent",
    "WordLoaderComponent"
]