# MongoDB Receipt Storage Guide

## Overview

This application now uses MongoDB for receipt document storage alongside PostgreSQL. This hybrid approach provides:

- **PostgreSQL**: Stores structured transaction data, user information, and relationships
- **MongoDB**: Stores receipt documents, images, extracted data, and provides flexible archiving

## Architecture

### Why Hybrid Storage?

1. **PostgreSQL** is ideal for:
   - Structured financial transactions
   - User authentication and authorization
   - ACID compliance for critical financial data
   - Complex relational queries

2. **MongoDB** is ideal for:
   - Unstructured receipt documents
   - Large binary data (images)
   - Flexible schema for AI-extracted data
   - Easy archiving and data lifecycle management
   - Efficient storage of varying receipt formats

## Receipt Document Structure

Each receipt stored in MongoDB has the following structure:

```json
{
  "receipt_id": 123,                    // Reference to PostgreSQL receipt ID
  "uploader_id": 45,                    // User who uploaded
  "image_url": "uploads/receipt.jpg",   // Location of receipt image
  "image_data": "<Binary>",             // Optional: actual image data
  "status": "PROCESSED",                // PENDING, PENDING_CONFIRMATION, PROCESSED, ERROR
  "raw_ai_data": {                      // Raw extraction from Gemini AI
    "vendor_name": "Target",
    "total_amount": "45.99",
    "items": [...]
  },
  "extracted_items": [                  // Parsed line items
    {
      "description": "Item 1",
      "amount": 12.99,
      "quantity": 2,
      "unit_price": 6.50
    }
  ],
  "metadata": {                         // Structured metadata
    "vendor_name": "Target",
    "total_amount": 45.99,
    "currency": "USD",
    "transaction_date": "2024-12-05T10:30:00",
    "receipt_number": "INV-12345"
  },
  "archived": false,                    // Archive flag
  "archive_date": null,                 // When archived
  "archive_reason": null,               // Why archived
  "created_at": "2024-12-05T10:00:00",
  "updated_at": "2024-12-05T10:05:00",
  "tags": ["groceries", "2024"],        // Custom tags
  "file_size": 2048576,                 // Size in bytes
  "mime_type": "image/jpeg"             // Image format
}
```

## API Endpoints

### Get Receipt from MongoDB

```http
GET /api/receipts/mongo/<receipt_id>
Authorization: Bearer <token>
```

Query Parameters:
- `include_archived` (optional): Set to `true` to include archived receipts

Response:
```json
{
  "receipt": {
    "_id": "507f1f77bcf86cd799439011",
    "receipt_id": 123,
    "uploader_id": 45,
    ...
  }
}
```

### Get User's Receipts

```http
GET /api/receipts/mongo/user/<user_id>
Authorization: Bearer <token>
```

Query Parameters:
- `include_archived` (optional): Include archived receipts (default: false)
- `limit` (optional): Max results (default: 100, max: 500)
- `skip` (optional): Skip N results for pagination (default: 0)

Response:
```json
{
  "receipts": [...],
  "count": 25,
  "limit": 100,
  "skip": 0
}
```

### Archive Receipt

```http
POST /api/receipts/mongo/archive/<receipt_id>
Authorization: Bearer <token>
Content-Type: application/json

{
  "reason": "old_data"
}
```

Response:
```json
{
  "message": "Receipt archived successfully",
  "receipt_id": 123,
  "reason": "old_data"
}
```

### Unarchive Receipt

```http
POST /api/receipts/mongo/unarchive/<receipt_id>
Authorization: Bearer <token>
```

Response:
```json
{
  "message": "Receipt unarchived successfully",
  "receipt_id": 123
}
```

### Get Archived Receipts

```http
GET /api/receipts/mongo/archived
Authorization: Bearer <token>
```

Query Parameters:
- `days_old` (optional): Filter receipts archived more than N days ago

Response:
```json
{
  "archived_receipts": [...],
  "count": 15
}
```

### Get Receipt Statistics

```http
GET /api/receipts/mongo/stats
Authorization: Bearer <token>
```

Query Parameters:
- `user_id` (optional): Get stats for specific user (admin only)

