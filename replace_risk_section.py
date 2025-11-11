"""Script to replace the Risk Analysis section with cleaner version"""

# Read the main app.py
with open('src/frontend/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Read the clean version (skip the first 2 lines which are comments)
with open('src/frontend/risk_analysis_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    clean_section = ''.join(lines[2:])  # Skip first 2 comment lines

# Find the start and end of Risk Analysis section
start_marker = 'elif page == "📊 Risk Analysis":'
end_marker = 'elif page == "📰 Market News":'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("ERROR: Could not find Risk Analysis section markers")
    exit(1)

# Replace the section
new_content = content[:start_idx] + clean_section + '\n' + content[end_idx:]

# Write back
with open('src/frontend/app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully replaced Risk Analysis section!")
print(f"   Old section: {len(content[start_idx:end_idx])} characters")
print(f"   New section: {len(clean_section)} characters")
print(f"   Total file size: {len(new_content)} characters")
