# 05. Multimodal RAG Assistant

The **Multimodal Lab** allows investigators to incorporate non-text evidence—such as surveillance footage, audio recordings, and scanned documents—directly into the AI reasoning process.

## 🎥 1. Evidence Types

- **Images**: Scan and analyze receipts, ID cards, or screenshots of suspicious activity.
- **Video**: Provide security footage or screen recordings for AI summarization and anomaly detection.
- **Audio**: Upload call center recordings or voice memos to transcribe and analyze tone/content for fraud indicators.

## 🧠 2. Vision-Language Modeling

The system uses advanced multimodal LLMs (like GPT-4o) to "see" and "hear" the evidence. 
1. **Analyze**: AI identifies key objects, people, or text within the media.
2. **Contextualize**: The system links the physical evidence back to the digital transaction logs.
3. **Reason**: Ask questions like:
   - *"Is the person in this photo the same as the account holder?"*
   - *"Does this receipt amount match the transaction record?"*

## 🎬 3. Media Controls

- **Playback**: Integrated video and audio players allow you to review the evidence alongside the AI's analysis.
- **Snapshots**: Use the image analysis tool to perform OCR (Optical Character Recognition) on scanned documents.

> [!IMPORTANT]
> Large video files may take longer to process. Ensure you have a stable connection and the backend state is ready.
