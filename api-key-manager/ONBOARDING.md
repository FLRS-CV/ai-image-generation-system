# 👥 Team Member Onboarding

## For Project Leads: Sharing Access

### Step 1: Share Repository Access
1. Add team member to GitHub repository
2. Ensure they have clone/pull permissions

### Step 2: Share Super Admin Key Securely
**Super Admin Key**: `sk-proj-superadmin-iRskCpsLWvWjAWAfqVYEZXkACrJmtYr-`

**Secure Sharing Methods**:
- ✅ Encrypted messaging (Signal, WhatsApp)
- ✅ Password manager (shared vault)
- ✅ Secure email
- ✅ Video call/in-person
- ❌ Never via plain text email or public channels

### Step 3: Provide Setup Instructions
Send them this message:

---

**Welcome to the AI Image Generation System! 🎉**

To get started:
1. Clone the repo: `https://github.com/FLRS-CV/ai-image-generation-system.git`
2. Follow the setup guide: `api-key-manager/SETUP.md`
3. Use this super admin key: `sk-proj-superadmin-iRskCpsLWvWjAWAfqVYEZXkACrJmtYr-`
4. Create your personal admin account after setup
5. Test virtual staging functionality

Let me know if you need help! 🚀

---

## For New Team Members: First Steps

### ✅ Setup Checklist
- [ ] Clone repository successfully
- [ ] Python environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created from template
- [ ] Super admin key added to `.env`
- [ ] Server starts without errors (`python run_server.py`)
- [ ] Can access `http://localhost:8004`
- [ ] Super admin login works
- [ ] Personal admin account created
- [ ] Virtual staging tested

### 🎯 Your Role Access
After setup, you'll have access to:

**As Super Admin** (initial setup only):
- ✅ Create admin and user accounts
- ✅ Manage all API keys
- ✅ Virtual staging features
- ✅ View usage statistics

**As Personal Admin** (recommended for daily use):
- ✅ Create user accounts
- ✅ Virtual staging features
- ❌ Cannot manage other admin keys (security)

### 🆘 Need Help?
1. Check the troubleshooting section in `SETUP.md`
2. Verify your `.env` file matches the example
3. Ensure ComfyUI is running (for virtual staging)
4. Contact your team lead

### 🔐 Security Reminder
- Keep the super admin key secure
- Use your personal admin account for daily work
- Never commit `.env` files to git
- Report any access issues immediately

---

**Ready to build amazing AI-powered virtual staging! 🏠✨**