Response:
```json
{
  "stats": {
    "total": 100,
    "archived": 20,
    "active": 80,
    "pending": 5,
    "confirmed": 75,
    "total_size": 52428800
  }
}
```

### Search Receipts

```http
GET /api/receipts/mongo/search?q=target&include_archived=false
Authorization: Bearer <token>
```

Query Parameters:
- `q` (required): Search query text
- `include_archived` (optional): Include archived receipts (default: false)

Response:
```json
{
  "results": [...],
  "count": 3,
  "query": "target"
}
```

### Bulk Archive Old Receipts

```http
POST /api/receipts/mongo/bulk-archive
Authorization: Bearer <token>
Content-Type: application/json

{
  "days_old": 90,
  "user_id": 45  // optional
}
```

Response:
```json
{
  "message": "Successfully archived 15 receipts",
  "archived_count": 15,
  "days_old": 90
}
```

**Note:** This endpoint requires System Admin role and enforces a minimum of 30 days.

## Archiving Strategy

### Why Archive?

Archiving allows you to:
1. **Reduce active dataset size** for better performance
2. **Maintain historical records** without deletion
3. **Easy restoration** if needed
4. **Cost management** for cloud storage
5. **Compliance** with data retention policies

### Archive Reasons

Common archive reasons:
- `user_requested` - User manually archived
- `old_data` - Data older than threshold
- `processed` - Receipt fully processed
- `deleted` - User "deleted" (soft delete)
- `auto_archived_after_X_days` - Automated archiving

### Best Practices

1. **Regular Archiving**: Set up automated jobs to archive receipts older than 90 days
2. **User Control**: Allow users to archive their own receipts
3. **Search Before Archive**: Ensure receipts are properly tagged before archiving
4. **Backup Before Bulk Operations**: Always backup before bulk archiving
5. **Monitor Storage**: Track MongoDB storage usage via stats endpoint

## Docker Setup

The MongoDB service is configured in `docker-compose.yml`:

```yaml
mongodb:
  image: mongo:7.0
  container_name: pythonmoneytracker-mongodb
  restart: unless-stopped
  environment:
    MONGO_INITDB_ROOT_USERNAME: mongouser
    MONGO_INITDB_ROOT_PASSWORD: Admin@1234
    MONGO_INITDB_DATABASE: receipts
  ports:
    - "27017:27017"
  volumes:
    - mongodb_data:/data/db
    - mongodb_config:/data/configdb
```

### Environment Variables

Add to your `.env` file:

```env
MONGODB_URL=mongodb://mongouser:Admin@1234@mongodb:27017/receipts?authSource=admin
```

For local development (outside Docker):
```env
MONGODB_URL=mongodb://mongouser:Admin@1234@localhost:27017/receipts?authSource=admin
```

## Starting the Services

```bash
# Start all services including MongoDB
docker-compose up -d

# Check MongoDB is running
docker-compose ps

# View MongoDB logs
docker-compose logs -f mongodb

# Access MongoDB shell
docker exec -it pythonmoneytracker-mongodb mongosh -u mongouser -p Admin@1234 --authenticationDatabase admin
```

## MongoDB Operations

### Connect to MongoDB Shell

```bash
docker exec -it pythonmoneytracker-mongodb mongosh -u mongouser -p Admin@1234 --authenticationDatabase admin
```

### Common MongoDB Commands

```javascript
// Switch to receipts database
use receipts

// Count total receipts
db.receipts.countDocuments()

// Count archived receipts
db.receipts.countDocuments({ archived: true })

// Find receipts by user
db.receipts.find({ uploader_id: 45 })

// Find pending receipts
db.receipts.find({ status: "PENDING" })

// Find receipts archived in last 7 days
db.receipts.find({
  archived: true,
  archive_date: { $gte: new Date(Date.now() - 7*24*60*60*1000) }
})

// Get storage stats
db.receipts.stats()

// List all indexes
db.receipts.getIndexes()
```

## Performance Optimization

### Indexes

The following indexes are automatically created:

