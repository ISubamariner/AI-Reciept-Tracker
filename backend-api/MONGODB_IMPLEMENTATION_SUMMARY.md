# MongoDB Receipt Storage - Implementation Summary

## What Was Added

This update adds MongoDB as a secondary storage system for receipt documents, enabling efficient archiving and flexible data management alongside the existing PostgreSQL database.

## Key Features

### ✅ Hybrid Database Architecture
- **PostgreSQL**: User data, transactions, and structured financial records
- **MongoDB**: Receipt documents, images, AI extraction data, and archived receipts

### ✅ Automatic Receipt Storage
- All uploaded receipts are automatically saved to both databases
- No manual intervention required
- Seamless integration with existing upload workflow

### ✅ Flexible Archiving System
- Mark receipts as archived without deleting
- Easy restoration of archived receipts
- Bulk archiving for old data
- Custom archive reasons for tracking

### ✅ Advanced Search & Filtering
- Search by vendor name, receipt number, or tags
- Filter by status (pending, processed, error)
- Query archived vs. active receipts
- Pagination support for large datasets

### ✅ Storage Statistics
- Track total receipts, archived count, file sizes
- Monitor storage usage per user or system-wide
- Performance metrics for optimization

## New Files Created

1. **`app/mongo_connector.py`** - MongoDB connection and document management
2. **`app/services/receipt_mongo_service.py`** - Business logic for receipt operations
3. **`MONGODB_STORAGE_GUIDE.md`** - Comprehensive documentation
4. **`MONGODB_QUICK_REFERENCE.md`** - Quick command reference

## Modified Files

1. **`docker-compose.yml`** - Added MongoDB service
2. **`requirements.txt`** - Added pymongo dependency
3. **`app/__init__.py`** - Initialize MongoDB on app startup
4. **`app/receipts/routes.py`** - Added MongoDB routes and integration
5. **`config.py`** - Added MongoDB configuration

## API Endpoints Added

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/receipts/mongo/<receipt_id>` | GET | Get receipt from MongoDB |
| `/api/receipts/mongo/user/<user_id>` | GET | Get user's receipts |
| `/api/receipts/mongo/archive/<receipt_id>` | POST | Archive receipt |
| `/api/receipts/mongo/unarchive/<receipt_id>` | POST | Unarchive receipt |
| `/api/receipts/mongo/archived` | GET | List archived receipts |
| `/api/receipts/mongo/stats` | GET | Get storage statistics |
| `/api/receipts/mongo/search` | GET | Search receipts |
| `/api/receipts/mongo/bulk-archive` | POST | Bulk archive old receipts (admin) |

## Getting Started

### 1. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (existing)
- MongoDB (new)
- Backend API

### 2. Verify Setup

Check that MongoDB is running:

```bash
curl http://localhost:5000/api/health
```

You should see:
```json
{
  "services": {
    "database": "connected",
    "mongodb": "connected",
    "gemini_api": "configured"
  }
}
```

### 3. Use Existing Upload Flow

No changes required! Continue uploading receipts as before:

```bash
curl -X POST http://localhost:5000/api/receipts/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "image=@receipt.jpg"
```

Receipts are now automatically saved to both PostgreSQL and MongoDB.

## Common Use Cases

### Archive Old Receipts

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/archive/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "old_data"}'
```

### View Statistics

```bash
curl http://localhost:5000/api/receipts/mongo/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Search Receipts

```bash
curl "http://localhost:5000/api/receipts/mongo/search?q=target" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Bulk Archive (Admin)

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/bulk-archive \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days_old": 90}'
```

## Document Structure

Each receipt in MongoDB contains:

```javascript
{
  receipt_id: 123,              // Link to PostgreSQL
  uploader_id: 45,              // User who uploaded
  image_url: "uploads/...",     // Image location
  status: "PROCESSED",          // Receipt status
  raw_ai_data: {...},           // AI extraction results
  metadata: {                   // Structured data
    vendor_name: "Store",
    total_amount: 45.99,
    currency: "USD",
    ...
  },
  archived: false,              // Archive flag
  created_at: ISODate(...),
  updated_at: ISODate(...),
  tags: ["groceries"],
  file_size: 2048576,
  mime_type: "image/jpeg"
}
```

## Configuration

### Environment Variables

The following environment variable is added to `.env`:

```env
MONGODB_URL=mongodb://mongouser:Admin@1234@mongodb:27017/receipts?authSource=admin
```

### Docker Compose

MongoDB service configuration:

```yaml
mongodb:
  image: mongo:7.0
  container_name: pythonmoneytracker-mongodb
  environment:
    MONGO_INITDB_ROOT_USERNAME: mongouser
    MONGO_INITDB_ROOT_PASSWORD: Admin@1234
    MONGO_INITDB_DATABASE: receipts
  ports:
    - "27017:27017"
  volumes:
    - mongodb_data:/data/db
