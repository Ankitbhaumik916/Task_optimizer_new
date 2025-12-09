import streamlit as st
from database.models import db
import time

st.set_page_config(page_title="Team Management", page_icon="👥")

def show_create_team(user_id):
    """Create new team - ULTRA SIMPLE"""
    st.subheader("Create New Team")
    
    team_name = st.text_input("Team Name", placeholder="Enter team name")
    
    if st.button("Create Team", type="primary"):
        if not team_name:
            st.error("Team name required")
            return
        
        with st.spinner("Creating..."):
            try:
                # Simple create team call
                team_id = db.create_team(team_name, user_id)
                
                if team_id:
                    st.session_state.user['team_id'] = team_id
                    st.success(f"✅ Team '{team_name}' created!")
                    
                    # Generate simple code
                    code = f"TEAM{team_id}"
                    st.info(f"**Team ID:** `{team_id}`")
                    st.info(f"**Share this ID with members**")
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create team")
            except Exception as e:
                st.error(f"Error: {str(e)}")

def show_join_team(user_id):
    """Join team - ULTRA SIMPLE"""
    st.subheader("Join Team")
    
    # Get all teams (simple query)
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM teams')
    teams = cursor.fetchall()
    conn.close()
    
    if not teams:
        st.info("No teams exist yet. Create one!")
        if st.button("Create Team Instead"):
            st.session_state.active_tab = "Create Team"
            st.rerun()
        return
    
    st.write(f"**Available Teams ({len(teams)}):**")
    
    for team_id, team_name in teams:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write(f"**{team_name}**")
            st.caption(f"ID: {team_id}")
        
        with col2:
            if st.button("Join", key=f"join_{team_id}"):
                join_team_simple(user_id, team_id, team_name)
        
        st.markdown("---")

def join_team_simple(user_id, team_id, team_name):
    """Simple team join"""
    with st.spinner("Joining..."):
        # Check if already in a team
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT team_id FROM users WHERE id = ?', (user_id,))
        current_team = cursor.fetchone()
        
        if current_team and current_team[0]:
            if current_team[0] == team_id:
                st.warning("You're already in this team!")
                conn.close()
                return
            else:
                st.warning(f"You're already in another team (ID: {current_team[0]})")
                conn.close()
                return
        
        # Join team
        cursor.execute('UPDATE users SET team_id = ? WHERE id = ?', (team_id, user_id))
        conn.commit()
        
        # Get admin info
        cursor.execute('''
            SELECT u.username 
            FROM teams t
            JOIN users u ON t.created_by = u.id
            WHERE t.id = ?
        ''', (team_id,))
        admin = cursor.fetchone()
        conn.close()
        
        st.session_state.user['team_id'] = team_id
        st.success(f"✅ Joined **{team_name}**!")
        
        if admin:
            st.info(f"👑 Admin: {admin[0]}")
        
        time.sleep(1)
        st.rerun()

def show_team_overview(team_id, user_id):
    """Simple team overview"""
    # Get team info
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, created_at FROM teams WHERE id = ?', (team_id,))
    team = cursor.fetchone()
    
    if not team:
        st.error("Team not found")
        return
    
    team_name, created_at = team
    
    # Get members
    cursor.execute('''
        SELECT id, username, email, role 
        FROM users 
        WHERE team_id = ? 
        ORDER BY 
            CASE role 
                WHEN 'admin' THEN 1
                ELSE 2
            END,
            username
    ''', (team_id,))
    
    members = cursor.fetchall()
    conn.close()
    
    # Display
    st.subheader(f"🏢 {team_name}")
    st.caption(f"Created: {created_at}")
    
    st.metric("Total Members", len(members))
    
    st.markdown("---")
    st.subheader("👥 Team Members")
    
    for member_id, username, email, role in members:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            role_icon = "👑" if role == 'admin' else "👤"
            st.write(f"{role_icon} **{username}**")
            st.caption(email)
        
        with col2:
            st.caption(role.title())
        
        with col3:
            if member_id == user_id:
                st.caption("You")
        
        st.markdown("---")

