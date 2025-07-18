import streamlit as st
import pandas as pd
from cinema import Cinema

# Page configuration
st.set_page_config(
    page_title="Cinemas",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and apply custom cinema-themed styling
def load_css():
    with open('styles.css', 'r') as f:
        css = f.read()
    return f"<style>{css}</style>"

st.markdown(load_css(), unsafe_allow_html=True)

def init_session_state():
    """Initialize Streamlit session state variables"""
    if 'cinema' not in st.session_state:
        st.session_state.cinema = None
    if 'current_booking' not in st.session_state:
        st.session_state.current_booking = None
    if 'selected_seats' not in st.session_state:
        st.session_state.selected_seats = []
    if 'booking_id' not in st.session_state:
        st.session_state.booking_id = None
    if 'page' not in st.session_state:
        st.session_state.page = 'setup'

def format_seating_map(cinema, current_booking=None):
    """Format the seating map for display in Streamlit with enhanced styling"""
    if not cinema:
        return ""
    
    # Screen header - let CSS handle the centering
    screen_text = "S C R E E N"
    # Create separator line that matches the seating area width
    separator_length = cinema.seats_per_row * 4
    
    seating_display = f'<div class="screen-header">{screen_text}</div>\n'
    seating_display += f'<div style="color: #ffd700; text-align: center; margin-bottom: 20px;">{"═" * separator_length}</div>\n'
    
    # Seating grid with colored seats
    for row_index in range(cinema.rows):
        row_letter = cinema.get_row_letter(row_index)
        line = f'<span style="color: #ffd700; font-weight: bold;">{row_letter}</span>   '

        for col_index in range(cinema.seats_per_row):
            seat_status = cinema.seating_map[row_index][col_index]

            if seat_status == '.':
                line += '<span style="color: #90EE90;">●</span>'  # Available - green
            elif current_booking and seat_status == current_booking:
                line += '<span style="color: #FFD700;">●</span>'  # Selected - gold
            else:
                line += '<span style="color: #FF6B6B;">●</span>'  # Booked - red
            line += "   "
        
        seating_display += line + "\n"
    
    # Column numbers with styling
    line = "    "  # Match the spacing after row letters
    for col in range(1, cinema.seats_per_row + 1):
        if col < 10:
            line += f'<span style="color: #ffd700;">{col}</span>   '
        else:
            line += f'<span style="color: #ffd700;">{col}</span>  '
    seating_display += line
    
    # Wrap in HTML for proper formatting
    return f'<div style="font-family: monospace; line-height: 1.8; text-align: center;">{seating_display}</div>'

def cinema_setup_page():
    """Cinema setup page"""
    st.markdown('<h1 class="cinema-title">Cinema</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #ffd700; text-align: center;">Setup Your Cinema</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; color: #ffffff; font-size: 1.2em; margin: 20px 0;">
    Welcome to Cinema! Please configure your movie session:
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("cinema_setup"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title = st.text_input("Movie Title", placeholder="e.g., Inception")
        
        with col2:
            rows = st.number_input("Number of Rows", min_value=1, max_value=26, value=8)
        
        with col3:
            seats_per_row = st.number_input("Seats per Row", min_value=1, max_value=50, value=10)
        
        submitted = st.form_submit_button("Create Cinema", type="primary")
        
        if submitted:
            if not title:
                st.error("Please enter a movie title")
            else:
                try:
                    cinema = Cinema(title, rows, seats_per_row)
                    st.session_state.cinema = cinema
                    st.session_state.page = 'main'
                    st.success(f"Cinema created successfully! {cinema.total_seats} seats available.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating cinema: {str(e)}")

def main_menu_page():
    """Main menu page"""
    cinema = st.session_state.cinema
    
    st.markdown(f'<h1 class="cinema-title">{cinema.title}</h1>', unsafe_allow_html=True)
    
    # Sidebar with cinema info and navigation
    with st.sidebar:
        st.header("Cinema Information")
        st.info(f"""
        **Movie:** {cinema.title}\n
        **Total Seats:** {cinema.total_seats}\n
        **Available Seats:** {cinema.available_seats}\n
        **Rows:** {cinema.rows} (A-{chr(64 + cinema.rows)})\n
        **Seats per Row:** {cinema.seats_per_row}\n
        """)
        
        st.header("Navigation")
        if st.button("Book Tickets", use_container_width=True):
            st.session_state.page = 'booking'
            st.rerun()
        
        if st.button("Check Bookings", use_container_width=True):
            st.session_state.page = 'check_bookings'
            st.rerun()
        
        if st.button("Reset Cinema", use_container_width=True):
            st.session_state.cinema = None
            st.session_state.page = 'setup'
            st.rerun()
    
    # Main content
    st.markdown('<h2 style="color: #ffd700; text-align: center; margin: 30px 0;">Current Seating Layout</h2>', unsafe_allow_html=True)
    
    # Display seating map
    seating_map = format_seating_map(cinema)
    st.markdown(f'<div class="seat-grid">{seating_map}</div>', unsafe_allow_html=True)
    
    # Legend
    st.markdown("""
    <div class="legend">
    <h4 style="color: #ffd700; margin-bottom: 10px;">Legend:</h4>
    <div style="font-family: 'Courier New', monospace; font-size: 16px;">
    • <span style="color: #90EE90;">.</span> Available seats<br>
    • <span style="color: #FF6B6B;">#</span> Booked seats<br>
    • <span style="color: #FFD700;">o</span> Currently selected seats
    </div>
    </div>
    """, unsafe_allow_html=True)

def booking_page():
    """Ticket booking page"""
    cinema = st.session_state.cinema
    
    st.markdown(f'<h1 class="cinema-title">{cinema.title}</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #ffd700; text-align: center;">Book Your Tickets</h2>', unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("← Back to Main Menu", use_container_width=True):
            st.session_state.page = 'main'
            st.session_state.selected_seats = []
            st.session_state.booking_id = None
            st.rerun()
    
    if cinema.available_seats == 0:
        st.error("Sorry, no seats available!")
        return
    
    # Number of tickets selection
    st.markdown('<h3 style="color: #ffd700;">Select Number of Tickets</h3>', unsafe_allow_html=True)
    num_tickets = st.number_input(
        "How many tickets would you like to book?", 
        min_value=1, 
        max_value=cinema.available_seats, 
        value=1
    )
    
    # Seat allocation method
    st.markdown('<h3 style="color: #ffd700;">Seat Selection</h3>', unsafe_allow_html=True)
    allocation_method = st.radio(
        "Choose allocation method:",
        ["Auto-allocate (recommended)", "Choose starting position"]
    )
    
    # Custom position selection (only show when needed)
    row_letter = None
    seat_number = None
    if allocation_method == "Choose starting position":
        st.markdown("**Select your preferred starting position:**")
        col1, col2 = st.columns(2)
        with col1:
            row_letter = st.selectbox(
                "Starting Row:", 
                [chr(65 + i) for i in range(cinema.rows)][::-1],
                key="row_selector"
            )
        with col2:
            seat_number = st.number_input(
                "Starting Seat:", 
                min_value=1, 
                max_value=cinema.seats_per_row, 
                value=1,
                key="seat_selector"
            )
    
    # Seat allocation
    if st.button("Show Available Seats", type="primary"):
        if allocation_method == "Auto-allocate (recommended)":
            seats = cinema.allocate_default_seats(num_tickets)
        else:
            # Custom position selection
            if row_letter and seat_number:
                row_index = cinema.get_row_index(row_letter)
                col_index = seat_number - 1
                seats = cinema.allocate_seats_from_position(num_tickets, row_index, col_index)
            else:
                st.error("Please select a starting row and seat number.")
                seats = None
        
        if seats:
            st.session_state.selected_seats = seats
            st.session_state.booking_id = cinema.generate_booking_id()
        else:
            st.error("Could not allocate the requested seats. Please try a different number or position.")
    
    # Display selected seats
    if st.session_state.selected_seats:
        st.markdown('<h3 style="color: #ffd700;">Selected Seats</h3>', unsafe_allow_html=True)
        
        # Create temporary booking for display
        temp_booking_id = "TEMP_DISPLAY"
        for row_index, col_index in st.session_state.selected_seats:
            cinema.seating_map[row_index][col_index] = temp_booking_id
        
        seating_map = format_seating_map(cinema, temp_booking_id)
        st.markdown(f'<div class="seat-grid">{seating_map}</div>', unsafe_allow_html=True)
        
        # Reset temporary booking
        for row_index, col_index in st.session_state.selected_seats:
            cinema.seating_map[row_index][col_index] = '.'
        
        # Show booking details
        seat_list = []
        for row_index, col_index in st.session_state.selected_seats:
            row_letter = cinema.get_row_letter(row_index)
            seat_list.append(f"{row_letter}{col_index + 1}")
        
        st.markdown(f"""
        <div class="booking-info">
        <h4>Booking Details</h4>
        <strong>Booking ID:</strong> {st.session_state.booking_id}<br>
        <strong>Movie:</strong> {cinema.title}<br>
        <strong>Number of Tickets:</strong> {len(st.session_state.selected_seats)}<br>
        <strong>Seats:</strong> {', '.join(seat_list)}
        </div>
        """, unsafe_allow_html=True)
        
        # Confirm booking
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Booking", type="primary", use_container_width=True):
                try:
                    cinema.book_seats(st.session_state.selected_seats, st.session_state.booking_id)
                    st.success(f"Booking confirmed! Your booking ID is {st.session_state.booking_id}")
                    st.session_state.selected_seats = []
                    st.session_state.booking_id = None
                    st.session_state.page = 'main'  # Auto-redirect to main menu
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error confirming booking: {str(e)}")
        
        with col2:
            if st.button("Select Different Seats", use_container_width=True):
                st.session_state.selected_seats = []
                st.session_state.booking_id = None
                st.rerun()

def check_bookings_page():
    """Check and manage existing bookings"""
    cinema = st.session_state.cinema
    
    st.markdown(f'<h1 class="cinema-title">{cinema.title}</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #ffd700; text-align: center;">Check Your Bookings</h2>', unsafe_allow_html=True)
    
    with st.sidebar:
        if st.button("← Back to Main Menu", use_container_width=True):
            st.session_state.page = 'main'
            st.rerun()
    
    if not cinema.bookings:
        st.info("No bookings found.")
        return
    
    # Show all bookings
    st.markdown('<h3 style="color: #ffd700;">All Bookings</h3>', unsafe_allow_html=True)
    
    booking_data = []
    for booking_id, seats in cinema.bookings.items():
        seat_list = []
        for row_index, col_index in seats:
            row_letter = cinema.get_row_letter(row_index)
            seat_list.append(f"{row_letter}{col_index + 1}")
        
        booking_data.append({
            "Booking ID": booking_id,
            "Number of Seats": len(seats),
            "Seats": ", ".join(seat_list)
        })
    
    df = pd.DataFrame(booking_data)
    st.dataframe(df, use_container_width=True)
    
    # Check specific booking
    st.markdown('<h3 style="color: #ffd700;">Check Specific Booking</h3>', unsafe_allow_html=True)
    booking_id = st.selectbox("Select Booking ID:", list(cinema.bookings.keys()))
    
    if booking_id:
        # Display seating map with this booking highlighted
        seating_map = format_seating_map(cinema, booking_id)
        st.markdown(f'<div class="seat-grid">{seating_map}</div>', unsafe_allow_html=True)
        
        # Booking details
        seats = cinema.bookings[booking_id]
        seat_list = []
        for row_index, col_index in seats:
            row_letter = cinema.get_row_letter(row_index)
            seat_list.append(f"{row_letter}{col_index + 1}")
        
        st.markdown(f"""
        <div class="booking-info">
        <h4>Booking Details</h4>
        <strong>Booking ID:</strong> {booking_id}<br>
        <strong>Movie:</strong> {cinema.title}<br>
        <strong>Number of Seats:</strong> {len(seats)}<br>
        <strong>Seats:</strong> {', '.join(seat_list)}
        </div>
        """, unsafe_allow_html=True)
        
        # Cancel booking option
        st.markdown('<h3 style="color: #ff6b6b;">Cancel Booking</h3>', unsafe_allow_html=True)
        if st.button(f"Cancel Booking {booking_id}", type="secondary"):
            if cinema.cancel_booking(booking_id):
                st.success(f"Booking {booking_id} has been cancelled successfully!")
                st.rerun()
            else:
                st.error("Failed to cancel booking.")

def main():
    """Main application entry point"""
    init_session_state()
    
    # Route to appropriate page
    if st.session_state.page == 'setup' or st.session_state.cinema is None:
        cinema_setup_page()
    elif st.session_state.page == 'main':
        main_menu_page()
    elif st.session_state.page == 'booking':
        booking_page()
    elif st.session_state.page == 'check_bookings':
        check_bookings_page()

if __name__ == "__main__":
    main() 