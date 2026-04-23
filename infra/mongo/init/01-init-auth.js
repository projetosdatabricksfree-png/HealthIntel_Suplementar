// Initialize MongoDB with root user
const username = process.env.MONGO_INITDB_ROOT_USERNAME || 'healthintel';
const password = process.env.MONGO_INITDB_ROOT_PASSWORD || 'healthintel';

admin = db.getSiblingDB('admin');

try {
  admin.createUser({
    user: username,
    pwd: password,
    roles: [
      { role: 'root', db: 'admin' }
    ]
  });
  print('Admin user created successfully');
} catch (e) {
  print('User already exists or error: ' + e.message);
}
