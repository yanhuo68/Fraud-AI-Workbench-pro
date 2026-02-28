# 08. LLM Fine Tuning (Model Forge)

The **LLM Forge** enables organizations to refine generic Large Language Models into specialists that understand the nuance of your specific fraud environment and investigative language.

## 🧬 1. The Adaptation Process

- **Base Models**: Sentinel supports local fine-tuning of Llama (via MLX) and Ollama expert prompts.
- **Training Data**: Convert your historical investigation notes or synthetic fraud scenarios into a structural training set.
- **Adapter Logic**: The system uses **LoRA (Low-Rank Adaptation)** to train specialized "layers" without needing the massive hardware required for full model training.

## 🧠 2. Expert Prompts

If you don't need a full fine-tune, use the **Expert Prompt Workshop**:
1. Define a "persona" (e.g., *Senior AML Investigator*).
2. Provide few-shot examples of correct analysis.
3. Save the result as a **Registered Prompt Version** that can be used across all RAG assistants.

## ⚖️ 3. Evaluation & Testing

Compare your forged model against base versions:
- **Accuracy Check**: Does the new model identify fraud indicators more precisely?
- **Consistency**: Is the tone and format of reports standardized?
- **Speed**: Verify that the specialized model meets your performance requirements for real-time assistance.

> [!IMPORTANT]
> Fine-tuning is a resource-intensive task. Ensure your hardware (or cloud instance) meets the requirements listed in the **Pre-flight Check** on this page.
