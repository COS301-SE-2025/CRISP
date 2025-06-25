# Claude Code Prompt: Remote Raspberry Pi Database Setup

Copy and paste this prompt to Claude Code to automatically set up remote Raspberry Pi database connection for any Django project.

---

**CLAUDE CODE PROMPT:**

```
Hi Claude! I need help setting up my Django project to connect to a remote PostgreSQL database on a Raspberry Pi. Here are my requirements:

**My Setup:**
- Local Django development on my machine
- Remote PostgreSQL database on Raspberry Pi
- Pi SSH access: ssh datadefenders@100.117.251.119
- Pi has Tailscale IP: 100.117.251.119
- Pi has WiFi IP: 192.168.68.112 (check with ifconfig on Pi)
- Database name: crisp_db
- Database user: crisp_user
- Database password: AdminPassword

**What I need you to do:**

1. **Analyze my Django project structure** and identify the settings file
2. **Create environment configuration files** for both direct connection and SSH tunnel options
3. **Create helper scripts** for managing SSH tunnels and connections
4. **Set up proper database configuration** that uses environment variables
5. **Create setup instructions** that work for my team
6. **Fix any line ending issues** for cross-platform compatibility
7. **Test the connection** and run migrations if possible

**Additional Requirements:**
- Support both direct connection (via Tailscale/WiFi) and SSH tunnel methods
- Include Redis configuration if my project uses Celery
- Make it easy for teammates to switch between local and remote databases
- Include troubleshooting steps
- Ensure all sensitive data uses environment variables
- Create scripts that work on both Windows WSL and Linux

**Pi Database Setup Commands** (I'll run these manually on the Pi):
```bash
# Configure PostgreSQL for external connections
sudo nano /etc/postgresql/*/main/postgresql.conf
# Change: listen_addresses = '*'

sudo nano /etc/postgresql/*/main/pg_hba.conf  
# Add: host all all 100.0.0.0/8 md5

sudo systemctl restart postgresql

# Set up database permissions
sudo -u postgres psql crisp_db -c "GRANT ALL PRIVILEGES ON SCHEMA public TO crisp_user;"
sudo -u postgres psql crisp_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO crisp_user;"
sudo -u postgres psql crisp_db -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO crisp_user;"
sudo -u postgres psql crisp_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO crisp_user;"
sudo -u postgres psql crisp_db -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO crisp_user;"
sudo -u postgres psql -c "ALTER USER crisp_user WITH SUPERUSER;"
```

Please examine my codebase, create all necessary configuration files, scripts, and documentation to make this work perfectly. Focus on making it robust and easy for my team to use.
```

---

## How to Use This Prompt

1. **Open Claude Code** in your Django project directory
2. **Copy and paste** the entire prompt above
3. **Claude will automatically:**
   - Analyze your project structure
   - Create environment configuration files
   - Set up helper scripts for SSH tunnels
   - Create comprehensive setup documentation
   - Fix any compatibility issues
   - Test connections and run migrations

4. **Customize the prompt** by updating:
   - SSH connection details (user@host)
   - IP addresses (Tailscale/WiFi)
   - Database credentials (name, user, password)
   - Additional requirements specific to your project

## What Claude Will Create

- `.env.pi` - Direct connection configuration
- `.env.tunnel` - SSH tunnel configuration  
- `scripts/connect_to_pi.sh` - Start SSH tunnels
- `scripts/check_tunnels.sh` - Check tunnel status
- `scripts/stop_tunnels.sh` - Stop tunnels
- `SETUP_PI_CONNECTION.md` - Complete setup guide
- Updated Django settings if needed
- Cross-platform compatibility fixes

## Team Usage

Each team member should:
1. Clone your repository
2. Use this Claude Code prompt in their local copy
3. Follow the generated setup instructions
4. Run the same Pi setup commands on your shared Pi

This approach ensures everyone has the same configuration and can easily switch between local development and remote Pi database operations.