import streamlit as st

st.set_page_config(page_title="Parmeet Singh", page_icon="📚", layout="wide")

col1, col2 = st.columns([0.8, 2.2])

with col1:
    # Show profile image as a circle without Base64
    st.markdown(
        """
        <style>
        .profile-pic {
            border-radius: 50%;
            width: 200px;
        }
        </style>
        <img src="parmeet.jpeg" class="profile-pic">
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.title(" Greetings, I am Parmeet Singh")
    st.write(
    """
    I am an **Agentic AI Engineer**, specializing in building intelligent and autonomous systems.  
    My expertise includes:  

    - **Autonomous Agents** that act beyond simple responses  
    - **Retrieval-Augmented Generation (RAG) Pipelines** for grounded knowledge access  
    - **Multi-Agent Workflows** powered by LangChain, CrewAI, AutoGen, and LangGraph  
    - **MCP (Model Context Protocol) Servers** that connect models with real-world tools  
    - Advanced applications built with the **OpenAI SDK**
    """
)

st.markdown("---")
st.subheader("Explore My Labs")
st.link_button("Go to Labs →", "/Labs")
st.write("Check out the **Labs** section in the sidebar to try my interactive AI projects.")