# Deployment Guide - Railway

This guide will walk you through deploying your GroupFolio bot to Railway for free 24/7 hosting.

## Why Railway?

- ✅ $5/month free credit (renews monthly)
- ✅ No credit card required
- ✅ Super easy deployment from GitHub
- ✅ Bot runs 24/7 (no sleeping like Render)
- ✅ Typically uses $3-4/month, so stays free

## Prerequisites

- A Railway account (sign up at https://railway.app)
- GitHub account
- Your code pushed to GitHub
- MongoDB Atlas connection string
- Discord bot token

---

## Step 1: Push Your Code to GitHub

If you haven't already:

```bash
cd /Users/dyang/Documents/GitHub/GroupFolio

# Initialize git (if not done)
git add .
git commit -m "Initial commit - GroupFolio Discord bot"

# Push to GitHub (create repo first on github.com)
git remote add origin https://github.com/YOUR_USERNAME/GroupFolio.git
git branch -M main
git push -u origin main
```

---

## Step 2: Sign Up for Railway

1. Go to https://railway.app
2. Click **"Login"** or **"Start a New Project"**
3. Sign in with your **GitHub account**
4. Authorize Railway to access your repositories

**No credit card needed!** You automatically get $5 free credit per month.

---

## Step 3: Create a New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your **GroupFolio** repository
4. Railway will detect your `Dockerfile` automatically

**Don't deploy yet!** We need to add environment variables first.

---

## Step 4: Add Environment Variables

In your Railway project dashboard:

1. Click on your service (should say "groupfolio" or similar)
2. Go to the **"Variables"** tab
3. Click **"+ New Variable"** and add these:

```
DISCORD_TOKEN=your_actual_discord_token_here
COMMAND_PREFIX=!
MONGODB_URI=mongodb+srv://username:password@cluster.xxxxx.mongodb.net/
```

**Important:**
- Replace with your actual Discord token
- Replace with your actual MongoDB connection string
- Don't use quotes around the values

---

## Step 5: Deploy!

1. Go back to the **"Deployments"** tab
2. Railway should automatically start deploying
3. Wait 1-2 minutes for the build to complete

---

## Step 6: Check if It's Running

1. Click on the **"Deployments"** tab
2. Click on the latest deployment
3. View the **logs** - you should see:

```
✓ Connected to MongoDB!
GroupFolio#1234 has connected to Discord!
Bot is in 1 server(s)
```

4. Test in your Discord server: `!ping`

---

## Managing Your Bot

### View Logs
- Go to your Railway project
- Click on your service
- Click **"Deployments"** → Latest deployment → **View logs**

### Restart the Bot
- Go to **"Deployments"**
- Click the **"⋮"** menu on the latest deployment
- Click **"Redeploy"**

### Update Environment Variables
- Go to **"Variables"** tab
- Edit or add variables
- Bot will automatically restart

### Check Usage/Billing
- Click your profile (top right)
- Go to **"Usage"**
- See how much of your $5 credit you've used

---

## Updating Your Bot (Making Code Changes)

When you make changes to your code:

```bash
# Make your changes in bot.py or other files

# Commit and push to GitHub
git add .
git commit -m "Add new feature"
git push

# Railway will automatically detect the push and redeploy!
```

That's it! Railway auto-deploys from GitHub.

---

## Troubleshooting

### Bot not responding in Discord
1. Check Railway logs for errors
2. Verify `MESSAGE CONTENT INTENT` is enabled in Discord Developer Portal
3. Make sure DISCORD_TOKEN variable is set correctly

### MongoDB connection failed
1. Check your MONGODB_URI is correct
2. Make sure MongoDB Atlas IP whitelist includes `0.0.0.0/0`
3. Verify you replaced `<password>` with your actual password

### "Out of credits" or bot stopped
1. Go to Railway dashboard → Usage
2. If you've used your $5 credit, you'll need to wait for next month
3. A small Discord bot should only use $3-4/month

### Build failed
1. Check Railway logs for error messages
2. Make sure all files are committed to GitHub
3. Verify `requirements.txt` and `Dockerfile` are present

---

## Railway vs Other Options

| Platform | Free Tier | Sleeping Issue | Credit Card | Ease of Use |
|----------|-----------|----------------|-------------|-------------|
| **Railway** | $5/month credit | ❌ No sleeping | ❌ Not required | ⭐⭐⭐⭐⭐ |
| Render | Free forever | ✅ Sleeps after 15min | ❌ Not required | ⭐⭐⭐⭐ |
| Fly.io | Generous free | ❌ No sleeping | ✅ Required | ⭐⭐⭐ |
| Heroku | Removed free tier | N/A | ✅ Required | ⭐⭐⭐⭐ |

---

## Cost Monitoring Tips

- Check usage weekly: Railway dashboard → Usage
- A Discord bot typically uses $3-4/month
- You get $5 free credit each month (renews)
- Set up usage alerts in Railway settings

---

## Next Steps

Now that your bot is deployed:
1. ✅ Bot runs 24/7
2. ✅ Auto-deploys when you push to GitHub
3. ✅ MongoDB connected
4. Ready to add portfolio features!

---

## Need Help?

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Check bot logs in Railway dashboard
- GitHub Issues: Create an issue in your repo

Enjoy your deployed bot! 🚀
