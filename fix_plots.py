import re

f = 'frontend/src/pages/DashboardPage.jsx'
with open(f, 'r', encoding='utf-8') as file:
    content = file.read()

target1 = """<img src={getPlotUrl('summary')} alt="SHAP Summary" className="w-full h-auto rounded-lg border border-white/10 bg-white" onError={(e)=>e.target.style.display='none'} />"""
replace1 = """{metrics.explainability?.plot_base64 && <img src={`data:image/png;base64,${metrics.explainability.plot_base64}`} alt="SHAP Summary" className="w-full h-auto rounded-lg border border-white/10 bg-white" />}"""

target2 = """<img src={getPlotUrl('bar')} alt="SHAP Bar" className="w-full h-auto rounded-lg border border-white/10 bg-white" onError={(e)=>e.target.style.display='none'} />"""
replace2 = """{metrics.explainability?.bar_plot_base64 && <img src={`data:image/png;base64,${metrics.explainability.bar_plot_base64}`} alt="SHAP Bar" className="w-full h-auto rounded-lg border border-white/10 bg-white" />}"""

content = content.replace(target1, replace1)
content = content.replace(target2, replace2)

with open(f, 'w', encoding='utf-8') as file:
    file.write(content)

print('SUCCESS')
