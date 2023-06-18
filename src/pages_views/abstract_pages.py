import os
from abc import ABC, abstractmethod
from typing import Tuple

import streamlit as st
from PIL import Image
from semantha_sdk.model.document import Document
from semantha_sdk.model.paragraph import Paragraph
from semantha_sdk.model.reference import Reference


class AbstractPage(ABC):

    @abstractmethod
    def display_page(self):
        pass

    @abstractmethod
    def _display_content(self):
        pass


class AbstractContentPage(AbstractPage, ABC):

    _content_placeholder: st.container

    def display_page(self):
        self.__display_logo()
        self._content_placeholder.empty()
        with self._content_placeholder.container():
            self._display_content()

    @staticmethod
    def __display_logo():
        _, _, _, text, logo = st.columns(5)
        with text:
            st.markdown("<h4 style='text-align: right'>brought to you by</h4>", unsafe_allow_html=True)

        with logo:
            image = Image.open(os.path.join(os.path.dirname(__file__), "..", "images", "Semantha-positiv-RGB.png"))
            st.image(image, width=250)

            st.write(
                """<style>
                [data-testid="stHorizontalBlock"] {
                    align-items: center;
                }
                </style>
                """,
                unsafe_allow_html=True
            )


class AbstractViewPage(AbstractContentPage, ABC):

    @abstractmethod
    def _display_single_match(self, doc: Document):
        pass

    @abstractmethod
    def _display_multi_matches(self, docs: list):
        pass


class AbstractSidebar(AbstractPage, ABC):

    def __init__(self):
        self._content_placeholder = st.empty()

    def display_page(self):
        self._content_placeholder.empty()
        with self._content_placeholder.container():
            with st.sidebar:
                st.header("⚙️ Settings")
                self._display_content()
