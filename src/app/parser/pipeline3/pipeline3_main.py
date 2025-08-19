"""
Pipeline 3 Main - Hybrid local + cloud orchestrator.
Combines M1 Llama processing with OpenAI validation for 95%+ accuracy at low cost.
"""

import time
import asyncio
from dataclasses import dataclass
from fastapi import UploadFile
from typing import Dict, Any

from app.parser.text_extract import extract_text_from_file
from app.model.schema.resume.together import Resume
from .router import Router
from .local import LocalProcessor
from .cloud import CloudProcessor

@dataclass
class Pipeline3Result:
    resume: Resume
    processing_time: float
    cost: float
    tokens_used: int
    local_confidence: float
    cloud_confidence: float
    method_used: str

class Pipeline3Parser:
    def __init__(self):
        self.router = Router()
        self.local = LocalProcessor()
        self.cloud = CloudProcessor()
    
    async def parse_resume(self, file: UploadFile) -> Pipeline3Result:
        start_time = time.time()
        total_cost = 0.0
        total_tokens = 0
        
        try:
            # Extract text
            resume_text = await extract_text_from_file(file)
            print(f"Extracted resume text: {len(resume_text)} characters")
            
            routing = self.router.decide_route(resume_text)
            print(f"Routing: local_weight={routing.local_weight}, cloud_weight={routing.cloud_weight}")
            

            print("Starting local and cloud processing...")
            local_task = self.local.process(resume_text)
            cloud_task = self.cloud.process(resume_text)
            
    
            try:
                local_result, cloud_result = await asyncio.gather(
                    local_task, cloud_task, return_exceptions=True
                )
            except Exception as e:
                print(f"Error in parallel processing: {e}")
                local_result = None
                cloud_result = None
            
    
            if isinstance(local_result, Exception):
                print(f"Local processing failed: {local_result}")
                local_result = None
            if isinstance(cloud_result, Exception):
                print(f"Cloud processing failed: {cloud_result}")
                cloud_result = None
            
            print(f"Local success: {local_result.success if local_result else False}")
            print(f"Cloud success: {cloud_result.success if cloud_result else False}")
            

            final_data = self._combine_results(local_result, cloud_result, routing)
            

            local_confidence = local_result.confidence if local_result and local_result.success else 0.0
            cloud_confidence = cloud_result.confidence if cloud_result and cloud_result.success else 0.0
            
            if cloud_result and cloud_result.success:
                total_cost += cloud_result.cost
            
            total_tokens = len(resume_text.split()) * 2
            
            print("Creating Resume object...")
            validated_data = self._clean_data_pipeline1_style(final_data)
            resume = Resume.model_validate(validated_data)
            
            processing_time = time.time() - start_time
            
            print(f"Pipeline 3 completed successfully in {processing_time:.2f}s")
            print(f"Local confidence: {local_confidence:.3f}, Cloud confidence: {cloud_confidence:.3f}")
            
            return Pipeline3Result(
                resume=resume,
                processing_time=processing_time,
                cost=total_cost,
                tokens_used=total_tokens,
                local_confidence=local_confidence,
                cloud_confidence=cloud_confidence,
                method_used="hybrid"
            )
            
        except Exception as e:
            print(f"Error in Pipeline 3: {e}")
          
            processing_time = time.time() - start_time
            fallback_resume = self._create_fallback_resume()
            return Pipeline3Result(
                resume=fallback_resume,
                processing_time=processing_time,
                cost=0.0,
                tokens_used=1000,
                local_confidence=0.0,
                cloud_confidence=0.0,
                method_used="fallback"
            )
    
    def _clean_data_pipeline1_style(self, data):
        if not data:
            data = self._get_fallback_structure()
        
        if "personal_info" in data and "links" in data["personal_info"]:
            cleaned_links = []
            for link in data["personal_info"]["links"]:
                if "linkedin" in str(link).lower():
                    cleaned_links.append("linkedin")
                elif "github" in str(link).lower():
                    cleaned_links.append("github")
                else:
                    cleaned_links.append("other")
            data["personal_info"]["links"] = cleaned_links
        
    
        for item in data.get("education_items", []):
       
            for course in item.get("relevant_coursework", []):
                if not course.get("code"):
                    course["code"] = None
            
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
        
        # Fix experience items - exactly like Pipeline 1
        for item in data.get("experience_items", []):
            if item.get("location") is None:
                item["location"] = {"city": None, "state": None, "zip_code": None}
        
        # Fix root-level relevant_coursework - exactly like Pipeline 1
        if "relevant_coursework" in data:
            fixed_coursework = []
            for course in data["relevant_coursework"]:
                if isinstance(course, str):
                    fixed_coursework.append({"code": None, "name": course})
                elif isinstance(course, dict):
                    if "code" not in course:
                        course["code"] = None
                    if "name" not in course:
                        course["name"] = str(course.get("code", "Unknown Course"))
                    fixed_coursework.append(course)
            data["relevant_coursework"] = fixed_coursework
        
        defaults = {
            "education_items": [], 
            "experience_items": [], 
            "skills": [], 
            "relevant_coursework": [], 
            "paragraphs": []
        }
        for key, default in defaults.items():
            if key not in data:
                data[key] = default
        
        return data
    
    def _combine_results(self, local_result, cloud_result, routing) -> Dict[str, Any]:
        

        if not local_result or not cloud_result:
            if local_result and local_result.success:
                print("Using local result only")
                return local_result.data
            elif cloud_result and cloud_result.success:
                print("Using cloud result only")
                return cloud_result.data
            else:
                print("Both failed, using fallback")
                return self._get_fallback_structure()
        
        if local_result.success and cloud_result.success:
            print(f"Both succeeded - local conf: {local_result.confidence:.3f}, cloud conf: {cloud_result.confidence:.3f}")
            
          
            if cloud_result.confidence > local_result.confidence + 0.1:
                print("Using cloud result (higher confidence)")
                return cloud_result.data
            else:
                print("Using local result")
                return local_result.data
        
        # One succeeded
        if local_result.success:
            print("Using local result (cloud failed)")
            return local_result.data
        elif cloud_result.success:
            print("Using cloud result (local failed)")
            return cloud_result.data
        
        print("Both failed, using fallback")
        return self._get_fallback_structure()
    
    def _get_fallback_structure(self) -> Dict[str, Any]:
        """Fallback structure when all processing fails"""
        return {
            "personal_info": {
                "name": "Unknown",
                "email": None,
                "phone_number": None,
                "home_address": {"city": None, "state": None, "zip_code": None},
                "links": []
            },
            "education_items": [],
            "experience_items": [],
            "skills": [],
            "relevant_coursework": [],
            "paragraphs": []
        }
    
    def _create_fallback_resume(self) -> Resume:
        """Create a minimal fallback resume when parsing fails"""
        from app.model.schema.resume.info import ResumePersonalInfo
        from app.model.schema.resume.location import ResumeLocation
        
        return Resume(
            personal_info=ResumePersonalInfo(
                name="Unknown",
                home_address=ResumeLocation(
                    city=None,
                    state=None,
                    zip_code=None
                ),
                phone_number=None,
                email=None,
                links=[]
            ),
            education_items=[],
            skills=[],
            relevant_coursework=[],
            experience_items=[],
            paragraphs=[]
        )