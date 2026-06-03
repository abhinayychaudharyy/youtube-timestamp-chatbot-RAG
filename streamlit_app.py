import streamlit as st
import requests

st.set_page_config(page_title="YouTube RAG", page_icon="📺", layout="centered")

st.title("📺 YouTube Video Q&A")
st.write("Ask questions about any YouTube video!")

video_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
question = st.text_input("Your Question", placeholder="What is this video about?")

if st.button("Get Answer"):
    if not video_url or not question:
        st.warning("Please provide both a YouTube URL and a question.")
    else:
        with st.spinner("Analyzing video and generating answer..."):
            try:
                response = requests.post(
                    "http://localhost:8000/chat",
                    json={"video_url": video_url, "question": question}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Success!")
                    
                    st.markdown("### Answer")
                    st.write(data.get("answer"))
                    
                    st.markdown("### Source Timestamp")
                    timestamp = data.get("timestamp")
                    yt_link = data.get("youtube_link")
                    st.markdown(f"[{timestamp}]({yt_link})")
                    
                else:
                    try:
                        error_data = response.json()
                        st.error(f"Error: {error_data.get('detail', 'Unknown error')}")
                    except ValueError:
                        st.error(f"Error {response.status_code}: {response.text}")
                        
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend server. Please make sure the backend is running on http://localhost:8000.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
