# Deployment Guide for HRMS Lite

This guide will help you deploy the HRMS Lite application to production.

## Prerequisites

- GitHub account
- Render account (for backend)
- Vercel account (for frontend)

## Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Push your code to the repository:

```bash
git init
git add .
git commit -m "Initial commit - HRMS Lite Application"
git branch -M main
git remote add origin https://github.com/yourusername/hrms-lite.git
git push -u origin main
```

## Step 2: Deploy Backend to Render

1. Go to [render.com](https://render.com) and sign up
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: hrms-lite-backend
   - **Environment**: Python 3
   - **Root Directory**: backend
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"
6. Wait for deployment to complete
7. Copy the deployed URL (e.g., `https://hrms-lite-backend.onrender.com`)

## Step 3: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and sign up
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Create React App
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: build
5. Add Environment Variable:
   - **Name**: `REACT_APP_API_URL`
   - **Value**: Your backend URL from Step 2
6. Click "Deploy"
7. Wait for deployment to complete

## Step 4: Update CORS Settings

1. Go to your Render dashboard
2. Navigate to your backend service
3. Add environment variable:
   - **Name**: `ALLOWED_ORIGINS`
   - **Value**: Your frontend URL from Step 3
4. Redeploy the service

## Step 5: Test the Application

1. Visit your frontend URL
2. Test all features:
   - Add employees
   - View employee list
   - Delete employees
   - Mark attendance
   - View attendance records

## Environment Variables

### Backend (.env)
```
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app
```

### Frontend (.env.production)
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Make sure the frontend URL is added to allowed origins
2. **Database Issues**: Render uses ephemeral storage on free tier - data may reset
3. **Build Failures**: Check that all dependencies are in requirements.txt
4. **API Connection**: Verify the API URL is correct in frontend environment

### Logs and Monitoring

- **Render**: Check the Logs tab in your service dashboard
- **Vercel**: Check the Functions tab in your project dashboard

## Production Considerations

### Security
- Add authentication in production
- Use HTTPS everywhere
- Validate all inputs
- Implement rate limiting

### Performance
- Use a production database (PostgreSQL)
- Implement caching
- Optimize bundle size
- Add CDN

### Monitoring
- Add error tracking (Sentry)
- Implement health checks
- Monitor API usage
- Set up alerts

## Scaling

### Backend Scaling
- Upgrade to paid Render plan
- Use load balancer
- Implement caching
- Database optimization

### Frontend Scaling
- Use CDN for static assets
- Implement lazy loading
- Optimize images
- Service workers

## Backup Strategy

### Database Backup
```python
# Add to main.py for backup endpoint
@app.get("/backup")
async def backup_database():
    # Implement backup logic
    pass
```

### Regular Backups
- Schedule automated backups
- Store backups securely
- Test restore procedures

## Maintenance

### Regular Tasks
- Update dependencies
- Monitor security vulnerabilities
- Check logs regularly
- Performance monitoring

### Updates
- Test updates in staging
- Use feature flags
- Rollback procedures
- Communication plan
