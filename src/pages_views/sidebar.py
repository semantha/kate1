from typing import List

import streamlit as st

import state
from pages_views.abstract_pages import AbstractSidebar


class CompareSidebar(AbstractSidebar):
    __THRESHOLD_RELAXED = 0.65
    __THRESHOLD_MEDIUM = 0.7
    __THRESHOLD_STRICT = 0.75
    __THRESHOLD_RELAXED_NAME = 'Relaxed'
    __THRESHOLD_MEDIUM_NAME = 'Medium'
    __THRESHOLD_STRICT_NAME = 'Strict'

    def __init__(self):
        super().__init__()

    def _display_content(self):
        with st.expander("Comparison settings", True):
            __threshold_level = st.radio(
                'Select strictness of comparison',
                [
                    self.__THRESHOLD_STRICT_NAME,
                    self.__THRESHOLD_MEDIUM_NAME,
                    self.__THRESHOLD_RELAXED_NAME
                ],
                key="compare_sidebar_radio",
                index=1
            )
            if __threshold_level == self.__THRESHOLD_RELAXED_NAME:
                state.set_similarity_threshold(self.__THRESHOLD_RELAXED)
            if __threshold_level == self.__THRESHOLD_MEDIUM_NAME:
                state.set_similarity_threshold(self.__THRESHOLD_MEDIUM)
            if __threshold_level == self.__THRESHOLD_STRICT_NAME:
                state.set_similarity_threshold(self.__THRESHOLD_STRICT)

        self._display_extras()

    def _display_extras(self):
        pass


class CompareSidebarWithTagFilter(CompareSidebar):
    def __init__(self):
        super().__init__()
        self.__options = _prepare_lib_tags_as_filter_options()
        self.__default = state.get_selected_tags_compare_view()

    def _display_extras(self):
        if state.get_single_document_with_references()[1] is not None:
            with st.expander("Filter settings", True):
                __selected = st.multiselect(label="Select topics to include in visualizations",
                                            default=self.__default,
                                            options=self.__options,
                                            key="dashboard_sidebar_multiselect")
            __update_button = st.button("Update visualizations")
            if __update_button:
                state.set_selected_tags_compare_view(__selected)


class CompareSidebarWithSnowflakeSettings(CompareSidebar):

    def _display_extras(self):
        with st.expander("Streamlit settings", True):
            st.subheader("Please enter your Snowflake account information below.")
            with st.form("snowflake_settings"):
                sf_dict = state.get_snowflake_cred_dict()
                default_settings_enabled = state.get_default_sf_credentials_enabled()
                if sf_dict["account"] is None or default_settings_enabled:
                    sf_account = st.text_input(key="sf_account", label='Account:')
                else:
                    sf_account = st.text_input(value=sf_dict["account"], key="sf_account", label='Account:')
                if sf_dict["user"] is None or default_settings_enabled:
                    sf_user = st.text_input(key="sf_user", label="User:")
                else:
                    sf_user = st.text_input(value=sf_dict["user"], key="sf_user", label="User:")
                if sf_dict["password"] is None or default_settings_enabled:
                    sf_password = st.text_input(key="sf_password", label="Password:", type="password")
                else:
                    sf_password = st.text_input(value=sf_dict["password"], key="sf_password", label="Password:")
                if sf_dict["role"] is None or default_settings_enabled:
                    sf_role = st.text_input(key="sf_role", label="Role:")
                else:
                    sf_role = st.text_input(value=sf_dict["role"], key="sf_role", label="Role:")
                if sf_dict["warehouse"] is None or default_settings_enabled:
                    sf_warehouse = st.text_input(key="sf_warehouse", label="Warehouse:")
                else:
                    sf_warehouse = st.text_input(value=sf_dict["warehouse"], key="sf_warehouse", label="Warehouse:")
                if sf_dict["database"] is None or default_settings_enabled:
                    sf_database = st.text_input(key="sf_database", label="Database:")
                else:
                    sf_database = st.text_input(value=sf_dict["database"], key="sf_database", label="Database:")
                if sf_dict["schema"] is None or default_settings_enabled:
                    sf_schema = st.text_input(key="sf_schema", label="Schema:")
                else:
                    sf_schema = st.text_input(value=sf_dict["schema"], key="sf_schema", label="Schema:")
                if sf_dict["stage"] is None or default_settings_enabled:
                    sf_stage = st.text_input(key="sf_stage", label="Stage:")
                else:
                    sf_stage = st.text_input(value=sf_dict["stage"], key="sf_stage", label="Stage:")

                submit_button = st.form_submit_button(label='Submit')

                if submit_button:
                    __snow_creds = {
                        'account': sf_account.strip(),
                        'user': sf_user.strip(),
                        'password': sf_password.strip(),
                        'role': sf_role.strip(),
                        'warehouse': sf_warehouse.strip(),
                        'database': sf_database.strip(),
                        'schema': sf_schema.strip(),
                        'stage': sf_stage.strip()
                    }
                    for v in __snow_creds.values():
                        if v:
                            state.set_default_sf_credentials_enabled(False)
                            break
                    state.set_snowflake_cred_dict(__snow_creds)
                    state.set_default_sf_credentials_enabled(False)
            __use_default_sf_account = st.checkbox("Use default Snowflake account (internal use only)")
            if __use_default_sf_account:
                with st.form("semantha_sf_pw"):
                    sf_pw = st.text_input(key="semantha_sf_pw", label="Password:", type="password")
                    pw_submit_button = st.form_submit_button(label='Submit')
                    if pw_submit_button:
                        if sf_pw == st.secrets.semantha.snowflake_password:
                            state.set_snowflake_cred_dict(st.secrets.snowflake.to_dict())
                            state.set_default_sf_credentials_enabled(True)
                            st.success("Successfully loaded default Snowflake account information.")
                        else:
                            st.error("Invalid password.")


class HowToSidebar(AbstractSidebar):

    def _display_content(self):
        st.write("_The sidebar can be used to adjust settings ..._")


def _prepare_lib_tags_as_filter_options() -> List[str]:
    __options = state.get_semantha().get_library_tags()
    if __options is None:
        __options = []
    __options.append(state.NO_TAG)
    return __options
