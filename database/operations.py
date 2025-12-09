from datetime import datetime, timedelta
import pandas as pd
from .models import db

class DatabaseOperations:
    def __init__(self):
        self.db = db
    
    # ========== MOOD OPERATIONS ==========
    def add_team_member(self, team_id, email, role='member'):
        """Add a member to team by email"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Find user by email
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if not user:
                return False, "User not found"
            
            user_id = user[0]
            
            # Check if already in a team
            cursor.execute('SELECT team_id FROM users WHERE id = ?', (user_id,))
            existing_team = cursor.fetchone()
            
            if existing_team and existing_team[0]:
                return False, "User is already in a team"
            
            # Add to team
            cursor.execute('UPDATE users SET team_id = ?, role = ? WHERE id = ?', 
                        (team_id, role, user_id))
            
            conn.commit()
            return True, f"Successfully added user to team"
            
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_team_invite_info(self, team_id):
        """Get team info for invitations"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT t.name, u.username as admin_name, u.email as admin_email,
            COUNT(DISTINCT u2.id) as member_count
        FROM teams t
        LEFT JOIN users u ON t.created_by = u.id
        LEFT JOIN users u2 ON u2.team_id = t.id
        WHERE t.id = ?
        GROUP BY t.id, t.name, u.username, u.email
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (team_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'name': result[0],
                'admin_name': result[1],
                'admin_email': result[2],
                'member_count': result[3]
            }
        return None
    
    def create_mood_entry(self, user_id, text_entry=None, text_sentiment=None, 
                         visual_sentiment=None, stress_level=5):
        """Create a new mood entry"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Calculate combined score if both available
        if text_sentiment and visual_sentiment:
            combined_score = (text_sentiment + visual_sentiment) / 2
        elif text_sentiment:
            combined_score = text_sentiment
        elif visual_sentiment:
            combined_score = visual_sentiment
        else:
            combined_score = 5.0
        
        cursor.execute('''
        INSERT INTO mood_entries 
        (user_id, text_entry, text_sentiment, visual_sentiment, combined_score, stress_level)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, text_entry, text_sentiment, visual_sentiment, combined_score, stress_level))
        
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        
        return entry_id
    
    def get_user_mood_history(self, user_id, days=30):
        """Get mood history for a user"""
        conn = self.db.get_connection()
        
        query = f'''
        SELECT date(created_at) as date, 
               AVG(combined_score) as avg_mood,
               AVG(stress_level) as avg_stress,
               COUNT(*) as entries
        FROM mood_entries 
        WHERE user_id = ? 
          AND created_at >= date('now', '-{days} days')
        GROUP BY date(created_at)
        ORDER BY date DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=(user_id,))
        conn.close()
        
        return df
    
    def get_team_mood_summary(self, team_id):
        """Get team mood summary for dashboard"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT 
            u.username,
            AVG(me.combined_score) as avg_mood,
            AVG(me.stress_level) as avg_stress,
            COUNT(me.id) as total_entries,
            MAX(me.created_at) as last_entry
        FROM users u
        LEFT JOIN mood_entries me ON u.id = me.user_id
        WHERE u.team_id = ? 
          AND me.created_at >= date('now', '-7 days')
        GROUP BY u.id, u.username
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (team_id,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'username': r[0],
                'avg_mood': round(r[1], 1) if r[1] else 0,
                'avg_stress': round(r[2], 1) if r[2] else 0,
                'total_entries': r[3] if r[3] else 0,
                'last_entry': r[4]
            }
            for r in results
        ]
    
    def get_today_mood_stats(self, user_id):
        """Get today's mood stats for a user"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT 
            AVG(combined_score) as avg_mood_today,
            AVG(stress_level) as avg_stress_today,
            COUNT(*) as entries_today
        FROM mood_entries 
        WHERE user_id = ? 
          AND date(created_at) = date('now')
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            return {
                'avg_mood': round(result[0], 1),
                'avg_stress': round(result[1], 1) if result[1] else 0,
                'entries': result[2] if result[2] else 0
            }
        else:
            return {
                'avg_mood': None,
                'avg_stress': None,
                'entries': 0
            }
    
    # ========== TASK OPERATIONS ==========
    def create_task(self, title, description, assigned_to=None, 
                   priority='medium', deadline=None):
        """Create a new task"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO tasks (title, description, assigned_to, priority, deadline)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, description, assigned_to, priority, deadline))
        
        conn.commit()
        task_id = cursor.lastrowid
        conn.close()
        
        return task_id
    
    def get_user_tasks(self, user_id, status_filter=None):
        """Get tasks for a user"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT t.*, u.username as assigned_name
        FROM tasks t
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE t.assigned_to = ?
        '''
        
        if status_filter:
            query += f" AND t.status = '{status_filter}'"
        
        query += " ORDER BY t.priority DESC, t.deadline ASC"
        
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        
        columns = [desc[0] for desc in cursor.description]
        tasks = []
        rows = cursor.fetchall()
        
        for row in rows:
            task_dict = {}
            for i, col in enumerate(columns):
                task_dict[col] = row[i]
            tasks.append(task_dict)
        
        conn.close()
        return tasks
    
    def get_team_tasks(self, team_id):
        """Get all tasks for a team"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT t.*, u.username as assigned_name
        FROM tasks t
        JOIN users u ON t.assigned_to = u.id
        WHERE u.team_id = ?
        ORDER BY 
            CASE t.priority 
                WHEN 'urgent' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            t.deadline ASC
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (team_id,))
        
        columns = [desc[0] for desc in cursor.description]
        tasks = []
        rows = cursor.fetchall()
        
        for row in rows:
            task_dict = {}
            for i, col in enumerate(columns):
                task_dict[col] = row[i]
            tasks.append(task_dict)
        
        conn.close()
        return tasks
    
    def update_task_status(self, task_id, new_status):
        """Update task status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE tasks SET status = ? WHERE id = ?', (new_status, task_id))
        conn.commit()
        conn.close()
        
        return True
    
    def delete_task(self, task_id):
        """Delete a task"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
        
        return True
    
    def get_task_stats(self, user_id):
        """Get task statistics for dashboard"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            SUM(CASE WHEN status = 'todo' THEN 1 ELSE 0 END) as todo,
            SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent
        FROM tasks 
        WHERE assigned_to = ?
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] == 0:
            return {
                'total': 0,
                'completed': 0,
                'in_progress': 0,
                'todo': 0,
                'urgent': 0,
                'completion_rate': 0
            }
        
        total = result[0] if result[0] else 0
        completed = result[1] if result[1] else 0
        
        return {
            'total': total,
            'completed': completed,
            'in_progress': result[2] if result[2] else 0,
            'todo': result[3] if result[3] else 0,
            'urgent': result[4] if result[4] else 0,
            'completion_rate': round((completed / total) * 100, 1) if total > 0 else 0
        }
    
    # ========== TEAM OPERATIONS ==========
    def get_team_members(self, team_id):
        """Get all members of a team"""
        conn = self.db.get_connection()
        
        query = '''
        SELECT id, username, email, role, created_at
        FROM users
        WHERE team_id = ?
        ORDER BY role DESC, username
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (team_id,))
        
        columns = [desc[0] for desc in cursor.description]
        members = []
        rows = cursor.fetchall()
        
        for row in rows:
            member_dict = {}
            for i, col in enumerate(columns):
                member_dict[col] = row[i]
            members.append(member_dict)
        
        conn.close()
        return members
    
    def get_team_stats(self, team_id):
        """Get team statistics"""
        conn = self.db.get_connection()
        
        # Team mood stats
        mood_query = '''
        SELECT 
            AVG(me.combined_score) as avg_team_mood,
            AVG(me.stress_level) as avg_team_stress,
            COUNT(DISTINCT me.user_id) as active_members
        FROM mood_entries me
        JOIN users u ON me.user_id = u.id
        WHERE u.team_id = ?
          AND me.created_at >= date('now', '-7 days')
        '''
        
        # Task stats
        task_query = '''
        SELECT 
            COUNT(*) as total_tasks,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
            COUNT(DISTINCT assigned_to) as members_with_tasks
        FROM tasks t
        JOIN users u ON t.assigned_to = u.id
        WHERE u.team_id = ?
        '''
        
        cursor = conn.cursor()
        
        # Get mood stats
        cursor.execute(mood_query, (team_id,))
        mood_stats = cursor.fetchone()
        
        # Get task stats
        cursor.execute(task_query, (team_id,))
        task_stats = cursor.fetchone()
        
        # Get member count
        cursor.execute('SELECT COUNT(*) FROM users WHERE team_id = ?', (team_id,))
        member_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'avg_mood': round(mood_stats[0], 1) if mood_stats and mood_stats[0] else 0,
            'avg_stress': round(mood_stats[1], 1) if mood_stats and mood_stats[1] else 0,
            'active_members': mood_stats[2] if mood_stats and mood_stats[2] else 0,
            'total_tasks': task_stats[0] if task_stats and task_stats[0] else 0,
            'completed_tasks': task_stats[1] if task_stats and task_stats[1] else 0,
            'members_with_tasks': task_stats[2] if task_stats and task_stats[2] else 0,
            'total_members': member_count if member_count else 0,
            'completion_rate': round((task_stats[1] / task_stats[0] * 100), 1) if task_stats and task_stats[0] and task_stats[0] > 0 else 0
        }

# Create singleton instance
db_ops = DatabaseOperations()


    
    
    