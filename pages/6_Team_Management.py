import streamlit as st
from database.models import db
from database.operations import db_ops
import time

st.set_page_config(page_title="Team Management", page_icon="👥")

def main():
    if not st.session_state.get("authenticated", False):
        st.warning("Please login to access team management")
        return
    
    user_id = st.session_state.user['id']
    team_id = st.session_state.user.get('team_id')
    
    st.title("👥 Team Management")
    
    # Navigation tabs
    tabs = ["Team Overview", "Invite Members", "Member Management", "Team Settings"]
    
    if not team_id:
        tabs = ["Create Team", "Join Team"]
    
    tab = st.radio("Navigation", tabs, horizontal=True, label_visibility="collapsed")
    
    if not team_id:
        if tab == "Create Team":
            show_create_team(user_id)
        elif tab == "Join Team":
            show_join_team(user_id)
    else:
        if tab == "Team Overview":
            show_team_overview(team_id, user_id)
        elif tab == "Invite Members":
            show_invite_members(team_id)
        elif tab == "Member Management":
            show_member_management(team_id, user_id)
        elif tab == "Team Settings":
            show_team_settings(team_id, user_id)

def show_create_team(user_id):
    """Page for creating a new team"""
    st.subheader("Create New Team")
    
    with st.form("create_team_form"):
        team_name = st.text_input("Team Name*", 
                                 placeholder="Enter your team name",
                                 help="Choose a descriptive name for your team")
        
        team_description = st.text_area("Team Description (optional)",
                                       placeholder="Describe your team's purpose or goals")
        
        col1, col2 = st.columns(2)
        with col1:
            default_role = st.selectbox("Default member role", 
                                       ["Member", "Manager", "Viewer"],
                                       help="Default role for new members")
        
        with col2:
            privacy = st.radio("Team Privacy",
                              ["Open - Anyone can join with code", 
                               "Closed - Admin approval required"],
                              index=0)
        
        submitted = st.form_submit_button("Create Team", type="primary")
        
        if submitted:
            if not team_name:
                st.error("Team name is required")
                return
            
            with st.spinner("Creating team..."):
                result = db.create_team(team_name, user_id)
                
                if result['success']:
                    # Update session state
                    st.session_state.user['team_id'] = result['team_id']
                    
                    st.success(f"✅ Team '{team_name}' created successfully!")
                    st.balloons()
                    
                    # Show team code
                    st.info(f"**Your Team Code:** `{result['team_code']}`")
                    st.write("Share this code with your team members so they can join.")
                    
                    # Show next steps
                    with st.expander("🎯 Next Steps"):
                        st.write("1. **Share the team code** with your members")
                        st.write("2. **Invite members** using the 'Invite Members' tab")
                        st.write("3. **Set up team tasks** in the Task Manager")
                        st.write("4. **Start tracking mood** with your team")
                    
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Failed to create team: {result.get('error', 'Unknown error')}")

