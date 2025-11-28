import streamlit as st
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config
st.set_page_config(
    page_title="AutoResearch Agent",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    .stProgress > div > div > div > div {
        background-color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'research_result' not in st.session_state:
    st.session_state.research_result = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'article_generated' not in st.session_state:
    st.session_state.article_generated = False

# Title and description
st.markdown('<h1 class="main-header"> AutoResearch Agent</h1>', unsafe_allow_html=True)
st.markdown("""
<p style="text-align: center; font-size: 1.2rem; color: #666;">
An intelligent agent that automates comprehensive web research and article generation
</p>
""", unsafe_allow_html=True)

# Sidebar for additional options
with st.sidebar:
    st.markdown( "⚙️ Settings")
    
    # API Configuration
    st.markdown("#### API Configuration")
    openai_api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key for GPT-4o access"
    )
    
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # Advanced options
    st.markdown("#### Advanced Options")
    use_custom_title = st.checkbox("Use custom article title", value=False)
    custom_title = ""
    if use_custom_title:
        custom_title = st.text_input("Custom title", placeholder="Enter your custom title here")
    
    article_length = st.select_slider(
        "Article Length",
        options=["Short", "Medium", "Long", "Comprehensive"],
        value="Medium"
    )
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **AutoResearch Agent** uses LangGraph to:
    - Search the web for recent information
    - Analyze from multiple perspectives
    - Generate structured Wikipedia-style articles
    - Fact-check and cite sources
    """)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<h3 class="sub-header"> Research Topic</h3>', unsafe_allow_html=True)
    
    # Topic input
    topic = st.text_area(
        "Enter your research topic:",
        height=100,
        placeholder="e.g., The Impact of Quantum Computing on Cryptography\n\nor\n\nRecent Advances in Renewable Energy Storage\n\nor\n\nThe Future of AI in Healthcare",
        help="Be specific for better results!"
    )
    
    # Research button
    col1_1, col1_2, col1_3 = st.columns([1, 2, 1])
    with col1_2:
        research_button = st.button(
            "🚀 Start Research",
            type="primary",
            use_container_width=True,
            disabled=not topic or st.session_state.is_processing
        )

with col2:
    st.markdown('<h3 class="sub-header"> Research Metrics</h3>', unsafe_allow_html=True)
    
    # Display metrics if research has been done
    if st.session_state.research_result and st.session_state.research_result.get("success"):
        result = st.session_state.research_result
        
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Sources Used", result.get("sources_used", 0))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with metric_cols[1]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Facts Extracted", result.get("research_facts", 0))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with metric_cols[2]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Status", " Success")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Article length
        article_text = result.get("final_article", "")
        word_count = len(article_text.split())
        char_count = len(article_text)
        
        st.markdown(f"**Article Stats:**")
        st.markdown(f"- Words: {word_count}")
        st.markdown(f"- Characters: {char_count}")

# Function to run research
async def run_research_async(topic: str, custom_title: str = None):
    """Run the research asynchronously."""
    try:
        # Import and run the agent
        from main import AutoResearchAgent
        
        agent = AutoResearchAgent()
        result = await agent.research(topic)
        
        # Update custom title if provided
        if custom_title and result.get("success"):
            result["title"] = custom_title
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "topic": topic
        }

def run_research(topic: str, custom_title: str = None):
    """Wrapper to run async research."""
    return asyncio.run(run_research_async(topic, custom_title))

# Handle research button click
if research_button and topic:
    st.session_state.is_processing = True
    
    # Display progress
    progress_bar = st.progress(0, text="Starting research...")
    
    # Create placeholder for status updates
    status_placeholder = st.empty()
    
    # Simulate progress updates
    progress_stages = [
        " Searching the web...",
        " Retrieving content...",
        " Analyzing information...",
        " Generating outline...",
        " Drafting sections...",
        " Synthesizing article...",
        " Final refinement..."
    ]
    
    try:
        for i, stage in enumerate(progress_stages):
            progress = (i + 1) / len(progress_stages)
            progress_bar.progress(progress, text=stage)
            status_placeholder.info(stage)
            
            # Small delay to show progress
            import time
            time.sleep(0.5)
        
        # Run the actual research
        with st.spinner("🚀 Generating your article..."):
            result = run_research(topic, custom_title if use_custom_title else None)
        
        # Store result in session state
        st.session_state.research_result = result
        st.session_state.is_processing = False
        st.session_state.article_generated = True
        
        # Clear progress indicators
        progress_bar.empty()
        status_placeholder.empty()
        
        # Show success message
        st.success(" Research completed successfully!")
        
        # Force a rerun to show results
        st.rerun()
        
    except Exception as e:
        st.error(f" Error during research: {str(e)}")
        st.session_state.is_processing = False

# Display the article if generated
if st.session_state.research_result and st.session_state.research_result.get("success"):
    st.markdown("---")
    st.markdown('<h2 class="sub-header"> Generated Article</h2>', unsafe_allow_html=True)
    
    result = st.session_state.research_result
    
    # Article title
    article_title = result.get("title", f"Research on: {result.get('topic', 'Unknown Topic')}")
    st.markdown(f"### {article_title}")
    
    # Article content in an expandable card
    with st.expander("View Full Article", expanded=True):
        st.markdown('<div class="article-card">', unsafe_allow_html=True)
        st.markdown(result.get("final_article", "No article generated."))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Download button
    article_text = result.get("final_article", "")
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    
    with col_d2:
        st.download_button(
            label=" Download Article",
            data=article_text,
            file_name=f"research_article_{result.get('topic', 'article').replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

# Error display
elif st.session_state.research_result and not st.session_state.research_result.get("success"):
    st.error(f" Research failed: {st.session_state.research_result.get('error', 'Unknown error')}")

# Instructions when no research has been done
elif not st.session_state.article_generated:
    st.markdown("---")
    with st.container():
        st.markdown("###  How to use:")
        col_i1, col_i2, col_i3 = st.columns(3)
        
        with col_i1:
            st.markdown("""
            #### 1. Enter Topic
            - Be specific and clear
            - Use complete sentences
            - Focus on recent developments
            """)
        
        with col_i2:
            st.markdown("""
            #### 2. Configure
            - Set OpenAI API key
            - Adjust advanced options
            - Choose article length
            """)
        
        with col_i3:
            st.markdown("""
            #### 3. Generate
            - Click 'Start Research'
            - Wait for processing
            - View/download results
            """)
    
    # Example topics
    st.markdown("###  Example Topics:")
    examples = [
        "The Impact of Quantum Computing on Cryptography",
        "Recent Advances in Renewable Energy Storage",
        "The Future of Artificial Intelligence in Healthcare",
        "Blockchain Technology in Supply Chain Management",
        "Climate Change and Its Effects on Biodiversity"
    ]
    
    for example in examples:
        if st.button(f"✨ {example}", key=f"example_{example}"):
            st.session_state.example_topic = example
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>AutoResearch Agent • Powered by LangGraph & OpenAI</p>
    <p>Generates comprehensive, cited Wikipedia-style articles from any topic</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Handle example topic selection
if 'example_topic' in st.session_state:
    st.experimental_set_query_params(topic=st.session_state.example_topic)
    del st.session_state.example_topic