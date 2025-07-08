# Question Paper Generator - AI-Powered Question Extraction

A comprehensive web application that uses OpenAI's GPT models to extract questions from various file formats (PDF, Word, Excel, Images) and provides detailed metadata analysis with image extraction capabilities.

## 🌟 Features

- **Multi-Format Support**: Extract questions from PDF, DOCX, XLSX, JPG, PNG, TIFF files
- **AI-Powered Question Extraction**: Uses OpenAI GPT for intelligent question identification
- **Quality Analysis**: Comprehensive question quality assessment using AI
- **Detailed Metadata**: Generates extensive metadata in the specified format including:
  - Board, Grade, Question ID, Subject classification
  - Difficulty Level, Bloom's Taxonomy, Question Type
  - Time Allocation, Marks, Prerequisites
  - Exam relevance (JEE, NEET, KCET) and frequency analysis
- **Image Extraction**: Automatically extracts and saves images with QuestionID.png naming
- **Beautiful UI**: Modern, responsive web interface with drag-and-drop file upload
- **Structured Output**: Generates downloadable JSON files with organized metadata

## 📋 Metadata Format

The application generates metadata in the following comprehensive format:

| Field | Description |
|-------|-------------|
| Board | Educational Board (CBSE, ICSE, State Board, etc.) |
| Grade | Grade Level (9, 10, 11, 12, UG, PG) |
| Question ID | Unique Question Identifier (Q0001, Q0002, etc.) |
| Question | Clean question text (without options) |
| Option A/B/C/D | Multiple choice options |
| Answer Key | Correct answer (if determinable) |
| Subject | Subject classification |
| Unit | Subject unit/module |
| Chapter | Chapter within unit |
| Topic | Specific topic |
| Sub-topic | Detailed sub-topic |
| Concept | Core concept being tested |
| Difficulty Level | Easy, Medium, Hard |
| Bloom's Taxonomy | Remember, Understand, Apply, Analyze, Evaluate, Create |
| Question Type | MCQ, Short Answer, Long Answer, True/False, etc. |
| Time Allocation | Estimated time to solve |
| Marks | Suggested marks for the question |
| Formula Required | Whether mathematical formulas are needed |
| Prerequisites | Required prior knowledge |
| Solution Steps | Estimated number of solution steps |
| Calculation Required | Whether calculations are involved |
| Graph/Diagram | Image presence indicator with filename |
| Most Relevant Exam | Primary exam type (JEE, NEET, KCET, etc.) |
| Next Relevant Exam | Secondary exam relevance |
| Exam Frequency (JEE/NEET/KCET) | Frequency of similar questions |
| Frequency Status | Overall frequency assessment |
| Trend | Question trend analysis |

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Tesseract OCR (for image processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd question-paper-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract OCR**
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
   - **macOS**: `brew install tesseract`
   - **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the web interface**
   - Open your browser to `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
PORT=8000
HOST=0.0.0.0
```

### API Key Setup

1. Get your OpenAI API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file
3. Ensure you have sufficient credits in your OpenAI account

## 📖 Usage

### Web Interface

1. **Upload File**: Drag and drop or click to browse and select your document
2. **Set Output Folder**: Specify where to save the extracted data
3. **Configure Options**:
   - Enable/disable AI quality analysis
   - Enable/disable image extraction
   - Add custom metadata tags
4. **Process**: Click "Process Document" to start extraction
5. **Download Results**: Download the generated JSON file and extracted images

### API Usage

You can also use the API directly:

```bash
curl -X POST "http://localhost:8000/api/process-file" \
     -F "file=@your_document.pdf" \
     -F "output_folder=/path/to/output" \
     -F "include_quality_check=true" \
     -F "extract_images=true" \
     -F "metadata_tags=[]"
```

### Supported File Types

- **PDF**: `.pdf`
- **Word Documents**: `.docx`, `.doc`
- **Excel Spreadsheets**: `.xlsx`, `.xls`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`, `.bmp`

## 📁 Output Structure

```
output_folder/
├── questions_metadata_YYYYMMDD_HHMMSS.json    # Main metadata file
├── question_images/                            # Extracted images folder
│   ├── Q0001.png                              # Question images named by ID
│   ├── Q0002.png
│   └── image_manifest.json                    # Image mapping file
└── image_manifest.json                        # Image details
```

## 🔍 Sample Output

```json
{
  "metadata": {
    "source_file": "sample_questions.pdf",
    "processed_at": "2024-01-15T10:30:00.000Z",
    "total_questions": 25,
    "output_folder": "/output/path"
  },
  "questions": [
    {
      "Board": "CBSE",
      "Grade": "12",
      "Question ID": "Q0001",
      "Question": "What is the derivative of x²?",
      "Option A": "2x",
      "Option B": "x²",
      "Option C": "2",
      "Option D": "x",
      "Answer Key": "A",
      "Subject": "Mathematics",
      "Unit": "Calculus",
      "Chapter": "Derivatives",
      "Topic": "Basic Differentiation",
      "Sub-topic": "Power Rule",
      "Concept": "Derivative of polynomial functions",
      "Difficulty Level": "Easy",
      "Bloom's Taxonomy": "Apply",
      "Question Type": "MCQ",
      "Time Allocation": "2 minutes",
      "Marks": "1",
      "Formula Required": "Yes",
      "Prerequisites": "Basic algebra and arithmetic",
      "Solution Steps": "1-2",
      "Calculation Required": "Yes",
      "Graph/Diagram": "No",
      "Most Relevant Exam": "JEE",
      "Next Relevant Exam": "KCET",
      "Exam Frequency (JEE)": "High",
      "Exam Frequency (NEET)": "Low",
      "Exam Frequency (KCET)": "High",
      "Frequency Status": "Regular",
      "Trend": "Application-focused"
    }
  ]
}
```

## 🛠️ API Endpoints

- `GET /` - Web interface
- `POST /api/process-file` - Process uploaded file
- `POST /api/analyze-quality` - Analyze single question quality
- `GET /api/supported-formats` - Get supported file formats

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure you have access to GPT-3.5-turbo

2. **Tesseract OCR Issues**
   - Ensure Tesseract is installed and in PATH
   - For Windows, you may need to set the tesseract path manually

3. **File Upload Issues**
   - Check file size limits
   - Verify file format is supported
   - Ensure output folder path is writable

4. **Image Extraction Issues**
   - PyMuPDF dependency for PDF image extraction
   - Install with: `pip install PyMuPDF`

### Getting Help

- Check the GitHub issues for common problems
- Create a new issue with detailed error descriptions
- Include sample files (without sensitive content) when reporting bugs

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Made with ❤️ for educators and assessment professionals**
