from typing import List

import pandas as pd
import streamlit as st
from semantha_sdk.model.answer import AnswerReference

import state
from pages_views.abstract_pages import AbstractContentPage


class RetrievalAugmentedGeneration(AbstractContentPage):
    __stop_tokens = ["References:", "Reference:", "Referenzen:", "Referenz:"]

    def __init__(self, page_id: int):
        super().__init__()
        if page_id == 4:
            self._content_placeholder = st.container()
        else:
            self._content_placeholder = st.empty()

    def _display_content(self):
        st.write("Enter your question about ESG and ESG regulations.")
        st.markdown("__A few example questions that can be used for testing:__\n"
                    "* What do we have to be careful of concerning personal data?\n"
                    "* How should ESG solutions adapt to changing demands of stakeholders and regulators?")
        __dummy = ""
        __question = st.text_input(
            key="rag_question",
            label="Search",
            value="",
            placeholder="Enter your question here...",
            label_visibility="collapsed"
        ).strip()
        _, __but_col, _ = st.columns([2, 1, 2])
        __search_button = __but_col.button(disabled=False, label="Search")
        if __search_button or (__dummy != __question):
            if __question == "":
                st.error("Please enter a question!")
            else:
                __dummy = __question
                with st.spinner("Generating an answer to your question..."):
                    __answer = state.get_semantha().generate_retrieval_augmented_answer(__question)
                    self.__display_answer_text(__answer.answer)
                    self.__display_references(__answer.references)

    def __display_answer_text(self, answer: str):
        with st.expander("Answer", expanded=True):
            for swt in self.__stop_tokens:
                answer = answer.split(swt, 1)[0]
            st.markdown(answer)

    def __display_references(self, references: List[AnswerReference]):
        ref_df = pd.DataFrame.from_records(
            [
                [
                    r.name,
                    state.get_semantha().get_tags_of_library_document(r.id)[
                        0] if state.get_semantha().get_tags_of_library_document(r.id) is not None else "",
                    r.content
                ]
                for r in references
            ],
            columns=[
                "Name",
                "Topic",
                "Content"
            ]
        )
        ref_df.index = ref_df.index + 1
        with st.expander("References", expanded=True):
            st.dataframe(ref_df, use_container_width=True)
