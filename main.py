import streamlit as st
import random
from data import SUPPORTED_CERTIFICATIONS, CERTIFICATION_DOMAINS, get_cached_certification_data
import time

# Set page configuration
st.set_page_config(
    page_title="WhizCards💡Certification Flash Cards",
    page_icon="📚",
    layout="wide"
)

# Check for API key
if 'GEMINI_API_KEY' not in st.secrets:
    st.error("Please set the GEMINI_API_KEY in your Streamlit secrets.")
    st.stop()

# Initialize session state for certification data
if 'current_certification_data' not in st.session_state:
    st.session_state.current_certification_data = None

# Custom CSS for modern UI
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .card {
        padding: 2.5rem;
        border-radius: 1.2rem;
        box-shadow: rgba(17, 17, 26, 0.1) 0px 4px 16px, 
                    rgba(17, 17, 26, 0.05) 0px 8px 32px;
        margin: 1.5rem 0;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1.25rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
    }
    .card:hover {
        transform: translateY(-8px);
        box-shadow: rgba(17, 17, 26, 0.1) 0px 8px 24px, 
                    rgba(17, 17, 26, 0.1) 0px 16px 56px;
    }
    .card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
        );
        transition: 0.5s;
    }
    .card:hover::before {
        left: 100%;
    }
    .question-card {
        background: linear-gradient(135deg, #fff9e6 0%, #fff5d6 100%);
        border-left: 5px solid #ffd700;
        color: #dc3545;
    }
    .answer-card {
        background: linear-gradient(135deg, #e6ffe6 0%, #d6ffd6 100%);
        border-left: 5px solid #4CAF50;
    }
    .answer-card[style*="background-color: #f0f0f0"] {
        background: linear-gradient(135deg, #f0f0f0 0%, #e6e6e6 100%);
        border-left: 5px solid #9e9e9e;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 600;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    h3 {
        color: #34495e;
        margin: 1.5rem 0;
        font-weight: 500;
    }
    .stSelectbox {
        margin-bottom: 1.5rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 0.8rem;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none !important;
        background-size: 200% auto !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    /* Navigation buttons (Previous/Next) styling */
    div[data-testid="column"]:has(button:contains("Previous")), 
    div[data-testid="column"]:has(button:contains("Next")) {
        padding: 0.5rem;
    }
    div[data-testid="column"]:has(button:contains("Previous")) button,
    div[data-testid="column"]:has(button:contains("Next")) button {
        background: linear-gradient(45deg, #3498db, #2980b9, #3498db) !important;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ffffff !important;
    }
    /* Reveal Answer button styling */
    div:has(button:contains("Reveal Answer")) button {
        background: linear-gradient(45deg, #2ecc71, #27ae60, #2ecc71) !important;
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ffffff !important;
    }
    /* Show Question button styling */
    div:has(button:contains("Show Question")) button {
        background: linear-gradient(45deg, #e74c3c, #c0392b, #e74c3c) !important;
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ffffff !important;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        background-position: right center !important;
        opacity: 0.95;
    }
    .stButton button:active {
        transform: translateY(0px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(0,0,0,0.1), transparent);
    }
    /* Enhanced Navigation buttons styling */
    .nav-buttons {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .nav-button {
        background: linear-gradient(135deg, #3498db, #2980b9) !important;
        color: white !important;
        padding: 0.8rem 1.8rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: none !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.5rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2) !important;
    }
    .nav-button-disabled {
        background: #f0f0f0 !important;
        color: #cccccc !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        border: 1px solid #e0e0e0 !important;
    }
    .nav-button:not(.nav-button-disabled):hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(52, 152, 219, 0.3) !important;
    }
    .nav-button:not(.nav-button-disabled):active {
        transform: translateY(0px);
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.2) !important;
    }
    .card-counter {
        font-size: 1.2rem;
        font-weight: 500;
        color: #2c3e50;
        text-align: center;
        padding: 0.5rem;
        background: rgba(52, 152, 219, 0.1);
        border-radius: 12px;
        margin: 0 1rem;
    }
    .clickable-card {
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .clickable-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.15);
    }
    .tooltip {
        position: relative;
        display: inline-block;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    /* Loading animation styles */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    .loading-container {
        text-align: center;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 600px;
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    .loading-emoji {
        font-size: 3rem;
        margin: 1rem;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    .loading-message {
        font-size: 1.2rem;
        color: #2c3e50;
        margin: 1rem 0;
        font-weight: 500;
    }
    .loading-submessage {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("📚WhizCards💡Prep Flash Cards")
st.markdown("---")

# Initialize session states if not exists
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.cards = None
    st.session_state.revealed_answers = set()
    st.session_state.current_card_index = 0
    st.session_state.show_answer = False
    st.session_state.last_cert = None
    st.session_state.last_domain = None

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    # Add view mode selection
    view_mode = st.radio(
        "Select View Mode",
        ["Two Column View", "Carousel View"]
    )
    
    # Certification selection
    selected_cert = st.selectbox(
        "Select Certification",
        SUPPORTED_CERTIFICATIONS,
        key='cert_select'
    )
    
    # Domain selection from predefined domains
    selected_domain = None
    if selected_cert:
        domains = CERTIFICATION_DOMAINS[selected_cert]
        selected_domain = st.selectbox(
            "Select Domain",
            domains,
            key='domain_select'
        )
    
    # Number of cards selection
    num_cards = st.selectbox(
        "Number of Cards",
        [3, 5, 10]
    )

# Main content
if selected_cert and selected_domain:
    # Initialize session states if not exists
    if 'cards' not in st.session_state:
        st.session_state.cards = None
    if 'revealed_answers' not in st.session_state:
        st.session_state.revealed_answers = set()
    if 'current_card_index' not in st.session_state:
        st.session_state.current_card_index = 0
    if 'show_answer' not in st.session_state:
        st.session_state.show_answer = False

    # Add a load button
    if st.button("Show Me Flash Cards", type="primary"):
        st.session_state.initialized = True
        # Reset states when explicitly loading new cards
        if (st.session_state.last_cert != selected_cert or 
            st.session_state.last_domain != selected_domain):
            st.session_state.revealed_answers = set()
            st.session_state.current_card_index = 0
            st.session_state.show_answer = False
        
        with st.spinner(f"Whizlabs is Generating flash cards for {selected_domain}..."):
            st.session_state.cards = get_cached_certification_data(
                selected_cert, selected_domain, num_cards
            )
            st.session_state.last_cert = selected_cert
            st.session_state.last_domain = selected_domain

# Main content
if st.session_state.initialized and st.session_state.cards:
    if not st.session_state.cards:
        st.warning("No flash cards could be generated for this domain. Please try another domain or certification.")
        st.stop()
    
    selected_cards = st.session_state.cards
    
    if view_mode == "Two Column View":
        for i, card in enumerate(selected_cards, 1):
            st.markdown(f"### Card {i}")
            
            # Create columns for the card
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(
                    f"""
                    <div class="card question-card">
                        {card['question']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col2:
                # Make the answer card clickable
                card_id = f"card_{i}"
                if card_id not in st.session_state.revealed_answers:
                    # Show clickable placeholder with tooltip
                    if st.button(
                        "Click Me to reveal answer",
                        key=f"reveal_{i}",
                        help="Click here to reveal the answer",
                        type="secondary"
                    ):
                        st.session_state.revealed_answers.add(card_id)
                        st.rerun()
                    
                    # Show placeholder card with instruction
                    st.markdown(
                        f"""
                        <div class="card answer-card" style="background-color: #f0f0f0; cursor: pointer;">
                            Click to reveal the answer
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    # Show revealed answer
                    st.markdown(
                        f"""
                        <div class="card answer-card">
                            {card['answer']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            st.markdown("---")
    else:  # Carousel View
        # Ensure current_card_index is within bounds
        if st.session_state.current_card_index >= len(selected_cards):
            st.session_state.current_card_index = 0
        
        # Navigation buttons
        st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_card_index > 0:
                if st.button("← Previous", key="prev_btn", help="Go to previous card"):
                    st.session_state.current_card_index -= 1
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                st.markdown(
                    '<button class="nav-button nav-button-disabled" disabled>← Previous</button>',
                    unsafe_allow_html=True
                )
        
        # Display current card number with enhanced styling
        with col2:
            if selected_cards:  # Only show counter if we have cards
                st.markdown(
                    f'<div class="card-counter">Card {st.session_state.current_card_index + 1} of {len(selected_cards)}</div>',
                    unsafe_allow_html=True
                )
        
        with col3:
            if st.session_state.current_card_index < len(selected_cards) - 1:
                if st.button("Next →", key="next_btn", help="Go to next card"):
                    st.session_state.current_card_index += 1
                    st.session_state.show_answer = False
                    st.rerun()
            else:
                st.markdown(
                    '<button class="nav-button nav-button-disabled" disabled>← Next</button>',
                    unsafe_allow_html=True
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Safely get current card
        if 0 <= st.session_state.current_card_index < len(selected_cards):
            current_card = selected_cards[st.session_state.current_card_index]
            
            # Create columns for better button placement
            content_col, button_col = st.columns([3, 1])
            
            with content_col:
                if not st.session_state.show_answer:
                    st.markdown(
                        f"""
                        <div class="card question-card">
                            {current_card['question']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="card answer-card">
                            {current_card['answer']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            with button_col:
                # Make the answer card clickable
                if not st.session_state.show_answer:
                    if st.button("Click to reveal", key="reveal_carousel", help="Click to reveal the answer"):
                        st.session_state.show_answer = True
                        st.rerun()
                else:
                    if st.button("Show question", key="hide_carousel", help="Click to show the question"):
                        st.session_state.show_answer = False
                        st.rerun()
        else:
            st.error("An error occurred while displaying the card. Please try refreshing the page.")
else:
    # Show instructions when cards haven't been loaded
    st.info("👆 Select your preferences in the sidebar and click 'Load Flash Cards' to start studying!")

# Footer
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Whizlabs ❤️ for certification preparation
</div>
""", unsafe_allow_html=True) 