- `receipt_id` (unique)
- `uploader_id`
- `status`
- `created_at` (descending)
- `archived`
- `archive_date`
- `(uploader_id, status)` (compound)
- `(archived, created_at)` (compound)

### Query Optimization Tips

1. **Use filters**: Always filter by `archived: false` for active receipts
2. **Limit results**: Use pagination with `limit` and `skip`
3. **Project fields**: Only request needed fields
4. **Use indexes**: Ensure queries use indexed fields

## Integration with Existing Workflow

### Upload Flow

1. User uploads receipt → PostgreSQL + **MongoDB**
2. AI extracts data → Stored in **MongoDB**
3. User confirms → PostgreSQL transaction + **MongoDB** update
4. Receipt processed → Status updated in both systems

### Archive Flow

1. User requests archive OR automated job triggers
2. **MongoDB** document marked as `archived: true`
3. PostgreSQL receipt remains unchanged
4. Archived receipts excluded from default queries
5. Can be unarchived anytime

## Backup and Restore

### Backup MongoDB

```bash
# Backup all databases
docker exec pythonmoneytracker-mongodb mongodump --username mongouser --password Admin@1234 --authenticationDatabase admin --out /backup

# Copy backup to host
docker cp pythonmoneytracker-mongodb:/backup ./mongodb-backup

# Backup specific database
docker exec pythonmoneytracker-mongodb mongodump --username mongouser --password Admin@1234 --authenticationDatabase admin --db receipts --out /backup
```

### Restore MongoDB

```bash
# Copy backup to container
docker cp ./mongodb-backup pythonmoneytracker-mongodb:/backup

# Restore database
docker exec pythonmoneytracker-mongodb mongorestore --username mongouser --password Admin@1234 --authenticationDatabase admin /backup
```

## Monitoring

### Health Check

Check MongoDB status via API:

```bash
curl http://localhost:5000/api/health
```

Response includes MongoDB connection status:
```json
{
  "services": {
    "database": "connected",
    "mongodb": "connected",
    "gemini_api": "configured"
  }
}
```

### Storage Monitoring

```javascript
// In MongoDB shell
use receipts

// Database stats
db.stats()

// Collection stats
db.receipts.stats()

// Data size by status
db.receipts.aggregate([
  { $group: {
    _id: "$status",
    count: { $sum: 1 },
    totalSize: { $sum: "$file_size" }
  }}
])
```

## Troubleshooting

### MongoDB Connection Issues

1. **Check MongoDB is running**:
   ```bash
   docker-compose ps mongodb
   ```

2. **Check logs**:
   ```bash
   docker-compose logs mongodb
   ```

3. **Verify connection string**:
   ```bash
   echo $MONGODB_URL
   ```

4. **Test connection manually**:
   ```bash
   docker exec -it pythonmoneytracker-mongodb mongosh -u mongouser -p Admin@1234
   ```

### Application Won't Start

If MongoDB connection fails, the application will still start but log warnings. MongoDB features will be unavailable until connection is restored.

### Data Sync Issues

If PostgreSQL and MongoDB get out of sync:

1. Check logs for errors
2. Verify receipt exists in both systems
3. Use `/api/receipts/mongo/stats` to check counts
4. Manually resync if needed

## Security Considerations

1. **Authentication**: MongoDB requires username/password
2. **Network**: MongoDB only accessible within Docker network
3. **Authorization**: API endpoints check user permissions
4. **Audit Logs**: All archive/unarchive operations are logged
5. **Data Privacy**: Receipts only accessible by owner or admin

## Migration Guide

If you're adding this to an existing system:

1. **Start MongoDB** container
2. **Install dependencies**: `pip install pymongo`
3. **Update environment** variables
4. **Restart backend** service
5. **Verify health check** shows MongoDB connected
6. **Existing receipts** remain in PostgreSQL only
7. **New receipts** will be stored in both systems
8. **(Optional)** Migrate existing receipts to MongoDB

## Future Enhancements

Potential improvements:
- Store actual image data in MongoDB GridFS
- Implement automatic archiving cron jobs
- Add receipt tagging system
- Implement full-text search
- Add receipt versioning
- Cloud storage integration (S3, R2)
- Implement data lifecycle policies
