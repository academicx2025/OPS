from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    LONG_ANSWER = "long_answer"
    FILL_IN_BLANK = "fill_in_blank"
    MATCHING = "matching"
    ESSAY = "essay"
    UNKNOWN = "unknown"

class DifficultyLevel(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    UNKNOWN = "unknown"

class QualityScore(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

@dataclass
class QuestionData:
    """Data model for extracted questions"""
    text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    subject_area: Optional[str] = None
    topic: Optional[str] = None
    bloom_taxonomy_level: Optional[str] = None
    estimated_time_minutes: Optional[int] = None

@dataclass
class QuestionQuality:
    """Data model for question quality analysis"""
    overall_score: QualityScore
    clarity_score: float  # 0-10
    difficulty_appropriateness: float  # 0-10
    grammar_correctness: float  # 0-10
    educational_value: float  # 0-10
    feedback: str
    suggestions: List[str]
    issues_identified: List[str]

@dataclass
class MetadataTag:
    """Data model for metadata tags"""
    key: str
    value: str
    category: str
    confidence: Optional[float] = None

@dataclass
class ProcessingMetadata:
    """Data model for file processing metadata"""
    source_filename: str
    file_size_bytes: int
    file_type: str
    processing_timestamp: datetime
    extraction_method: str
    total_questions_found: int
    processing_time_seconds: float
    openai_model_used: str
    quality_check_enabled: bool
    custom_tags: List[MetadataTag]
    
    # Content analysis
    estimated_reading_level: Optional[str] = None
    primary_subject: Optional[str] = None
    topics_covered: List[str] = None
    language_detected: Optional[str] = None
    
    # Question distribution
    question_types_distribution: Dict[str, int] = None
    difficulty_distribution: Dict[str, int] = None
    
    # Quality metrics
    average_quality_score: Optional[float] = None
    questions_needing_improvement: int = 0