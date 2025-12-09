import streamlit as st
from database.models import db
import time

class Authenticator:
    def __init__(self):
        self.db = db
    
    def show_login_page(self):
        st.title("🔐 Team Optimizer AI")
        st.markdown("### Sign in to access your team dashboard")
        
        # Create tabs for Login and Signup
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            self.login_form()
        
        with tab2:
            self.signup_form()
    
    def login_form(self):
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if not email or not password:
                    st.error("Please fill in all fields")
                    return
                
                user = self.db.authenticate_user(email, password)
                
                if user:
                    # Set session state
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success("Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid email or password")
    
    def signup_form(self):
        with st.form("signup_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Username*")
                email = st.text_input("Email*")
            
            with col2:
                password = st.text_input("Password*", type="password")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            team_option = st.radio("Team Options", 
                                ["Create New Team", "Join Existing Team", "Skip for now"],
                                help="You can always join/create team later in settings")
            
            team_info = None
            
            if team_option == "Create New Team":
                team_name = st.text_input("Team Name*", placeholder="Enter your team name")
                team_info = {'action': 'create', 'name': team_name}
            
            elif team_option == "Join Existing Team":
                team_code = st.text_input("Team Code*", 
                                        placeholder="Enter team code shared by admin",
                                        help="Ask your team admin for the team code")
                team_info = {'action': 'join', 'code': team_code}
            
            signup_button = st.form_submit_button("Create Account")
            
            if signup_button:
                # Validation
                if not all([username, email, password, confirm_password]):
                    st.error("Please fill in all required fields (*)")
                    return
                
                if password != confirm_password:
                    st.error("Passwords do not match")
                    return
                
                if len(password) < 6:
                    st.error("Password must be at least 6 characters")
                    return
                
                try:
                    # Create user first
                    user_id = self.db.create_user(username, email, password)
                    
                    # Handle team
                    if team_option == "Create New Team":
                        if not team_name:
                            st.error("Team name is required")
                            return
                        
                        result = self.db.create_team(team_name, user_id)
                        if result['success']:
                            st.success(f"✅ Account created! Team '{team_name}' has been created.")
                            st.info(f"**Team Code:** `{result['team_code']}`")
                            st.info("Share this code with your team members so they can join!")
                        else:
                            st.error(f"Error creating team: {result.get('error', 'Unknown error')}")
                            return
                    
                    elif team_option == "Join Existing Team":
                        if not team_code:
                            st.error("Team code is required")
                            return
                        
                        # Try to extract team ID from code
                        try:
                            if team_code.startswith("TEAM-"):
                                # Extract numeric ID from code
                                team_id = int(team_code.split('-')[1], 16) % 10000  # Simple extraction
                            else:
                                team_id = int(team_code)  # Assume it's direct team ID
                            
                            success, message = self.db.add_user_to_team(user_id, team_id)
                            if success:
                                st.success(f"✅ Account created! {message}")
                            else:
                                st.warning(f"Account created but could not join team: {message}")
                        except:
                            st.warning("Account created but team code was invalid. You can join a team later in settings.")
                    
                    else:  # Skip for now
                        st.success("✅ Account created successfully!")
                        st.info("You can create or join a team later in the Team Settings page.")
                    
                    # Show login suggestion
                    st.markdown("---")
                    st.info("You can now login with your credentials")
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        st.error("Email or username already exists")
                    else:
                        st.error(f"Error creating account: {str(e)}")
# Create authenticator instance
authenticator = Authenticator()