```

## Permissions

- **Basic User**: View own receipts, search, stats
- **Receipt Logger**: All basic + archive/unarchive own receipts
- **System Admin**: All operations + bulk archive + view all users

## Backup & Maintenance

### Backup MongoDB

```bash
docker exec pythonmoneytracker-mongodb mongodump \
  --username mongouser \
  --password Admin@1234 \
  --authenticationDatabase admin \
  --db receipts \
  --out /backup
```

### Monitor Storage

```bash
curl http://localhost:5000/api/receipts/mongo/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Clean Up Old Data

Administrators can bulk archive receipts older than 90 days:

```bash
curl -X POST http://localhost:5000/api/receipts/mongo/bulk-archive \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"days_old": 90}'
```

## Performance Optimizations

### Indexes Created

The system automatically creates indexes for:
- `receipt_id` (unique)
- `uploader_id`
- `status`
- `created_at`
- `archived`
- `archive_date`
- Compound indexes for common queries

### Query Optimization

- Default queries exclude archived receipts
- Pagination support (limit/skip)
- Efficient filtering by user, status, and date
- Text search on vendor names and receipt numbers

## Migration Notes

### For Existing Deployments

1. Existing receipts in PostgreSQL will continue to work
2. New receipts will be saved to both databases
3. Old receipts are NOT automatically migrated to MongoDB
4. You can optionally write a migration script if needed

### Backward Compatibility

- All existing API endpoints continue to work
- PostgreSQL remains the primary source of truth for transactions
- MongoDB features are additive and optional
- System continues to function if MongoDB is unavailable

## Troubleshooting

### MongoDB Connection Issues

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Check logs
docker-compose logs mongodb

# Restart MongoDB
docker-compose restart mongodb
```

### Data Sync Issues

If data appears inconsistent:

1. Check application logs for errors
2. Verify both databases are accessible
3. Use stats endpoint to compare counts
4. Manually sync if necessary

## Documentation

- **Full Guide**: `MONGODB_STORAGE_GUIDE.md`
- **Quick Reference**: `MONGODB_QUICK_REFERENCE.md`
- **This Summary**: `MONGODB_IMPLEMENTATION_SUMMARY.md`

## Benefits

1. ✅ **Better Storage Management**: Easy archiving of old receipts
2. ✅ **Flexible Schema**: Handle varying receipt formats
3. ✅ **Performance**: Optimized queries with proper indexing
4. ✅ **Scalability**: MongoDB handles large document collections
5. ✅ **Search**: Efficient text search across receipt data
6. ✅ **Cost Optimization**: Archive old data without deletion
7. ✅ **Data Retention**: Maintain historical records efficiently

## Next Steps

1. **Test the Setup**: Upload a receipt and verify it appears in MongoDB
2. **Configure Backups**: Set up automated MongoDB backups
3. **Monitor Usage**: Check storage stats regularly
4. **Set Archive Policy**: Decide how long to keep active receipts
5. **(Optional) Migrate Old Data**: Write script to migrate existing receipts

## Support

For questions or issues:
1. Check the full documentation in `MONGODB_STORAGE_GUIDE.md`
2. Review the quick reference in `MONGODB_QUICK_REFERENCE.md`
3. Check application logs for error messages
4. Verify MongoDB is running and accessible

---

**Status**: ✅ Ready for Production

**Version**: 1.0.0

**Date**: December 2024
