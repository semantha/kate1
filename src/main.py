import os

import hydralit_components as hc
import streamlit as st

import state
from pages_views.compare import ComparePage
from pages_views.document_collection import DocumentCollection
from pages_views.howto import HowToPage
from pages_views.rag import RetrievalAugmentedGeneration
from pages_views.sidebar import CompareSidebarWithSnowflakeSettings, HowToSidebar, CompareSidebarWithTagFilter

st.set_page_config(
    page_title="K-A-T-E One",
    page_icon=os.path.join(os.path.dirname(__file__), "images", "favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("<h1 style='text-align: center; background-color: #000045; color: #ece5f6'>K-A-T-E One</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; background-color: #000045; color: #ece5f6'>Knowledge, Access, and Technology for ESG</h4>", unsafe_allow_html=True)

menu_data = [
    {'id': 1, 'label': "How To", 'key': "md_how_to", 'icon': "fa fa-home"},
    {'id': 2, 'label': "Individual Document", 'key': "md_run_analysis"},
    {'id': 3, 'label': "Document Collection", 'key': "md_document_collection"},
    {'id': 4, 'label': "Semantic Q&A", 'key': "md_rag"}
]

state.set_page_id(int(hc.nav_bar(
    menu_definition=menu_data,
    hide_streamlit_markers=False,
    sticky_nav=True,
    sticky_mode='pinned',
    override_theme={'menu_background': '#4c00a5'}
)))


__howto_page = HowToPage(state.get_page_id())
__howto_sidebar = HowToSidebar()
__compare_page = ComparePage(state.get_page_id())
__compare_sidebar = CompareSidebarWithSnowflakeSettings()
__compare_sidebar_with_filter = CompareSidebarWithTagFilter()
__document_collection = DocumentCollection(state.get_page_id())
__rag_page = RetrievalAugmentedGeneration(state.get_page_id())

if state.get_page_id() == 1:
    __howto_page.display_page()
if state.get_page_id() == 2:
    __compare_page.display_page()
    __compare_sidebar_with_filter.display_page()
if state.get_page_id() == 3:
    __compare_sidebar.display_page()
    __document_collection.display_page()
if state.get_page_id() == 4:
    __rag_page.display_page()
