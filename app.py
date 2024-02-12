import streamlit as st
from graph import app as langgraph_app
from random import randint
from langchain_core.messages import HumanMessage, FunctionMessage, AIMessage
import threading

st.header("Human in the Loop with checkpoint demo! 🔁")


if "langraph_thread_id" not in st.session_state:
    st.session_state["langgraph_thread_id"] = threading.get_ident()

if "my_messages" not in st.session_state:
    st.session_state["my_messages"] = []

if "approve_resuested" not in st.session_state:
    st.session_state["approve_resuested"] = False

if "approve_granted" not in st.session_state:
    st.session_state["approve_granted"] = False

# st.write(st.session_state)
left, _, right = st.columns([80, 2, 18])

with right:
    st.write(st.session_state["langgraph_thread_id"])

graph_inputs = None

with left:
    chat_container = st.container(height=625)
    prompt = st.chat_input("Say something")

    if prompt:
        print(f"PROMPT NOT EMPTY!!!! {prompt}")
        graph_inputs = [HumanMessage(content=prompt)]
        st.session_state["my_messages"].extend(graph_inputs)

if graph_inputs is not None or (
    st.session_state["approve_resuested"] and st.session_state["approve_granted"]
):
    st.session_state["approve_resuested"] = False
    st.session_state["approve_granted"] = False
    for event in langgraph_app.stream(
        graph_inputs,
        {"configurable": {"thread_id": st.session_state.langgraph_thread_id}},
    ):
        for key, value in event.items():
            if isinstance(value, FunctionMessage):
                st.session_state.my_messages.append(value)
            elif isinstance(value, AIMessage):
                if "function_call" in value.additional_kwargs:
                    st.session_state["approve_resuested"] = True
                st.session_state.my_messages.append(value)
            else:
                st.write("§§§§§§§§§§§")
                st.write(key)
                st.write("----------")
                st.write(value)
                st.write("<<<<<<<<<<<<<")
with left:
    for message in st.session_state["my_messages"]:
        if isinstance(message, HumanMessage):
            with chat_container.chat_message("human"):
                st.write(message.content)
        elif isinstance(message, FunctionMessage):
            with chat_container.chat_message("assistant", avatar="🦾"):
                st.write(str(message)[:500])
        elif isinstance(message, AIMessage):
            with chat_container.chat_message("assistant", avatar="🤖"):
                st.write(message.content)
        else:
            st.write("AAAAAAA")
            st.write(message)


with right:
    if st.session_state["approve_resuested"]:
        st.write(st.session_state["my_messages"][-1])
        with st.form("approve_form"):
            user_answer = st.checkbox("APPROVE ACTION?")
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.session_state["approve_granted"] = user_answer
                st.rerun()
