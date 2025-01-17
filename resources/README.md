# Resources Directory

This directory contains static resources and assets used by the DeepSeek Chat Proxy application.

## Structure

```text
resources/
├── README.md              # This file
├── chrome-user-data/      # Chrome user profile data directory
└── chrome-win/            # Chrome binary files and dependencies
```

## Purpose

The resources directory serves several purposes:

1. House Chrome browser binaries and dependencies
2. Store Chrome user profile data
3. Maintain browser state and configurations

## Directory Details

### chrome-win/

- Contains Chrome browser executable files
- Includes necessary binary dependencies
- Used by the application to launch Chrome instances
- Should not be modified manually

### chrome-user-data/

- Stores Chrome user profiles and session data
- Contains cookies, cache, and local storage
- Maintains browser preferences and settings
- Automatically managed by the application

## Guidelines

- Do not modify chrome-win/ contents manually
- chrome-user-data/ is automatically managed by the application
- Backup chrome-user-data/ before making any changes
- Keep Chrome binaries up to date

## Notes

- Both directories are essential for proper browser automation
- chrome-user-data/ may grow in size over time
- Regular maintenance of these directories is recommended
- Some antivirus software might flag chrome-win/ - this is normal
