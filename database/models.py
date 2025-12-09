import sqlite3
from datetime import datetime
import hashlib
import bcrypt

class Database:
    def __init__(self, db_name='team_optimizer.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            team_id INTEGER,
            role TEXT DEFAULT 'member',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            allow_visual_tracking BOOLEAN DEFAULT 1
        )
        ''')
        
        # Teams table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        
        # Mood entries table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            text_entry TEXT,
            text_sentiment REAL,
            visual_sentiment REAL,
            combined_score REAL,
            stress_level INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        
        # Tasks table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            assigned_to INTEGER,
            status TEXT DEFAULT 'todo',
            priority TEXT DEFAULT 'medium',
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assigned_to) REFERENCES users (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_team_by_code(self, team_code):
        """Get team by team code - COMPATIBLE VERSION"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check what columns actually exist
        cursor.execute("PRAGMA table_info(teams)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Build query based on available columns
        select_columns = []
        
        # Always available columns
        select_columns.append("t.id")
        select_columns.append("t.name")
        select_columns.append("t.created_by")
        select_columns.append("t.created_at")
        select_columns.append("t.team_code")
        select_columns.append("t.is_active")
        
        # Optional columns (check if they exist)
        if 'description' in columns:
            select_columns.append("t.description")
        
        if 'settings' in columns:
            select_columns.append("t.settings")
        
        # Add admin info
        select_columns.append("u.username as admin_name")
        select_columns.append("u.email as admin_email")
        
        query = f'''
        SELECT {', '.join(select_columns)}
        FROM teams t
        LEFT JOIN users u ON t.created_by = u.id
        WHERE t.team_code = ? AND t.is_active = 1
        '''
        
        cursor.execute(query, (team_code,))
        
        team = cursor.fetchone()
        conn.close()
        
        if team:
            # Map results to dictionary
            result = {
                'id': team[0],
                'name': team[1],
                'created_by': team[2],
                'created_at': team[3],
                'team_code': team[4],
                'is_active': bool(team[5]),
            }
            
            # Handle optional columns
            idx = 6
            if 'description' in columns:
                result['description'] = team[idx]
                idx += 1
            
            if 'settings' in columns:
                result['settings'] = json.loads(team[idx]) if team[idx] else {}
                idx += 1
            
            # Admin info
            result['admin_name'] = team[idx]
            result['admin_email'] = team[idx + 1]
            
            return result
        return None

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    # User management methods
    def create_user(self, username, email, password, team_id=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, team_id)
        VALUES (?, ?, ?, ?)
        ''', (username, email, password_hash, team_id))
        
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        return user_id
    
    def authenticate_user(self, email, password):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, password_hash, team_id, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and self.verify_password(password, user[3]):
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'team_id': user[4],
                'role': user[5]
            }
        return None
    def create_team(self, team_name, created_by):
        """Create a new team and return team info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO teams (name, created_by) VALUES (?, ?)', 
                        (team_name, created_by))
            team_id = cursor.lastrowid
            
            # Update user's team_id
            cursor.execute('UPDATE users SET team_id = ? WHERE id = ?', (team_id, created_by))
            
            conn.commit()
            
            # Generate team code
            team_code = self.generate_team_code(team_id)
            
            return {
                'success': True,
                'team_id': team_id,
                'team_name': team_name,
                'team_code': team_code
            }
            
        except Exception as e:
            conn.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            conn.close()
    def add_user_to_team(self, user_id, team_code):
        """Add an existing user to a team using team code"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get team by code (we'll use team ID as code for now)
            cursor.execute('SELECT id FROM teams WHERE id = ?', (team_code,))
            team = cursor.fetchone()
            
            if not team:
                return False, "Team not found"
            
            team_id = team[0]
            
            # Update user's team
            cursor.execute('UPDATE users SET team_id = ? WHERE id = ?', (team_id, user_id))
            
            # Check if user was already in a team
            cursor.execute('SELECT team_id FROM users WHERE id = ?', (user_id,))
            old_team = cursor.fetchone()
            
            conn.commit()
            
            return True, f"Successfully joined team {team_id}"
            
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    def get_team_by_id(self, team_id):
        """Get team information by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.*, u.username as admin_name 
            FROM teams t
            LEFT JOIN users u ON t.created_by = u.id
            WHERE t.id = ?
        ''', (team_id,))
        
        team = cursor.fetchone()
        conn.close()
        
        if team:
            return {
                'id': team[0],
                'name': team[1],
                'created_by': team[2],
                'created_at': team[3],
                'admin_name': team[4]
            }
        return None

    def generate_team_code(self, team_id):
        """Generate a shareable team code"""
        import hashlib
        # Simple hash-based code
        code = hashlib.md5(f"team{team_id}".encode()).hexdigest()[:8].upper()
        return f"TEAM-{code}"

    def remove_user_from_team(self, user_id):
        """Remove user from their team"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE users SET team_id = NULL WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            return False
        finally:
            conn.close()

    def get_user_team_info(self, user_id):
        """Get user's team information"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT t.id, t.name, t.created_at, u.username as admin_name
            FROM teams t
            JOIN users u ON t.created_by = u.id
            WHERE t.id = (SELECT team_id FROM users WHERE id = ?)
        ''', (user_id,))
        
        team = cursor.fetchone()
        conn.close()
        
        if team:
            return {
                'id': team[0],
                'name': team[1],
                'created_at': team[2],
                'admin_name': team[3]
            }
        return None
    
    def get_user_by_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, email, team_id, role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'team_id': user[3],
                'role': user[4]
            }
        return None
    
    def create_team(self, team_name, created_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO teams (name, created_by) VALUES (?, ?)', (team_name, created_by))
        team_id = cursor.lastrowid
        
        # Update user's team_id
        cursor.execute('UPDATE users SET team_id = ? WHERE id = ?', (team_id, created_by))
        
        conn.commit()
        conn.close()
        
        return team_id
    

# Singleton instance
db = Database()

# Initialize database on import
db.init_db()