def show_invite_members(team_id):
    """Simple invite page"""
    st.subheader("Invite Members")
    
    # Get team name
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM teams WHERE id = ?', (team_id,))
    team_name = cursor.fetchone()[0]
    conn.close()
    
    st.write(f"**Team:** {team_name}")
    st.write(f"**Team ID:** `{team_id}`")
    
    st.markdown("---")
    
    st.info("**How to invite:**")
    st.write("1. Share the **Team ID** above with members")
    st.write("2. They go to **Team Management → Join Team**")
    st.write("3. They click 'Join' next to your team")
    
    st.markdown("---")
    
    # Quick share
    st.write("**Quick share message:**")
    share_text = f"""Join my team '{team_name}' on Team Optimizer AI!

Team ID: {team_id}

Go to Team Management → Join Team and select our team."""
    
    st.code(share_text, language="")
    
    if st.button("📋 Copy Message"):
        st.success("Copied to clipboard!")

def show_member_management(team_id, user_id):
    """Simple member management"""
    st.subheader("Manage Members")
    
    # Check if user is admin
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT role FROM users WHERE id = ? AND team_id = ?', (user_id, team_id))
    user_role = cursor.fetchone()
    
    if not user_role or user_role[0] != 'admin':
        st.warning("Only admins can manage members")
        conn.close()
        return
    
    # Get members
    cursor.execute('''
        SELECT id, username, email, role 
        FROM users 
        WHERE team_id = ?
        ORDER BY username
    ''', (team_id,))
    
    members = cursor.fetchall()
    conn.close()
    
    if not members:
        st.info("No members")
        return
    
    for member_id, username, email, role in members:
        with st.expander(f"{username} ({role})", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if member_id == user_id:
                    st.write("**Role:** Admin (You)")
                else:
                    new_role = st.selectbox(
                        "Change role",
                        ["member", "admin"],
                        index=0 if role == 'member' else 1,
                        key=f"role_{member_id}"
                    )
                    
                    if new_role != role:
                        if st.button("Update", key=f"update_{member_id}"):
                            conn = db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET role = ? WHERE id = ?', 
                                         (new_role, member_id))
                            conn.commit()
                            conn.close()
                            st.success(f"Updated {username} to {new_role}")
                            time.sleep(1)
                            st.rerun()
            
            with col2:
                if member_id != user_id:
                    if st.button("Remove", type="secondary", key=f"remove_{member_id}"):
                        if st.checkbox(f"Remove {username}?", key=f"confirm_{member_id}"):
                            conn = db.get_connection()
                            cursor = conn.cursor()
                            cursor.execute('UPDATE users SET team_id = NULL WHERE id = ?', 
                                         (member_id,))
                            conn.commit()
                            conn.close()
                            st.success(f"Removed {username}")
                            time.sleep(1)
                            st.rerun()

def main():
    if not st.session_state.get("authenticated", False):
        st.warning("Please login")
        return
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user.get('team_id')
    
    st.title("👥 Team Management")
    
    # Super simple navigation
    if not team_id:
        # Not in a team
        choice = st.radio("What do you want to do?", 
                         ["Create a new team", "Join existing team"])
        
        if choice == "Create a new team":
            show_create_team(user_id)
        else:
            show_join_team(user_id)
    else:
        # In a team
        option = st.selectbox("Team Options",
                             ["Team Overview", "Invite Members", "Manage Members", "Leave Team"])
        
        if option == "Team Overview":
            show_team_overview(team_id, user_id)
        elif option == "Invite Members":
            show_invite_members(team_id)
        elif option == "Manage Members":
            show_member_management(team_id, user_id)
        elif option == "Leave Team":
            st.subheader("Leave Team")
            st.warning("Are you sure you want to leave the team?")
            
            if st.button("Yes, leave team", type="primary"):
                conn = db.get_connection()
                cursor = conn.cursor()
                cursor.execute('UPDATE users SET team_id = NULL WHERE id = ?', (user_id,))
                conn.commit()
                conn.close()
                
                st.session_state.user['team_id'] = None
                st.success("Left team")
                time.sleep(1)
                st.rerun()

if __name__ == "__main__":
    main()