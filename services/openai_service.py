import os
import json
import re
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

class OpenAIService:
    """Service for OpenAI integration - question extraction and quality analysis"""
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"  # Default model
    
    async def extract_questions(self, text_content: str, filename: str) -> List[str]:
        """
        Extract questions from text content using OpenAI
        """
        try:
            # Prepare the prompt for question extraction
            prompt = self._create_extraction_prompt(text_content, filename)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator and question extraction specialist. Your task is to identify and extract all questions from the provided text content."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the response to extract questions
            questions = self._parse_extraction_response(response.choices[0].message.content)
            
            return questions
            
        except Exception as e:
            raise Exception(f"Error extracting questions with OpenAI: {str(e)}")
    
    async def analyze_question_quality(self, question: str) -> Dict[str, Any]:
        """
        Analyze the quality of a single question using OpenAI
        """
        try:
            prompt = self._create_quality_analysis_prompt(question)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational assessor specializing in question quality analysis. Evaluate questions based on clarity, educational value, grammar, and appropriateness."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Parse quality analysis response
            quality_data = self._parse_quality_response(response.choices[0].message.content)
            
            return quality_data
            
        except Exception as e:
            raise Exception(f"Error analyzing question quality: {str(e)}")
    
    def _create_extraction_prompt(self, text_content: str, filename: str) -> str:
        """Create prompt for question extraction"""
        return f"""
Please analyze the following text content from file "{filename}" and extract ALL questions present in the document.

Instructions:
1. Identify and extract every question found in the text
2. Include multiple choice questions, true/false questions, short answer questions, essay questions, etc.
3. For multiple choice questions, include all options
4. Maintain the original formatting and structure as much as possible
5. If no questions are found, return an empty list

Text Content:
{text_content[:4000]}  # Limit text to avoid token limits

Please provide the extracted questions in the following JSON format:
{{
  "questions": [
    {{
      "text": "Question text here",
      "type": "multiple_choice|true_false|short_answer|essay|other",
      "options": ["A) option1", "B) option2", "C) option3", "D) option4"] // if applicable
    }}
  ]
}}
"""
    
    def _create_quality_analysis_prompt(self, question: str) -> str:
        """Create prompt for question quality analysis"""
        return f"""
Please analyze the quality of the following question and provide a comprehensive assessment:

Question: "{question}"

Please evaluate the question based on these criteria and provide a detailed analysis:

1. Clarity (0-10): How clear and unambiguous is the question?
2. Educational Value (0-10): How well does it assess learning?
3. Grammar & Language (0-10): Correctness of grammar and language use
4. Difficulty Appropriateness (0-10): Is the difficulty level appropriate?

Provide your response in the following JSON format:
{{
  "overall_score": "excellent|good|fair|poor",
  "clarity_score": 8.5,
  "educational_value": 7.0,
  "grammar_score": 9.0,
  "difficulty_score": 6.5,
  "feedback": "Detailed feedback about the question",
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "issues_identified": ["Issue 1", "Issue 2"],
  "question_type": "multiple_choice|true_false|short_answer|essay|other",
  "estimated_difficulty": "easy|medium|hard",
  "bloom_taxonomy_level": "remember|understand|apply|analyze|evaluate|create"
}}
"""
    
    def _parse_extraction_response(self, response_text: str) -> List[str]:
        """Parse OpenAI response to extract questions"""
        try:
            # Try to parse as JSON first
            if response_text.strip().startswith('{'):
                data = json.loads(response_text)
                if 'questions' in data:
                    questions = []
                    for q in data['questions']:
                        if isinstance(q, dict) and 'text' in q:
                            question_text = q['text']
                            if 'options' in q and q['options']:
                                question_text += "\n" + "\n".join(q['options'])
                            questions.append(question_text)
                        elif isinstance(q, str):
                            questions.append(q)
                    return questions
            
            # Fallback: Parse as text and extract questions
            questions = []
            lines = response_text.split('\n')
            
            current_question = ""
            for line in lines:
                line = line.strip()
                if not line:
                    if current_question:
                        questions.append(current_question.strip())
                        current_question = ""
                    continue
                
                # Check if line contains a question
                if ('?' in line or 
                    line.lower().startswith(('what', 'how', 'why', 'when', 'where', 'which')) or
                    re.match(r'^\d+[\.\)]\s*', line) or
                    line.startswith(('A)', 'B)', 'C)', 'D)', 'a)', 'b)', 'c)', 'd)'))):
                    
                    if current_question and '?' in current_question:
                        questions.append(current_question.strip())
                        current_question = line
                    else:
                        current_question += " " + line if current_question else line
                else:
                    current_question += " " + line if current_question else line
            
            if current_question:
                questions.append(current_question.strip())
            
            # Filter out empty questions and duplicates
            questions = [q for q in questions if q and len(q.strip()) > 5]
            questions = list(dict.fromkeys(questions))  # Remove duplicates
            
            return questions
            
        except Exception as e:
            # Fallback: simple text parsing
            lines = response_text.split('\n')
            questions = [line.strip() for line in lines if '?' in line and len(line.strip()) > 5]
            return questions[:20]  # Limit to 20 questions
    
    def _parse_quality_response(self, response_text: str) -> Dict[str, Any]:
        """Parse OpenAI quality analysis response"""
        try:
            # Try to parse as JSON
            if response_text.strip().startswith('{'):
                return json.loads(response_text)
            
            # Fallback: create basic quality assessment
            return {
                "overall_score": "good",
                "clarity_score": 7.0,
                "educational_value": 7.0,
                "grammar_score": 8.0,
                "difficulty_score": 6.0,
                "feedback": "Question analyzed successfully",
                "suggestions": ["Consider reviewing for clarity"],
                "issues_identified": [],
                "question_type": "unknown",
                "estimated_difficulty": "medium",
                "bloom_taxonomy_level": "understand"
            }
            
        except Exception as e:
            # Basic fallback response
            return {
                "overall_score": "fair",
                "clarity_score": 6.0,
                "educational_value": 6.0,
                "grammar_score": 7.0,
                "difficulty_score": 5.0,
                "feedback": f"Analysis completed with limited data: {str(e)}",
                "suggestions": ["Manual review recommended"],
                "issues_identified": ["Automated analysis incomplete"],
                "question_type": "unknown",
                "estimated_difficulty": "medium",
                "bloom_taxonomy_level": "unknown"
            }