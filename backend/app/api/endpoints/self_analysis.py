"""
Self-Analysis API Endpoints
Provides code analysis and improvement suggestions using DeepSeek-Coder
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
import json
from datetime import datetime

from app.services.llm_service import get_llm_service
from app.services.model_orchestrator import orchestrator

router = APIRouter(prefix="/api/self-analysis", tags=["self_analysis"])

class CodeAnalyzer:
    """Analyzes codebase for improvements"""
    
    def __init__(self):
        self.llm_service = get_llm_service()
        self.orchestrator = orchestrator
        self.analysis_model = "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
        
    async def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for improvements"""
        try:
            content = file_path.read_text()
            
            prompt = f"""Analyze this {file_path.suffix} file for potential improvements:

File: {file_path.name}
```{file_path.suffix[1:]}
{content}
```

Provide analysis in the following categories:
1. Code Quality Issues
2. Performance Improvements
3. Security Concerns
4. Best Practice Violations
5. Suggested Refactoring

Format as JSON with these keys: quality_issues, performance, security, best_practices, refactoring"""

            messages = [{"role": "user", "content": prompt}]
            
            response = ""
            async for chunk in self.llm_service.generate_chat_response(
                messages=messages,
                model_name=self.analysis_model,
                max_tokens=2048,
                temperature=0.3
            ):
                response += chunk
                
            # Parse JSON response
            try:
                analysis = json.loads(response)
            except:
                # Fallback if not valid JSON
                analysis = {
                    "quality_issues": [],
                    "performance": [],
                    "security": [],
                    "best_practices": [],
                    "refactoring": response
                }
                
            return {
                "file": str(file_path),
                "analysis": analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "file": str(file_path),
                "error": str(e),
                "analyzed_at": datetime.now().isoformat()
            }
            
    async def analyze_component(self, component_path: str) -> List[Dict[str, Any]]:
        """Analyze all files in a component"""
        path = Path(component_path)
        if not path.exists():
            raise ValueError(f"Path {component_path} does not exist")
            
        files_to_analyze = []
        
        if path.is_file():
            files_to_analyze.append(path)
        else:
            # Analyze Python and TypeScript files
            for pattern in ["*.py", "*.ts", "*.tsx"]:
                files_to_analyze.extend(path.rglob(pattern))
                
        # Limit to 10 files to avoid overwhelming the system
        files_to_analyze = files_to_analyze[:10]
        
        tasks = [self.analyze_file(f) for f in files_to_analyze]
        results = await asyncio.gather(*tasks)
        
        return results

# Global analyzer instance
code_analyzer = CodeAnalyzer()

@router.get("/status")
async def get_analysis_status() -> Dict[str, Any]:
    """Get self-analysis system status"""
    model_status = await orchestrator.get_model_status()
    deepseek_status = next(
        (m for m in model_status if "deepseek" in m["name"].lower()),
        None
    )
    
    return {
        "enabled": deepseek_status is not None,
        "model_status": deepseek_status,
        "ready": deepseek_status and deepseek_status["status"] == "loaded"
    }

@router.post("/analyze-file")
async def analyze_file(file_path: str) -> Dict[str, Any]:
    """Analyze a specific file"""
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
    result = await code_analyzer.analyze_file(path)
    return result

@router.post("/analyze-component")
async def analyze_component(component_path: str) -> Dict[str, Any]:
    """Analyze a component or directory"""
    results = await code_analyzer.analyze_component(component_path)
    
    # Aggregate results
    total_issues = 0
    categories = {
        "quality_issues": [],
        "performance": [],
        "security": [],
        "best_practices": []
    }
    
    for result in results:
        if "analysis" in result:
            for category in categories:
                if category in result["analysis"]:
                    categories[category].extend(result["analysis"][category])
                    total_issues += len(result["analysis"][category])
                    
    return {
        "component": component_path,
        "files_analyzed": len(results),
        "total_issues": total_issues,
        "summary": categories,
        "details": results
    }

@router.post("/suggest-improvements")
async def suggest_improvements(
    project_path: str = "/mnt/f/assistant",
    focus_area: Optional[str] = None
) -> Dict[str, Any]:
    """Generate improvement suggestions for the project"""
    
    # Define key areas to analyze
    areas = {
        "backend": f"{project_path}/backend/app",
        "frontend": f"{project_path}/frontend/src",
        "api": f"{project_path}/backend/app/api",
        "services": f"{project_path}/backend/app/services",
        "components": f"{project_path}/frontend/src/components"
    }
    
    if focus_area and focus_area in areas:
        areas = {focus_area: areas[focus_area]}
        
    all_results = {}
    for area_name, area_path in areas.items():
        if Path(area_path).exists():
            results = await code_analyzer.analyze_component(area_path)
            all_results[area_name] = results
            
    # Generate summary report
    report = {
        "project": project_path,
        "analyzed_at": datetime.now().isoformat(),
        "areas_analyzed": list(all_results.keys()),
        "high_priority_issues": [],
        "suggested_actions": []
    }
    
    # Extract high priority issues
    for area, results in all_results.items():
        for result in results:
            if "analysis" in result and "security" in result["analysis"]:
                for issue in result["analysis"]["security"]:
                    report["high_priority_issues"].append({
                        "area": area,
                        "file": result["file"],
                        "issue": issue,
                        "type": "security"
                    })
                    
    # Generate action items
    if report["high_priority_issues"]:
        report["suggested_actions"].append(
            "Address security issues identified in the analysis"
        )
        
    return report

@router.post("/auto-refactor")
async def auto_refactor(
    file_path: str,
    dry_run: bool = True
) -> Dict[str, Any]:
    """Suggest or apply refactoring to a file"""
    
    path = Path(file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"File {file_path} not found")
        
    content = path.read_text()
    
    prompt = f"""Refactor this code to improve quality, readability, and performance:

File: {path.name}
```{path.suffix[1:]}
{content}
```

Provide the complete refactored code with improvements applied."""

    messages = [{"role": "user", "content": prompt}]
    
    refactored_code = ""
    async for chunk in code_analyzer.llm_service.generate_chat_response(
        messages=messages,
        model_name=code_analyzer.analysis_model,
        max_tokens=4096,
        temperature=0.1
    ):
        refactored_code += chunk
        
    # Extract code block if wrapped in markdown
    import re
    code_match = re.search(r'```[a-zA-Z]*\n(.*?)\n```', refactored_code, re.DOTALL)
    if code_match:
        refactored_code = code_match.group(1)
        
    result = {
        "file": str(file_path),
        "original_size": len(content),
        "refactored_size": len(refactored_code),
        "dry_run": dry_run,
        "refactored_code": refactored_code
    }
    
    if not dry_run:
        # Create backup
        backup_path = path.with_suffix(path.suffix + ".backup")
        backup_path.write_text(content)
        
        # Apply refactoring
        path.write_text(refactored_code)
        result["backup_created"] = str(backup_path)
        result["applied"] = True
        
    return result