# Datasets

This directory contains sample datasets used for comparing Toon vs JSON formats in LLM applications.

## Dataset Descriptions

### products.json
- **Type**: E-commerce catalog
- **Size**: 100+ products
- **Structure**: Array of product objects with nested specifications, shipping info, and metadata
- **Use Case**: Demonstrates token efficiency for product catalogs with rich metadata
- **Fields Include**:
  - Basic info (id, name, description, price)
  - Category and brand information
  - Stock and inventory data
  - Nested specifications object
  - Shipping and return policies
  - Ratings and review counts

### api_response.json
- **Type**: Nested API response (GitHub repository data)
- **Size**: Single complex object with deeply nested structures
- **Structure**: Repository data with nested objects for owner, commits, issues, pull requests
- **Use Case**: Tests token efficiency for complex nested API responses
- **Fields Include**:
  - Repository metadata
  - Owner/user information
  - Commit history with file changes
  - Issues with labels, assignees, milestones
  - Pull requests with head/base branches
  - API metadata (rate limits, timestamps)

### users.json
- **Type**: User profile data
- **Size**: 50+ user profiles
- **Structure**: Array of user objects with nested preferences and activity data
- **Use Case**: Demonstrates token efficiency for user profile data with nested preferences
- **Fields Include**:
  - Profile information (name, bio, location)
  - Nested preferences (language, theme, notifications, privacy)
  - Interests array
  - Subscription details
  - Activity metrics
  - Social connections
  - Timestamps and verification status

## Usage

These datasets are used by the experiment scripts to:
1. Convert JSON to Toon format
2. Count tokens in both formats
3. Calculate cost differences
4. Test LLM performance with both formats

## File Formats

All datasets are provided in JSON format. The conversion scripts will generate Toon format versions in the `outputs/` directory.

