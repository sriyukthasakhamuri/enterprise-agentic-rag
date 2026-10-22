import uuid

import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="Enterprise Agentic RAG",
    page_icon="🤖",
    layout="wide",
)


if "session_id" not in st.session_state:
    st.session_state.session_id = str(
        uuid.uuid4()
    )

if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("Enterprise Agentic RAG")

st.caption(
    "Multi-agent enterprise assistant using "
    "LangGraph, Qdrant, SQLite, Redis, and Ollama."
)


with st.sidebar:
    st.subheader("System")

    st.write(
        "Session ID:"
    )

    st.code(
        st.session_state.session_id
    )

    st.write(
        "Capabilities:"
    )

    st.markdown(
        """
- Semantic document retrieval
- SQL analytics
- Parallel hybrid retrieval
- Redis conversation memory
- Query rewriting
- Grounded answer generation
- Confidence evaluation
        """
    )

    if st.button(
        "Clear conversation"
    ):
        try:
            requests.delete(
                f"{API_BASE_URL}/agent/history/"
                f"{st.session_state.session_id}",
                timeout=10,
            )
        except requests.RequestException:
            pass

        st.session_state.messages = []
        st.session_state.session_id = str(
            uuid.uuid4()
        )

        st.rerun()


for message in st.session_state.messages:
    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )


prompt = st.chat_input(
    "Ask an enterprise analytics question..."
)


if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(
            "Analyzing with the agent..."
        ):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/agent/ask",
                    json={
                        "session_id":
                            st.session_state.session_id,
                        "query":
                            prompt,
                    },
                    timeout=120,
                )

                response.raise_for_status()

                result = response.json()

                answer = result.get(
                    "answer",
                    "No answer returned.",
                )

                st.markdown(answer)

                with st.expander(
                    "Agent details"
                ):
                    st.write(
                        "Route:",
                        result.get(
                            "route"
                        ),
                    )

                    st.write(
                        "Confidence:",
                        result.get(
                            "confidence"
                        ),
                    )

                    st.write(
                        "Retry count:",
                        result.get(
                            "retry_count"
                        ),
                    )

                    st.write(
                        "History messages used:",
                        result.get(
                            "history_messages_used"
                        ),
                    )

                    st.write(
                        "SQL results:"
                    )

                    st.json(
                        result.get(
                            "sql_results",
                            {},
                        )
                    )

                    st.write(
                        "Vector results:"
                    )

                    vector_results = (
                        result.get(
                            "vector_results",
                            [],
                        )
                    )

                    for index, item in enumerate(
                        vector_results,
                        start=1,
                    ):
                        st.markdown(
                            f"**{index}.** {item}"
                        )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            except requests.RequestException as error:
                error_message = (
                    "Could not connect to the API. "
                    "Make sure FastAPI is running on "
                    "http://127.0.0.1:8000."
                )

                st.error(
                    error_message
                )

                st.caption(
                    str(error)
                )