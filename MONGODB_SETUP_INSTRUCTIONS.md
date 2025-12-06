# MongoDB Setup Instructions

## Prerequisites

- Docker and Docker Compose installed
- Existing Python Money Tracker application
- `.env` file configured

## Installation Steps

### 1. Update Environment Variables

Add to your `.env` file in `backend-api/` directory:

```env
MONGODB_URL=mongodb://mongouser:Admin@1234@mongodb:27017/receipts?authSource=admin
```

For local development (if running outside Docker):
```env
MONGODB_URL=mongodb://mongouser:Admin@1234@localhost:27017/receipts?authSource=admin
```

### 2. Start Docker Services

From the `portfolio-ai-app/` directory:

```bash
# Stop existing services
docker-compose down

# Rebuild backend with new dependencies
docker-compose build backend

# Start all services including MongoDB
docker-compose up -d

# Verify all services are running
docker-compose ps
```

Expected output:
```
NAME                            STATUS
pythonmoneytracker-backend      Up
pythonmoneytracker-db           Up (healthy)
pythonmoneytracker-mongodb      Up (healthy)
```

### 3. Verify MongoDB Connection

Check the health endpoint:

```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "mongodb": "connected",
    "gemini_api": "configured"
  }
}
```

### 4. Test MongoDB Functionality

#### Test 1: Upload a Receipt

```bash
curl -X POST http://localhost:5000/api/receipts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@test_receipt.jpg"
```

#### Test 2: Check Statistics

```bash
curl http://localhost:5000/api/receipts/mongo/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Test 3: Connect to MongoDB Shell

```bash
docker exec -it pythonmoneytracker-mongodb mongosh \
  -u mongouser \
  -p Admin@1234 \
  --authenticationDatabase admin
```

In the MongoDB shell:
```javascript
// Switch to receipts database
use receipts

// Count receipts
db.receipts.countDocuments()

// View a sample receipt
db.receipts.findOne()
```

## Local Development (Non-Docker)

If you're running the backend locally:

### 1. Install MongoDB Locally

**Windows:**
```powershell
# Download MongoDB from mongodb.com or use chocolatey
choco install mongodb

# Start MongoDB
mongod --dbpath C:\data\db
```

**Mac:**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongod
```

### 2. Install Python Dependencies

```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Mac/Linux

# Install dependencies
pip install pymongo
```

### 3. Update .env for Local MongoDB

```env
MONGODB_URL=mongodb://localhost:27017/receipts
```

### 4. Run the Application

```bash
python run.py
```

## Troubleshooting

### Issue: MongoDB Container Won't Start

**Solution 1**: Check logs
```bash
docker-compose logs mongodb
```

**Solution 2**: Remove and recreate volumes
```bash
docker-compose down -v
docker-compose up -d
```

### Issue: Backend Can't Connect to MongoDB

**Solution 1**: Verify MongoDB is running
```bash
docker-compose ps mongodb
```

**Solution 2**: Check connection string
```bash
# Inside backend container
docker exec -it pythonmoneytracker-backend env | grep MONGODB
```

**Solution 3**: Test connection manually
```bash
docker exec -it pythonmoneytracker-mongodb mongosh \
  --eval "db.adminCommand('ping')" \
  -u mongouser \
  -p Admin@1234 \
  --authenticationDatabase admin
```

### Issue: Import Errors for pymongo

**Solution**: Rebuild backend container
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Issue: Permission Denied

**Solution**: Check MongoDB credentials in docker-compose.yml match .env

### Issue: Data Not Appearing in MongoDB

**Solution 1**: Check backend logs
```bash
docker-compose logs backend | grep -i mongo
```

**Solution 2**: Verify receipt upload succeeded
```bash
# Check if receipt exists in PostgreSQL
docker exec -it pythonmoneytracker-db psql -U postgres -d pythonmoneytracker -c "SELECT COUNT(*) FROM receipts;"

# Check if receipt exists in MongoDB
docker exec -it pythonmoneytracker-mongodb mongosh -u mongouser -p Admin@1234 --authenticationDatabase admin --eval "use receipts; db.receipts.countDocuments()"
```

## Verification Checklist

- [ ] MongoDB container is running
- [ ] Backend container can connect to MongoDB
- [ ] Health endpoint shows MongoDB as "connected"
- [ ] Can upload a receipt successfully
- [ ] Receipt appears in MongoDB (check with mongosh)
- [ ] Can query receipts via API
- [ ] Can archive/unarchive receipts
- [ ] Statistics endpoint returns data

## Next Steps

Once setup is complete:

1. ✅ **Review Documentation**
   - Read `MONGODB_STORAGE_GUIDE.md` for detailed information
   - Check `MONGODB_QUICK_REFERENCE.md` for common commands

2. ✅ **Configure Backups**
   - Set up automated MongoDB backups
   - Test restore procedure

3. ✅ **Set Archive Policy**
   - Decide archive threshold (e.g., 90 days)
   - Schedule bulk archive jobs

4. ✅ **Monitor Usage**
   - Check storage statistics regularly
   - Monitor MongoDB performance

5. ✅ **Update Frontend** (Optional)
   - Add UI for archiving receipts
   - Show archived receipts in separate view
   - Display storage statistics

## Uninstallation

If you need to remove MongoDB:

```bash
# Stop services
docker-compose down

# Remove MongoDB volume (WARNING: This deletes all data)
docker volume rm portfolio-ai-app_mongodb_data

# Edit docker-compose.yml to remove mongodb service

# Restart
docker-compose up -d
```

## Security Notes

### Default Credentials

The default MongoDB credentials are:
- Username: `mongouser`
- Password: `Admin@1234`

**⚠️ IMPORTANT**: Change these for production!

### Changing MongoDB Password

1. Update `docker-compose.yml`:
```yaml
MONGO_INITDB_ROOT_PASSWORD: YourNewPassword
```

2. Update `.env`:
```env
MONGODB_URL=mongodb://mongouser:YourNewPassword@mongodb:27017/receipts?authSource=admin
```

3. Recreate MongoDB container:
```bash
docker-compose down mongodb
docker volume rm portfolio-ai-app_mongodb_data
docker-compose up -d mongodb
```

### Production Recommendations

1. ✅ Use strong, unique passwords
2. ✅ Enable MongoDB authentication (already enabled)
3. ✅ Keep MongoDB within Docker network (already configured)
4. ✅ Regular backups
5. ✅ Monitor access logs
6. ✅ Use environment variables for credentials
7. ✅ Enable SSL/TLS in production

## Support

For issues or questions:
1. Check this setup guide
2. Review `MONGODB_STORAGE_GUIDE.md`
3. Check Docker and application logs
4. Verify environment variables are set correctly

## Summary

MongoDB is now integrated for receipt storage with:
- ✅ Automatic saving of all uploaded receipts
- ✅ Flexible archiving system
- ✅ Advanced search capabilities
- ✅ Storage statistics
- ✅ Full API for receipt management

The system continues to work if MongoDB is unavailable, with graceful degradation to PostgreSQL-only mode.
