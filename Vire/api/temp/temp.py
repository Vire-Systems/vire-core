
'{"job_uuid":"<job_uuid>", "remote":"https://github.com/user/repo_name", "user_uuid":"<user_uuid>", "framework":"<framework>","package_manager":"<package manager>","redis_url","<url>"}'


import os
path = "https://github.com/Poojit-Matukumalli/test.git".split("https://github.com")
print(path)
#print(path,os.path.basename(path))\

# A github webhook example

test ="""
{
  "ref": "refs/heads/main",
  "before": "0000000000000000000000000000000000000000",
  "after": "a747a7f8ccf4e2f9e3b9b5e5e5c3e3b9e3e3e3e3",
  "repository": {
    "id": 123456789,
    "name": "my-repo",
    "full_name": "username/my-repo",
    "private": false,
    "owner": {
      "name": "username",
      "email": "user@example.com"
    },
    "html_url": "https://github.com/username/my-repo"
  },
  "pusher": {
    "name": "username",
    "email": "user@example.com"
  },
  "sender": {
    "login": "username",
    "id": 12345,
    "avatar_url": "https://avatars.githubusercontent.com/u/12345"
  },
  "created": false,
  "deleted": false,
  "forced": false,
  "base_ref": null,
  "compare": "https://github.com/username/my-repo/compare/0000000...a747a7f",
  "commits": [
    {
      "id": "a747a7f8ccf4e2f9e3b9b5e5e5c3e3b9e3e3e3e3",
      "tree_id": "b747a7f8ccf4e2f9e3b9b5e5e5c3e3b9e3e3e3e3",
      "message": "Add new feature",
      "timestamp": "2025-01-24T10:30:00-05:00",
      "author": {
        "name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe"
      },
      "committer": {
        "name": "John Doe",
        "email": "john@example.com",
        "username": "johndoe"
      },
      "added": ["src/feature.js"],
      "removed": [],
      "modified": ["package.json"]
    }
  ],
  "head_commit": {
    "id": "a747a7f8ccf4e2f9e3b9b5e5e5c3e3b9e3e3e3e3",
    "message": "Add new feature",
    "timestamp": "2025-01-24T10:30:00-05:00",
    "author": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
"""
import json
test: dict = json.loads(test)
repo: dict = test.get("repository")
print(repo.get("name"))