import sys, re

f = 'frontend/src/pages/DashboardPage.jsx'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

content = re.sub(
    r'\{\s*label:\s*"Smart",\s*value:\s*"smart",\s*icon:\s*<Sparkles className="w-3 h-3"\s*/>\s*\},',
    '{ label: "KNN", value: "knn", icon: <Sparkles className="w-3 h-3" /> },\\n                { label: "Smart", value: "smart", icon: <Sparkles className="w-3 h-3" /> },',
    content
)

content = re.sub(
    r'\{\s*label:\s*"Isolation",\s*value:\s*"isolation"\s*\},',
    '{ label: "Isolation", value: "isolation" },\\n                  { label: "MAD", value: "mad" },\\n                  { label: "LOF", value: "lof" },\\n                  { label: "Hybrid", value: "hybrid" },',
    content
)

content = re.sub(r'className="grid grid-cols-2 md:grid-cols-5 gap-3"', 'className="grid grid-cols-3 md:grid-cols-6 gap-2"', content)
content = re.sub(r'className="grid grid-cols-3 gap-3"', 'className="grid grid-cols-3 md:grid-cols-6 gap-3"', content)

with open(f, 'w', encoding='utf-8') as file:
    file.write(content)

print("SUCCESS")
