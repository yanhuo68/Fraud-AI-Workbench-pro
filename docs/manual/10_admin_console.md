# 10. Admin Console (Sentinel Control Center)

The **Admin Console** is the restricted headquarters for platform security and user management. Access is strictly limited to users with the `admin` role.

## 🛡️ 1. User & Role Management

- **User Registry**: View all registered investigators, their active status, and last login.
- **Role Assignment**: Elevate users to `Admin`, `Data Scientist`, or `Guest`.
- **Credential Reset**: Force password resets for users or lock accounts suspicious of unauthorized access.

## 🔐 2. Role-Based Access Control (RBAC)

Sentinel uses a granular permission system:
- **Pages**: Control which UI tabs are visible to specific roles.
- **Actions**: Restrict high-impact operations (like "Clean Database") to top-tier administrators.
- **API Scopes**: Manage which backend routes are accessible via technical API keys.

## 📈 3. System Auditing

- **Audit Logs**: Track who accessed which investigative module and when.
- **Global Settings**: Update platform-wide configurations, such as default LLM providers, session timeouts, and database connection strings.

> [!CAUTION]
> Changes made in the Admin Console affect all users globally. Proceed with extreme caution when modifying role permissions or clearing system caches.
