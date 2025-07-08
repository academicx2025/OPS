import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class EnhancedMetadataService:
    """Enhanced service for generating detailed question metadata in the specified format"""
    
    def __init__(self):
        self.boards = ["CBSE", "ICSE", "State Board", "IB", "Cambridge", "Other"]
        self.grades = ["9", "10", "11", "12", "UG", "PG"]
        self.subjects = {
            "Mathematics": {"units": ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry"]},
            "Physics": {"units": ["Mechanics", "Thermodynamics", "Optics", "Electricity", "Modern Physics"]},
            "Chemistry": {"units": ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry"]},
            "Biology": {"units": ["Cell Biology", "Genetics", "Ecology", "Human Physiology", "Plant Biology"]},
            "English": {"units": ["Grammar", "Literature", "Comprehension", "Writing", "Vocabulary"]},
            "General": {"units": ["General Knowledge", "Mixed Topics"]}
        }
        
        self.difficulty_levels = ["Easy", "Medium", "Hard"]
        self.blooms_taxonomy = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        self.question_types = ["MCQ", "Fill in the Blank", "Short Answer", "Long Answer", "True/False", "Match the Following"]
        self.exam_types = ["JEE", "NEET", "KCET", "CBSE Board", "State Board", "Competitive", "Other"]
    
    def generate_enhanced_metadata(self, questions_data: List[Dict], 
                                 filename: str, output_folder: str) -> Dict[str, Any]:
        """
        Generate enhanced metadata for questions in the specified format
        """
        processed_questions = []
        image_folder = os.path.join(output_folder, "question_images")
        
        # Create image folder if it doesn't exist
        os.makedirs(image_folder, exist_ok=True)
        
        for i, question_data in enumerate(questions_data):
            question_id = f"Q{str(i+1).zfill(4)}"
            
            # Extract question text and analyze it
            question_text = question_data.get("text", "")
            quality_data = question_data.get("quality", {})
            
            # Generate comprehensive metadata
            metadata = self._generate_question_metadata(
                question_id=question_id,
                question_text=question_text,
                quality_data=quality_data,
                filename=filename
            )
            
            # Handle images if present
            if self._has_image_content(question_text):
                image_path = self._extract_and_save_image(
                    question_text, question_id, image_folder
                )
                metadata["Graph/Diagram"] = f"Yes - {question_id}.png"
            else:
                metadata["Graph/Diagram"] = "No"
            
            processed_questions.append(metadata)
        
        # Create downloadable JSON file
        json_output = {
            "metadata": {
                "source_file": filename,
                "processed_at": datetime.now().isoformat(),
                "total_questions": len(processed_questions),
                "output_folder": output_folder,
                "image_folder": image_folder if os.path.exists(image_folder) else None
            },
            "questions": processed_questions
        }
        
        # Save JSON file
        json_filename = f"questions_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = os.path.join(output_folder, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, indent=2, ensure_ascii=False)
        
        return {
            "json_file": json_path,
            "questions_processed": len(processed_questions),
            "images_extracted": len([q for q in processed_questions if q["Graph/Diagram"] != "No"]),
            "output_summary": json_output
        }
    
    def _generate_question_metadata(self, question_id: str, question_text: str, 
                                  quality_data: Dict, filename: str) -> Dict[str, Any]:
        """
        Generate comprehensive metadata for a single question
        """
        # Analyze question content
        subject_analysis = self._analyze_subject(question_text)
        difficulty_analysis = self._analyze_difficulty(question_text, quality_data)
        question_type = self._determine_question_type(question_text)
        blooms_level = self._determine_blooms_taxonomy(question_text, quality_data)
        
        # Extract options if MCQ
        options = self._extract_options(question_text)
        
        metadata = {
            # Basic Information
            "Board": self._determine_board(filename),
            "Grade": self._determine_grade(question_text, subject_analysis),
            "Question ID": question_id,
            "Question": self._clean_question_text(question_text),
            
            # Multiple Choice Options
            "Option A": options.get("A", ""),
            "Option B": options.get("B", ""),
            "Option C": options.get("C", ""),
            "Option D": options.get("D", ""),
            "Answer Key": self._determine_answer_key(question_text, options),
            
            # Subject Classification
            "Subject": subject_analysis["subject"],
            "Unit": subject_analysis["unit"],
            "Chapter": subject_analysis["chapter"],
            "Topic": subject_analysis["topic"],
            "Sub-topic": subject_analysis["sub_topic"],
            "Concept": subject_analysis["concept"],
            
            # Difficulty and Classification
            "Difficulty Level": difficulty_analysis["level"],
            "Bloom's Taxonomy": blooms_level,
            "Question Type": question_type,
            
            # Time and Scoring
            "Time Allocation": self._estimate_time_allocation(question_text, question_type),
            "Marks": self._estimate_marks(question_text, question_type, difficulty_analysis["level"]),
            
            # Requirements
            "Formula Required": self._check_formula_required(question_text),
            "Prerequisites": self._identify_prerequisites(question_text, subject_analysis),
            "Solution Steps": self._estimate_solution_steps(question_text, question_type),
            "Calculation Required": self._check_calculation_required(question_text),
            
            # Exam Relevance
            "Most Relevant Exam": self._determine_most_relevant_exam(subject_analysis, difficulty_analysis),
            "Next Relevant Exam": self._determine_next_relevant_exam(subject_analysis),
            "Exam Frequency (JEE)": self._estimate_exam_frequency(subject_analysis, "JEE"),
            "Exam Frequency (NEET)": self._estimate_exam_frequency(subject_analysis, "NEET"),
            "Exam Frequency (KCET)": self._estimate_exam_frequency(subject_analysis, "KCET"),
            "Frequency Status": self._determine_frequency_status(subject_analysis),
            "Trend": self._analyze_trend(subject_analysis, difficulty_analysis)
        }
        
        return metadata
    
    def _analyze_subject(self, question_text: str) -> Dict[str, str]:
        """Analyze and determine subject-related information"""
        text_lower = question_text.lower()
        
        # Subject keywords mapping
        subject_keywords = {
            "Mathematics": ["equation", "solve", "calculate", "formula", "algebra", "geometry", "calculus", "integral", "derivative"],
            "Physics": ["force", "velocity", "acceleration", "energy", "momentum", "wave", "electric", "magnetic", "quantum"],
            "Chemistry": ["molecule", "atom", "reaction", "compound", "element", "bond", "acid", "base", "organic"],
            "Biology": ["cell", "organism", "evolution", "dna", "protein", "enzyme", "gene", "species", "ecosystem"],
            "English": ["grammar", "literature", "author", "poem", "story", "sentence", "paragraph", "essay"]
        }
        
        # Determine subject
        subject_scores = {}
        for subject, keywords in subject_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                subject_scores[subject] = score
        
        subject = max(subject_scores, key=subject_scores.get) if subject_scores else "General"
        
        # Determine unit, chapter, topic based on subject
        unit_data = self.subjects.get(subject, self.subjects["General"])
        unit = self._determine_unit(text_lower, unit_data["units"])
        
        return {
            "subject": subject,
            "unit": unit,
            "chapter": self._determine_chapter(text_lower, subject, unit),
            "topic": self._determine_topic(text_lower, subject),
            "sub_topic": self._determine_sub_topic(text_lower, subject),
            "concept": self._determine_concept(text_lower, subject)
        }
    
    def _analyze_difficulty(self, question_text: str, quality_data: Dict) -> Dict[str, Any]:
        """Analyze difficulty level of the question"""
        text_lower = question_text.lower()
        
        # Use quality data if available
        if quality_data and "estimated_difficulty" in quality_data:
            openai_difficulty = quality_data["estimated_difficulty"]
            if openai_difficulty in ["easy", "medium", "hard"]:
                return {"level": openai_difficulty.title(), "confidence": 0.8}
        
        # Fallback analysis
        easy_indicators = ["basic", "simple", "identify", "list", "define"]
        hard_indicators = ["analyze", "evaluate", "synthesize", "compare", "critique"]
        
        easy_count = sum(1 for word in easy_indicators if word in text_lower)
        hard_count = sum(1 for word in hard_indicators if word in text_lower)
        
        word_count = len(question_text.split())
        
        if easy_count > 0 and word_count < 20:
            return {"level": "Easy", "confidence": 0.6}
        elif hard_count > 0 or word_count > 50:
            return {"level": "Hard", "confidence": 0.7}
        else:
            return {"level": "Medium", "confidence": 0.5}
    
    def _determine_question_type(self, question_text: str) -> str:
        """Determine the type of question"""
        text = question_text.upper()
        
        if any(option in text for option in ["A)", "B)", "C)", "D)", "(A)", "(B)", "(C)", "(D)"]):
            return "MCQ"
        elif "TRUE" in text and "FALSE" in text:
            return "True/False"
        elif "______" in text or "___" in text or "fill" in question_text.lower():
            return "Fill in the Blank"
        elif "match" in question_text.lower() and ("following" in question_text.lower() or "column" in question_text.lower()):
            return "Match the Following"
        elif len(question_text.split()) > 30:
            return "Long Answer"
        else:
            return "Short Answer"
    
    def _determine_blooms_taxonomy(self, question_text: str, quality_data: Dict) -> str:
        """Determine Bloom's taxonomy level"""
        if quality_data and "bloom_taxonomy_level" in quality_data:
            bloom_level = quality_data["bloom_taxonomy_level"]
            if bloom_level in [level.lower() for level in self.blooms_taxonomy]:
                return bloom_level.title()
        
        text_lower = question_text.lower()
        
        # Keyword mapping for Bloom's taxonomy
        bloom_keywords = {
            "Remember": ["recall", "identify", "list", "name", "state", "define"],
            "Understand": ["explain", "describe", "interpret", "summarize", "classify"],
            "Apply": ["solve", "calculate", "demonstrate", "use", "apply", "implement"],
            "Analyze": ["analyze", "compare", "contrast", "examine", "investigate"],
            "Evaluate": ["evaluate", "assess", "judge", "critique", "justify"],
            "Create": ["create", "design", "synthesize", "compose", "formulate"]
        }
        
        for level, keywords in bloom_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level
        
        return "Understand"  # Default
    
    def _extract_options(self, question_text: str) -> Dict[str, str]:
        """Extract multiple choice options"""
        options = {"A": "", "B": "", "C": "", "D": ""}
        
        # Pattern matching for options
        import re
        patterns = [
            r'[Aa]\)\s*([^B\n]+)',
            r'[Bb]\)\s*([^C\n]+)', 
            r'[Cc]\)\s*([^D\n]+)',
            r'[Dd]\)\s*([^\n]+)'
        ]
        
        option_keys = ["A", "B", "C", "D"]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, question_text)
            if match:
                options[option_keys[i]] = match.group(1).strip()
        
        return options
    
    def _determine_answer_key(self, question_text: str, options: Dict) -> str:
        """Attempt to determine the answer key"""
        # This is a simplified implementation
        # In practice, you might use OpenAI to help identify the correct answer
        text_lower = question_text.lower()
        
        if "answer" in text_lower and any(opt in text_lower for opt in ["a)", "b)", "c)", "d)"]):
            # Try to find explicit answer mentions
            import re
            answer_pattern = r'answer[:\s]*([abcd])'
            match = re.search(answer_pattern, text_lower)
            if match:
                return match.group(1).upper()
        
        return ""  # Return empty if cannot determine
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean and format question text"""
        # Remove options from question text for cleaner display
        import re
        
        # Remove option patterns
        patterns = [
            r'[Aa]\)\s*[^\n]+',
            r'[Bb]\)\s*[^\n]+',
            r'[Cc]\)\s*[^\n]+', 
            r'[Dd]\)\s*[^\n]+'
        ]
        
        cleaned = question_text
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _has_image_content(self, question_text: str) -> bool:
        """Check if question likely contains image content"""
        image_indicators = [
            "figure", "diagram", "graph", "chart", "image", "picture",
            "shown above", "shown below", "given figure", "following diagram"
        ]
        
        text_lower = question_text.lower()
        return any(indicator in text_lower for indicator in image_indicators)
    
    def _extract_and_save_image(self, question_text: str, question_id: str, image_folder: str) -> str:
        """Extract and save image (placeholder implementation)"""
        # This is a placeholder - in practice, you would extract actual images
        # from the source document and save them with the question ID
        
        image_filename = f"{question_id}.png"
        image_path = os.path.join(image_folder, image_filename)
        
        # Create a placeholder file to indicate image should be here
        with open(image_path.replace('.png', '_placeholder.txt'), 'w') as f:
            f.write(f"Image placeholder for question {question_id}\n")
            f.write("Original image should be extracted and saved here.\n")
        
        return image_path
    
    # Additional helper methods for detailed analysis
    def _determine_board(self, filename: str) -> str:
        """Determine educational board from filename or content"""
        filename_lower = filename.lower()
        
        if "cbse" in filename_lower:
            return "CBSE"
        elif "icse" in filename_lower:
            return "ICSE"
        elif "state" in filename_lower:
            return "State Board"
        else:
            return "CBSE"  # Default
    
    def _determine_grade(self, question_text: str, subject_analysis: Dict) -> str:
        """Determine grade level"""
        text_lower = question_text.lower()
        
        # Grade indicators in text
        if any(word in text_lower for word in ["basic", "introduction", "fundamental"]):
            return "10"
        elif any(word in text_lower for word in ["advanced", "complex", "detailed"]):
            return "12"
        else:
            return "11"  # Default
    
    def _determine_unit(self, text_lower: str, available_units: List[str]) -> str:
        """Determine unit within subject"""
        for unit in available_units:
            if unit.lower() in text_lower:
                return unit
        return available_units[0] if available_units else "General"
    
    def _determine_chapter(self, text_lower: str, subject: str, unit: str) -> str:
        """Determine chapter (simplified implementation)"""
        # This would be enhanced with more sophisticated content analysis
        return f"{unit} - Chapter 1"
    
    def _determine_topic(self, text_lower: str, subject: str) -> str:
        """Determine topic within chapter"""
        # Simplified topic determination
        if "equation" in text_lower:
            return "Equations and Solutions"
        elif "function" in text_lower:
            return "Functions"
        else:
            return "General Concepts"
    
    def _determine_sub_topic(self, text_lower: str, subject: str) -> str:
        """Determine sub-topic"""
        return "Basic Concepts"  # Simplified
    
    def _determine_concept(self, text_lower: str, subject: str) -> str:
        """Determine core concept"""
        return "Fundamental Understanding"  # Simplified
    
    def _estimate_time_allocation(self, question_text: str, question_type: str) -> str:
        """Estimate time allocation for the question"""
        word_count = len(question_text.split())
        
        if question_type == "MCQ":
            return "2 minutes"
        elif question_type in ["True/False", "Fill in the Blank"]:
            return "1 minute" 
        elif question_type == "Short Answer":
            return "5 minutes"
        elif question_type == "Long Answer":
            return "10 minutes"
        else:
            return "3 minutes"
    
    def _estimate_marks(self, question_text: str, question_type: str, difficulty: str) -> str:
        """Estimate marks for the question"""
        base_marks = {
            "MCQ": 1,
            "True/False": 1,
            "Fill in the Blank": 1,
            "Short Answer": 3,
            "Long Answer": 5,
            "Match the Following": 2
        }
        
        marks = base_marks.get(question_type, 2)
        
        if difficulty == "Hard":
            marks += 1
        elif difficulty == "Easy":
            marks = max(1, marks - 1)
        
        return str(marks)
    
    def _check_formula_required(self, question_text: str) -> str:
        """Check if formula is required"""
        formula_indicators = ["formula", "equation", "calculate", "solve", "compute"]
        text_lower = question_text.lower()
        
        return "Yes" if any(indicator in text_lower for indicator in formula_indicators) else "No"
    
    def _identify_prerequisites(self, question_text: str, subject_analysis: Dict) -> str:
        """Identify prerequisites for the question"""
        subject = subject_analysis["subject"]
        
        prerequisites_map = {
            "Mathematics": "Basic algebra and arithmetic",
            "Physics": "Mathematics fundamentals, basic physics concepts",
            "Chemistry": "Basic chemistry concepts, periodic table knowledge",
            "Biology": "Basic biological concepts",
            "English": "Basic grammar and vocabulary"
        }
        
        return prerequisites_map.get(subject, "General knowledge")
    
    def _estimate_solution_steps(self, question_text: str, question_type: str) -> str:
        """Estimate number of solution steps"""
        if question_type in ["MCQ", "True/False"]:
            return "1-2"
        elif question_type in ["Fill in the Blank", "Short Answer"]:
            return "2-3"
        else:
            return "3-5"
    
    def _check_calculation_required(self, question_text: str) -> str:
        """Check if calculations are required"""
        calculation_indicators = ["calculate", "compute", "solve", "find", "determine"]
        text_lower = question_text.lower()
        
        return "Yes" if any(indicator in text_lower for indicator in calculation_indicators) else "No"
    
    def _determine_most_relevant_exam(self, subject_analysis: Dict, difficulty_analysis: Dict) -> str:
        """Determine most relevant exam"""
        subject = subject_analysis["subject"]
        
        if subject in ["Physics", "Chemistry", "Mathematics"]:
            return "JEE"
        elif subject == "Biology":
            return "NEET"
        else:
            return "CBSE Board"
    
    def _determine_next_relevant_exam(self, subject_analysis: Dict) -> str:
        """Determine next relevant exam"""
        subject = subject_analysis["subject"]
        
        if subject in ["Physics", "Chemistry", "Mathematics"]:
            return "KCET"
        elif subject == "Biology":
            return "State Board"
        else:
            return "Competitive Exams"
    
    def _estimate_exam_frequency(self, subject_analysis: Dict, exam_type: str) -> str:
        """Estimate frequency of similar questions in specific exams"""
        subject = subject_analysis["subject"]
        
        frequency_map = {
            "JEE": {
                "Mathematics": "High",
                "Physics": "High", 
                "Chemistry": "High",
                "Biology": "Low"
            },
            "NEET": {
                "Biology": "High",
                "Chemistry": "Medium",
                "Physics": "Medium",
                "Mathematics": "Low"
            },
            "KCET": {
                "Mathematics": "High",
                "Physics": "High",
                "Chemistry": "High",
                "Biology": "Medium"
            }
        }
        
        return frequency_map.get(exam_type, {}).get(subject, "Medium")
    
    def _determine_frequency_status(self, subject_analysis: Dict) -> str:
        """Determine overall frequency status"""
        return "Regular"  # Simplified implementation
    
    def _analyze_trend(self, subject_analysis: Dict, difficulty_analysis: Dict) -> str:
        """Analyze question trend"""
        subject = subject_analysis["subject"]
        difficulty = difficulty_analysis["level"]
        
        if difficulty == "Hard":
            return "Increasing complexity"
        elif subject in ["Mathematics", "Physics"]:
            return "Application-focused"
        else:
            return "Concept-based"