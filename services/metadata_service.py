import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter
from pathlib import Path

class MetadataService:
    """Service for generating and managing metadata for processed questions"""
    
    def __init__(self):
        self.standard_subjects = [
            "Mathematics", "Science", "English", "History", "Geography", 
            "Physics", "Chemistry", "Biology", "Computer Science", "Economics",
            "Literature", "Philosophy", "Psychology", "Sociology", "Art"
        ]
        
        self.difficulty_keywords = {
            "easy": ["basic", "simple", "recall", "remember", "identify", "list"],
            "medium": ["explain", "describe", "compare", "analyze", "apply"],
            "hard": ["evaluate", "create", "synthesize", "critique", "design"]
        }
    
    def generate_metadata(self, filename: str, questions: List[str], 
                         quality_results: List[Dict], custom_tags: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for processed questions
        """
        start_time = time.time()
        
        # Basic file metadata
        file_info = self._extract_file_metadata(filename)
        
        # Content analysis
        content_analysis = self._analyze_content(questions)
        
        # Quality metrics
        quality_metrics = self._calculate_quality_metrics(quality_results)
        
        # Question distribution analysis
        distribution_analysis = self._analyze_question_distribution(questions, quality_results)
        
        # Generate custom metadata tags
        generated_tags = self._generate_automatic_tags(questions, quality_results)
        
        # Combine with user-provided custom tags
        all_tags = generated_tags
        if custom_tags:
            all_tags.extend(self._process_custom_tags(custom_tags))
        
        processing_time = time.time() - start_time
        
        metadata = {
            "metadata_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 2),
            
            # File information
            "source_file": {
                "name": filename,
                "type": file_info["type"],
                "size_category": file_info["size_category"],
                "estimated_size_mb": file_info["estimated_size_mb"]
            },
            
            # Content analysis
            "content_analysis": content_analysis,
            
            # Question metrics
            "question_metrics": {
                "total_questions": len(questions),
                "questions_with_quality_analysis": len(quality_results),
                "average_question_length": self._calculate_average_length(questions),
                "question_length_distribution": self._analyze_length_distribution(questions)
            },
            
            # Quality metrics
            "quality_metrics": quality_metrics,
            
            # Distribution analysis
            "distribution_analysis": distribution_analysis,
            
            # Metadata tags
            "tags": all_tags,
            
            # Processing info
            "processing_info": {
                "extraction_method": "openai_gpt",
                "quality_analysis_enabled": len(quality_results) > 0,
                "openai_model": "gpt-3.5-turbo",
                "processing_timestamp": datetime.now().isoformat()
            }
        }
        
        return metadata
    
    def _extract_file_metadata(self, filename: str) -> Dict[str, Any]:
        """Extract basic metadata from filename"""
        file_path = Path(filename)
        extension = file_path.suffix.lower()
        
        file_types = {
            '.pdf': 'PDF Document',
            '.docx': 'Word Document',
            '.doc': 'Word Document',
            '.xlsx': 'Excel Spreadsheet',
            '.xls': 'Excel Spreadsheet',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.png': 'PNG Image',
            '.tiff': 'TIFF Image',
            '.bmp': 'Bitmap Image'
        }
        
        return {
            "type": file_types.get(extension, "Unknown"),
            "extension": extension,
            "size_category": "unknown",
            "estimated_size_mb": 0  # Would need actual file for real size
        }
    
    def _analyze_content(self, questions: List[str]) -> Dict[str, Any]:
        """Analyze content characteristics of questions"""
        if not questions:
            return {
                "estimated_subject": "Unknown",
                "confidence": 0.0,
                "topics_identified": [],
                "language": "English",
                "reading_level": "Unknown"
            }
        
        # Combine all questions for analysis
        all_text = " ".join(questions).lower()
        
        # Subject detection based on keywords
        subject_scores = {}
        subject_keywords = {
            "Mathematics": ["equation", "calculate", "solve", "formula", "number", "algebra", "geometry"],
            "Science": ["experiment", "hypothesis", "theory", "molecule", "atom", "cell", "energy"],
            "English": ["grammar", "sentence", "paragraph", "literature", "author", "poem", "story"],
            "History": ["century", "war", "empire", "civilization", "ancient", "modern", "revolution"],
            "Geography": ["continent", "country", "climate", "mountain", "river", "population", "capital"],
            "Computer Science": ["algorithm", "program", "code", "software", "hardware", "database", "network"]
        }
        
        for subject, keywords in subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                subject_scores[subject] = score
        
        # Determine primary subject
        if subject_scores:
            primary_subject = max(subject_scores, key=subject_scores.get)
            confidence = subject_scores[primary_subject] / len(questions)
        else:
            primary_subject = "General"
            confidence = 0.5
        
        # Topic identification (simple keyword extraction)
        topics = self._extract_topics(all_text)
        
        return {
            "estimated_subject": primary_subject,
            "confidence": round(confidence, 2),
            "subject_scores": subject_scores,
            "topics_identified": topics[:10],  # Top 10 topics
            "language": "English",  # Default, could be enhanced with language detection
            "reading_level": self._estimate_reading_level(questions)
        }
    
    def _calculate_quality_metrics(self, quality_results: List[Dict]) -> Dict[str, Any]:
        """Calculate overall quality metrics from individual question analyses"""
        if not quality_results:
            return {
                "average_overall_score": "unknown",
                "score_distribution": {},
                "average_clarity": 0.0,
                "average_educational_value": 0.0,
                "average_grammar": 0.0,
                "questions_needing_improvement": 0,
                "excellent_questions": 0
            }
        
        # Calculate averages
        clarity_scores = [r.get("clarity_score", 0) for r in quality_results]
        educational_scores = [r.get("educational_value", 0) for r in quality_results]
        grammar_scores = [r.get("grammar_score", 0) for r in quality_results]
        
        # Count score distributions
        overall_scores = [r.get("overall_score", "unknown") for r in quality_results]
        score_distribution = dict(Counter(overall_scores))
        
        # Count questions needing improvement (score < 6.0)
        poor_questions = sum(1 for r in quality_results 
                           if any(r.get(score_key, 0) < 6.0 
                                for score_key in ["clarity_score", "educational_value", "grammar_score"]))
        
        excellent_questions = sum(1 for r in quality_results 
                                if r.get("overall_score") == "excellent")
        
        return {
            "average_overall_score": max(score_distribution, key=score_distribution.get) if score_distribution else "unknown",
            "score_distribution": score_distribution,
            "average_clarity": round(sum(clarity_scores) / len(clarity_scores), 2) if clarity_scores else 0.0,
            "average_educational_value": round(sum(educational_scores) / len(educational_scores), 2) if educational_scores else 0.0,
            "average_grammar": round(sum(grammar_scores) / len(grammar_scores), 2) if grammar_scores else 0.0,
            "questions_needing_improvement": poor_questions,
            "excellent_questions": excellent_questions,
            "quality_analysis_coverage": f"{len(quality_results)} questions analyzed"
        }
    
    def _analyze_question_distribution(self, questions: List[str], quality_results: List[Dict]) -> Dict[str, Any]:
        """Analyze the distribution of question types and difficulties"""
        if not questions:
            return {}
        
        # Question type distribution
        question_types = []
        difficulties = []
        
        for result in quality_results:
            if "question_type" in result:
                question_types.append(result["question_type"])
            if "estimated_difficulty" in result:
                difficulties.append(result["estimated_difficulty"])
        
        # Fallback analysis based on question text
        if not question_types:
            question_types = self._classify_question_types(questions)
        
        if not difficulties:
            difficulties = self._estimate_difficulties(questions)
        
        return {
            "question_types": dict(Counter(question_types)),
            "difficulty_levels": dict(Counter(difficulties)),
            "total_questions_analyzed": len(questions)
        }
    
    def _generate_automatic_tags(self, questions: List[str], quality_results: List[Dict]) -> List[Dict[str, Any]]:
        """Generate automatic metadata tags based on content analysis"""
        tags = []
        
        if not questions:
            return tags
        
        # Content-based tags
        all_text = " ".join(questions).lower()
        
        # Educational level tags
        if any(word in all_text for word in ["basic", "fundamental", "introduction"]):
            tags.append({
                "key": "educational_level",
                "value": "beginner",
                "category": "difficulty",
                "confidence": 0.7
            })
        elif any(word in all_text for word in ["advanced", "complex", "detailed"]):
            tags.append({
                "key": "educational_level",
                "value": "advanced",
                "category": "difficulty", 
                "confidence": 0.8
            })
        
        # Question format tags
        if any("A)" in q or "B)" in q for q in questions):
            tags.append({
                "key": "format",
                "value": "multiple_choice",
                "category": "question_type",
                "confidence": 0.9
            })
        
        # Assessment type tags
        if len(questions) > 20:
            tags.append({
                "key": "assessment_type",
                "value": "comprehensive_exam",
                "category": "scope",
                "confidence": 0.8
            })
        elif len(questions) < 5:
            tags.append({
                "key": "assessment_type", 
                "value": "quiz",
                "category": "scope",
                "confidence": 0.7
            })
        
        # Quality-based tags
        if quality_results:
            avg_quality = sum(1 for r in quality_results if r.get("overall_score") in ["excellent", "good"]) / len(quality_results)
            if avg_quality > 0.8:
                tags.append({
                    "key": "quality_status",
                    "value": "high_quality",
                    "category": "quality",
                    "confidence": 0.9
                })
        
        return tags
    
    def _process_custom_tags(self, custom_tags: List[Dict]) -> List[Dict[str, Any]]:
        """Process and validate custom tags provided by user"""
        processed_tags = []
        
        for tag in custom_tags:
            if isinstance(tag, dict) and "key" in tag and "value" in tag:
                processed_tag = {
                    "key": str(tag["key"]),
                    "value": str(tag["value"]),
                    "category": tag.get("category", "custom"),
                    "confidence": tag.get("confidence", 1.0),
                    "source": "user_provided"
                }
                processed_tags.append(processed_tag)
        
        return processed_tags
    
    def _calculate_average_length(self, questions: List[str]) -> float:
        """Calculate average length of questions in characters"""
        if not questions:
            return 0.0
        return round(sum(len(q) for q in questions) / len(questions), 1)
    
    def _analyze_length_distribution(self, questions: List[str]) -> Dict[str, int]:
        """Analyze distribution of question lengths"""
        if not questions:
            return {}
        
        short = sum(1 for q in questions if len(q) < 50)
        medium = sum(1 for q in questions if 50 <= len(q) < 150)
        long_q = sum(1 for q in questions if len(q) >= 150)
        
        return {
            "short_questions": short,
            "medium_questions": medium, 
            "long_questions": long_q
        }
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract potential topics from text using simple keyword analysis"""
        # This is a simplified implementation
        # In a real application, you might use NLP libraries like spaCy or NLTK
        common_topics = [
            "algebra", "geometry", "calculus", "statistics",
            "biology", "chemistry", "physics", "environmental science",
            "literature", "grammar", "writing", "reading",
            "history", "geography", "economics", "politics",
            "programming", "algorithms", "databases", "networks"
        ]
        
        found_topics = [topic for topic in common_topics if topic in text]
        return found_topics
    
    def _estimate_reading_level(self, questions: List[str]) -> str:
        """Estimate reading level based on question complexity"""
        if not questions:
            return "Unknown"
        
        avg_length = sum(len(q.split()) for q in questions) / len(questions)
        
        if avg_length < 10:
            return "Elementary"
        elif avg_length < 20:
            return "Middle School"
        elif avg_length < 30:
            return "High School"
        else:
            return "College Level"
    
    def _classify_question_types(self, questions: List[str]) -> List[str]:
        """Classify question types based on text patterns"""
        types = []
        
        for question in questions:
            q_lower = question.lower()
            if any(option in question for option in ["A)", "B)", "C)", "D)"]):
                types.append("multiple_choice")
            elif "true" in q_lower and "false" in q_lower:
                types.append("true_false")
            elif len(question.split()) > 30:
                types.append("essay")
            elif question.endswith("?"):
                types.append("short_answer")
            else:
                types.append("other")
        
        return types
    
    def _estimate_difficulties(self, questions: List[str]) -> List[str]:
        """Estimate question difficulties based on keywords and complexity"""
        difficulties = []
        
        for question in questions:
            q_lower = question.lower()
            word_count = len(question.split())
            
            easy_indicators = sum(1 for word in self.difficulty_keywords["easy"] if word in q_lower)
            hard_indicators = sum(1 for word in self.difficulty_keywords["hard"] if word in q_lower)
            
            if easy_indicators > 0 and word_count < 15:
                difficulties.append("easy")
            elif hard_indicators > 0 or word_count > 40:
                difficulties.append("hard")
            else:
                difficulties.append("medium")
        
        return difficulties