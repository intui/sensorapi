# 🔗 Connect GitHub MCP Server to Claude Desktop

## Overview

The GitHub MCP (Model Context Protocol) server allows Claude Desktop to directly interact with GitHub repositories, read code, create issues, manage pull requests, and more.

## Prerequisites

- Claude Desktop installed
- Node.js 16+ installed
- Git configured with GitHub access
- GitHub Personal Access Token

## Step 1: Install GitHub MCP Server

### Option A: Install via npm (Recommended)

```bash
npm install -g @modelcontextprotocol/server-github
```

### Option B: Clone and build from source

```bash
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/github
npm install
npm run build
```

## Step 2: Create GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes you need:
   - `repo` - Full repository access
   - `read:org` - Read organization data
   - `read:user` - Read user profile data
   - `user:email` - Read user email

4. Copy the generated token (starts with `ghp_` or `github_pat_`)

## Step 3: Configure Claude Desktop

### Find Claude Desktop Config File

**macOS:**

```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**

```bash
%APPDATA%/Claude/claude_desktop_config.json
```

**Linux:**

```bash
~/.config/Claude/claude_desktop_config.json
```

### Create/Edit Configuration File

Create or edit the `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

### Alternative: Using Local Installation

If you built from source:

```json
{
  "mcpServers": {
    "github": {
      "command": "node",
      "args": ["/path/to/servers/build/github/index.js"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_token_here"
      }
    }
  }
}
```

## Step 4: Restart Claude Desktop

1. Completely quit Claude Desktop
2. Restart the application
3. Look for MCP server connection status

## Step 5: Test the Connection

Try these commands in Claude Desktop:

1. **List repositories:**

   ```
   List my GitHub repositories
   ```

2. **Read a file:**

   ```
   Show me the README.md file from my sensorapi repository
   ```

3. **Check repository status:**

   ```
   What's the current status of my sensorapi repository?
   ```

## Troubleshooting

### Connection Issues

1. **Check token permissions:**
   - Ensure token has required scopes
   - Verify token is not expired

2. **Verify config file:**

   ```bash
   # Check if config file is valid JSON
   cat ~/.config/Claude/claude_desktop_config.json | jq .
   ```

3. **Check Claude Desktop logs:**
   - Look for MCP server startup messages
   - Check for authentication errors

### Common Errors

**"MCP server not found":**

- Ensure `@modelcontextprotocol/server-github` is installed globally
- Try full path to the server executable

**"Authentication failed":**

- Check if GitHub token is correct
- Verify token has necessary permissions
- Try regenerating the token

**"Connection refused":**

- Restart Claude Desktop completely
- Check if Node.js is in system PATH

## Advanced Configuration

### Multiple GitHub Accounts

```json
{
  "mcpServers": {
    "github-personal": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "personal_token_here"
      }
    },
    "github-work": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "work_token_here"
      }
    }
  }
}
```

### Custom GitHub Enterprise

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token",
        "GITHUB_API_URL": "https://github.enterprise.com/api/v3"
      }
    }
  }
}
```

## Security Best Practices

1. **Token Management:**
   - Use tokens with minimal required permissions
   - Set expiration dates on tokens
   - Rotate tokens regularly

2. **Config File Security:**

   ```bash
   # Restrict config file permissions (macOS/Linux)
   chmod 600 ~/.config/Claude/claude_desktop_config.json
   ```

3. **Environment Variables:**
   Consider using system environment variables instead of storing tokens in config:

   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
         }
       }
     }
   }
   ```

## Verification Commands

Once connected, you can use these commands to verify functionality:

```
# Repository operations
- "List my repositories"
- "Show me the issues in [repo-name]"
- "What are the recent commits in [repo-name]?"

# File operations  
- "Read the README from [repo-name]"
- "Show me the package.json in [repo-name]"
- "List files in [repo-name]/src directory"

# Repository analysis
- "Analyze the code structure of [repo-name]"
- "What dependencies does [repo-name] use?"
- "Show me the latest release of [repo-name]"
```

## Support Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/github)
- [Claude Desktop MCP Guide](https://claude.ai/docs/mcp)

---

**Note:** The GitHub MCP server provides read-only access by default. Write operations (creating issues, PRs, etc.) may require additional configuration and permissions.