def show_join_team(user_id):
    """Page for joining an existing team"""
    st.subheader("Join Existing Team")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### Join with Team Code")
        
        team_code = st.text_input("Enter Team Code", 
                                 placeholder="TEAM-XXXX or team ID",
                                 help="Get the team code from your team admin")
        
        if st.button("Join Team", type="primary", use_container_width=True):
            if not team_code:
                st.error("Please enter a team code")
                return
            
            with st.spinner("Joining team..."):
                # Try to extract team ID
                try:
                    if team_code.startswith("TEAM-"):
                        # Extract from hash code
                        import hashlib
                        # This is a simplified approach - in production, you'd have a proper mapping
                        team_id = int(team_code.split('-')[1], 16) % 10000
                    else:
                        team_id = int(team_code)
                    
                    success, message = db.add_user_to_team(user_id, team_id)
                    
                    if success:
                        # Update session state
                        st.session_state.user['team_id'] = team_id
                        
                        st.success(f"✅ {message}")
                        
                        # Get team info
                        team_info = db.get_team_by_id(team_id)
                        if team_info:
                            st.info(f"You've joined **{team_info['name']}** "
                                   f"(Admin: {team_info['admin_name']})")
                        
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"Failed to join team: {message}")
                        
                except ValueError:
                    st.error("Invalid team code format. Please check and try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with col2:
        st.write("### Quick Tips")
        st.info("💡 **Where to find team code:**")
        st.write("1. Ask your team admin")
        st.write("2. Check team invitation email")
        st.write("3. Look in team chat/slack")
        
        st.info("👑 **Don't have a team?**")
        if st.button("Create New Team", use_container_width=True):
            st.switch_page("pages/6_Team_Management.py")

def show_team_overview(team_id, user_id):
    """Show team overview dashboard"""
    
    # Get team information
    team_info = db.get_team_by_id(team_id)
    team_stats = db_ops.get_team_stats(team_id)
    team_members = db_ops.get_team_members(team_id)
    
    if not team_info:
        st.error("Team not found")
        return
    
    # Team header
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        st.subheader(f"🏢 {team_info['name']}")
        st.caption(f"Created on {team_info['created_at']} • Admin: {team_info['admin_name']}")
    
    with col2:
        # Team code
        team_code = db.generate_team_code(team_id)
        st.code(team_code, language="")
        st.caption("Team Code")
    
    with col3:
        if st.button("📋 Copy Code", use_container_width=True):
            st.success("Code copied to clipboard!")
    
    st.markdown("---")
    
    # Team stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Members", team_stats['total_members'])
    
    with col2:
        st.metric("Active Today", team_stats['active_members'])
    
    with col3:
        st.metric("Avg Mood", f"{team_stats['avg_mood']:.1f}/10")
    
    with col4:
        st.metric("Task Completion", f"{team_stats['completion_rate']}%")
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("👥 Team Members")
        
        if team_members:
            for member in team_members:
                # Get today's mood for each member
                today_mood = db_ops.get_today_mood_stats(member['id'])
                
                with st.container():
                    cols = st.columns([3, 2, 2, 1])
                    
                    with cols[0]:
                        role_emoji = "👑" if member['role'] == 'admin' else "👤"
                        st.write(f"{role_emoji} **{member['username']}**")
                        st.caption(member['email'])
                    
                    with cols[1]:
                        if today_mood['avg_mood']:
                            mood_score = today_mood['avg_mood']
                            from utils.visualizations import viz
                            color = viz._get_mood_color(mood_score)
                            st.markdown(f'<span style="color:{color}; font-weight:bold;">{mood_score:.1f}/10</span>', 
                                      unsafe_allow_html=True)
                        else:
                            st.caption("No entry")
                    
                    with cols[2]:
                        if member['role'] == 'admin':
                            st.markdown('<span style="color:#FFD166; font-weight:bold;">Admin</span>', 
                                      unsafe_allow_html=True)
                        else:
                            st.caption(member['role'].title())
                    
                    with cols[3]:
                        if member['id'] == user_id:
                            st.caption("You")
                    
                    st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
        else:
            st.info("No team members found")
    
    with col2:
        st.subheader("🚀 Quick Actions")
        
        if st.button("📧 Invite Members", use_container_width=True):
            st.session_state.active_tab = "Invite Members"
            st.rerun()
        
        if st.button("📊 View Analytics", use_container_width=True):
            st.switch_page("pages/5_Analytics.py")
        
        if st.button("📋 Manage Tasks", use_container_width=True):
            st.switch_page("pages/3_Task_Manager.py")
        
        st.markdown("---")
        
        st.subheader("ℹ️ Team Info")
        st.write(f"**Members:** {team_stats['total_members']}")
        st.write(f"**Active Today:** {team_stats['active_members']}")
        st.write(f"**Avg Mood:** {team_stats['avg_mood']:.1f}/10")
        
        # Leave team option (not for admin)
        is_admin = any(member['id'] == user_id and member['role'] == 'admin' 
                      for member in team_members) if team_members else False
        
        if not is_admin:
            st.markdown("---")
            if st.button("🚪 Leave Team", type="secondary", use_container_width=True):
                if st.checkbox("I confirm I want to leave this team"):
                    if db.remove_user_from_team(user_id):
                        st.session_state.user['team_id'] = None
                        st.success("You have left the team")
                        time.sleep(2)
                        st.rerun()

def show_invite_members(team_id):
    """Page for inviting members to join team"""
    st.subheader("Invite Team Members")
    
    # Get team info
    team_info = db.get_team_by_id(team_id)
    team_code = db.generate_team_code(team_id)
    
    # Invitation methods
    method = st.radio("Invitation Method", 
                     ["Share Team Code", "Send Email Invites", "Generate Invite Link"],
                     horizontal=True)
    
    if method == "Share Team Code":
        st.info("Share this code with your team members. They can use it to join your team.")
        
        # Team code display
        col1, col2 = st.columns([3, 1])
        with col1:
            st.code(team_code, language="")
        with col2:
            if st.button("📋 Copy", use_container_width=True):
                st.success("Code copied!")
        
        st.markdown("---")
        st.subheader("How to join:")
        st.write("1. Share the team code above with your members")
        st.write("2. They go to **Team Management → Join Team**")
        st.write("3. They enter the team code")
        st.write("4. They're automatically added to the team!")
        
        # Quick share options
        st.markdown("---")
        st.subheader("Quick Share")
        
        share_cols = st.columns(4)
        with share_cols[0]:
            if st.button("📧 Email", use_container_width=True):
                st.info("Email template copied!")
        with share_cols[1]:
            if st.button("💬 Slack", use_container_width=True):
                st.info("Slack message copied!")
        with share_cols[2]:
            if st.button("📱 WhatsApp", use_container_width=True):
                st.info("WhatsApp message copied!")
        with share_cols[3]:
            if st.button("📄 Copy Message", use_container_width=True):
                message = f"""Join my team '{team_info['name']}' on Team Optimizer AI!

Team Code: {team_code}

Go to Team Management → Join Team and enter the code above."""
                st.info("Invitation message copied!")
    
    elif method == "Send Email Invites":
        st.info("Send direct email invitations to team members.")
        
        emails = st.text_area("Enter email addresses (one per line)", 
                             placeholder="member1@company.com\nmember2@company.com",
                             height=100)
        
        message = st.text_area("Invitation message",
                              value=f"""Hi!

You're invited to join my team '{team_info['name']}' on Team Optimizer AI.

Team Code: {team_code}

Use this code to join the team and start collaborating!

Best regards,
{st.session_state.user['username']}""",
                              height=150)
        
        if st.button("Send Invitations", type="primary"):
            if not emails:
                st.error("Please enter at least one email address")
            else:
                # Simulate sending emails
                email_list = [email.strip() for email in emails.split('\n') if email.strip()]
                st.success(f"Invitations sent to {len(email_list)} email addresses!")
                st.info("Note: Email functionality requires email server setup. This is a demo.")
    
    elif method == "Generate Invite Link":
        st.info("Generate a unique invite link that expires after a certain time.")
        
        col1, col2 = st.columns(2)
        with col1:
            expiry = st.selectbox("Link expires in", 
                                 ["24 hours", "7 days", "30 days", "Never"])
        with col2:
            max_uses = st.number_input("Maximum uses", min_value=1, max_value=100, value=10)
        
        # Generate a simple invite token
        import hashlib
        import time
        token = hashlib.md5(f"{team_id}{time.time()}".encode()).hexdigest()[:16]
        invite_link = f"https://yourapp.com/join/{token}"
        
        st.code(invite_link, language="")
        
        if st.button("Generate New Link", type="primary"):
            st.success("New invite link generated!")
            st.info(f"Expires: {expiry} • Max uses: {max_uses}")
            
            if st.button("📋 Copy Link", use_container_width=True):
                st.success("Link copied!")

def show_member_management(team_id, user_id):
    """Page for managing team members"""
    st.subheader("Member Management")
    
    # Check if user is admin
    team_members = db_ops.get_team_members(team_id)
    is_admin = any(member['id'] == user_id and member['role'] == 'admin' 
                  for member in team_members) if team_members else False
    
    if not is_admin:
        st.warning("Only team admins can manage members")
        return
    
    # Get current members
    members = db_ops.get_team_members(team_id)
    
    if members:
        st.write(f"**Total Members:** {len(members)}")
        
        # Member table with actions
        for member in members:
            with st.expander(f"{member['username']} ({member['email']})", expanded=False):
                col1, col2, col3 = st.columns([2, 2, 2])
                
                with col1:
                    # Role management
                    current_role = member['role']
                    if member['id'] == user_id:
                        st.write(f"**Role:** {current_role.title()} (You)")
                    else:
                        new_role = st.selectbox(
                            "Role",
                            ["member", "admin", "manager"],
                            index=["member", "admin", "manager"].index(current_role) 
                            if current_role in ["member", "admin", "manager"] else 0,
                            key=f"role_{member['id']}"
                        )
                        
                        if new_role != current_role:
                            if st.button("Update Role", key=f"update_{member['id']}"):
                                conn = db.get_connection()
                                cursor = conn.cursor()
                                cursor.execute('UPDATE users SET role = ? WHERE id = ?', 
                                             (new_role, member['id']))
                                conn.commit()
                                conn.close()
                                st.success(f"Updated {member['username']}'s role to {new_role}")
                                time.sleep(1)
                                st.rerun()
                
                with col2:
                    # Activity status
                    today_mood = db_ops.get_today_mood_stats(member['id'])
                    if today_mood['entries'] > 0:
                        st.success("Active today")
                    else:
                        st.warning("No activity today")
                
                with col3:
                    # Remove member (not self)
                    if member['id'] != user_id:
                        if st.button("Remove from Team", type="secondary", 
                                   key=f"remove_{member['id']}"):
                            if st.checkbox(f"Confirm remove {member['username']}?", 
                                         key=f"confirm_{member['id']}"):
                                success = db.remove_user_from_team(member['id'])
                                if success:
                                    st.success(f"Removed {member['username']} from team")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error("Failed to remove member")
    else:
        st.info("No team members to manage")

def show_team_settings(team_id, user_id):
    """Page for team settings"""
    st.subheader("Team Settings")
    
    # Check if user is admin
    team_members = db_ops.get_team_members(team_id)
    is_admin = any(member['id'] == user_id and member['role'] == 'admin' 
                  for member in team_members) if team_members else False
    
    if not is_admin:
        st.warning("Only team admins can modify team settings")
        
        # Show read-only settings
        team_info = db.get_team_by_id(team_id)
        if team_info:
            st.write(f"**Team Name:** {team_info['name']}")
            st.write(f"**Created:** {team_info['created_at']}")
            st.write(f"**Admin:** {team_info['admin_name']}")
        return
    
    # Get current team info
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM teams WHERE id = ?', (team_id,))
    team_data = cursor.fetchone()
    conn.close()
    
    if not team_data:
        st.error("Team not found")
        return
    
    current_name = team_data[0]
    
    # Team settings form
    with st.form("team_settings_form"):
        team_name = st.text_input("Team Name", value=current_name)
        
        col1, col2 = st.columns(2)
        with col1:
            privacy = st.selectbox("Team Privacy",
                                  ["Open - Anyone can join with code",
                                   "Closed - Admin approval required"],
                                  index=0)
        
        with col2:
            default_role = st.selectbox("Default New Member Role",
                                       ["Member", "Manager", "Viewer"],
                                       index=0)
        
        mood_sharing = st.radio("Mood Data Sharing",
                               ["Anonymous only", 
                                "Team members can see names",
                                "Managers only"],
                               index=1)
        
        task_permissions = st.multiselect("Task Permissions",
                                         ["All members can create tasks",
                                          "All members can assign tasks",
                                          "Only managers can delete tasks",
                                          "Task deadlines visible to all"],
                                         default=["All members can create tasks",
                                                 "Task deadlines visible to all"])
        
        submitted = st.form_submit_button("Save Settings", type="primary")
        
        if submitted:
            if not team_name:
                st.error("Team name is required")
                return
            
            # Update team name
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE teams SET name = ? WHERE id = ?', (team_name, team_id))
            conn.commit()
            conn.close()
            
            st.success("Team settings updated!")
            
            # Show backup team code
            team_code = db.generate_team_code(team_id)
            st.info(f"**Team Code:** `{team_code}` (unchanged)")
    
    # Danger zone
    st.markdown("---")
    st.subheader("⚠️ Danger Zone")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Reset Team Code", type="secondary", use_container_width=True):
            st.warning("This will generate a new team code. Old code will no longer work.")
            if st.checkbox("I understand and want to reset the team code"):
                # In production, you'd implement actual reset logic
                st.info("Team code reset feature will be available in next update")
    
    with col2:
        if st.button("🗑️ Delete Team", type="secondary", use_container_width=True):
            st.error("This will permanently delete the team and all associated data!")
            if st.checkbox("I understand this cannot be undone"):
                if st.text_input("Type 'DELETE' to confirm") == "DELETE":
                    st.error("Team deletion feature will be available in next update")

if __name__ == "__main__":
    main()