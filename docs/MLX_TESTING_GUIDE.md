# MLX Fine-Tuned Model Testing Guide

## 📍 Finding Your Trained Model

### Model Location
Your MLX model is located at: **`./adapters/`**

**Files:**
- `adapters.safetensors` - Final trained model (22 MB)
- `adapter_config.json` - Model configuration
- `0000100_adapters.safetensors` - Checkpoint at iteration 100
- `0000200_adapters.safetensors` - Checkpoint at iteration 200
- `0000300_adapters.safetensors` - Checkpoint at iteration 300

---

## 🧪 Testing Your Model

### Method 1: Streamlit UI Testing (Recommended)

**Step-by-Step:**

1. **Open your Streamlit app** (should already be running)
   - URL: http://localhost:8504

2. **Navigate to Tab 4: Model Testing** 🧪

3. **Select Comparison Settings:**
   - **Inference Mode:** Choose **"Real (Slower, Actual Models)"**
   - **Comparison Type:** Choose **"3-Way Comparison (All)"**

4. **Pick a Test Transaction** from the dropdown

5. **Wait 10-30 seconds** for real inference to complete

6. **Review Results:**
   - **🤖 Base Model** - Generic (always simulated)
   - **✨ MLX Fine-Tuned** - ✅ Real output from your trained model
   - **🧠 Ollama Expert** - ✅ Real output from Ollama (if running)

**What to Look For:**
- MLX should provide specific fraud indicators
- MLX should give clear BLOCK/REVIEW/APPROVE decisions
- Compare word counts between simulated and real
- Check "📊 Quantitative Comparison" section for metrics

---

### Method 2: Command Line Testing (Quick)

**Test Your Fine-Tuned Model:**

```bash
cd /Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1

mlx_lm.generate \
  --model mlx-community/Llama-3.2-1B-Instruct-4bit \
  --adapter-path ./adapters \
  --prompt "Analyze this fraud case: Transaction Amount: $8500, Fraud Probability: 82%, Account Age: 12 days, Velocity: 15 transactions/24h, Previous Fraud: 1" \
  --max-tokens 150
```

**Compare with Base Model (no fine-tuning):**

```bash
mlx_lm.generate \
  --model mlx-community/Llama-3.2-1B-Instruct-4bit \
  --prompt "Analyze this fraud case: Amount $8500, Fraud Prob 82%, Account Age 12 days" \
  --max-tokens 100
```

**Expected Difference:**
- **Base Model:** Generic response, vague recommendation
- **Fine-Tuned:** Specific red flags, clear action (BLOCK/REVIEW/APPROVE)

---

## 🔍 Verify Training Quality

### Check Model Files
```bash
cd /Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1
ls -lh adapters/
```

**Should show:**
- `adapters.safetensors` (~22 MB)
- 3 checkpoint files
- Config file

### Test Quality Indicators

**Good Signs:**
- ✅ Fine-tuned model mentions specific fraud indicators
- ✅ Uses terminology from your training data
- ✅ Gives clear BLOCK/APPROVE/REVIEW decision
- ✅ Lists specific red flags (previous fraud, velocity, etc.)

**Bad Signs:**
- ❌ Response identical to base model
- ❌ Vague recommendations ("consider reviewing")
- ❌ No specific fraud indicators mentioned

---

## 🚨 Troubleshooting

### Issue: "MLX inference failed"

**Solution 1: Check MLX Installation**
```bash
pip show mlx-lm
```

If not installed:
```bash
pip install mlx-lm
```

**Solution 2: Verify Model Path**
```bash
ls ./adapters/adapters.safetensors
```

Should exist without errors.

### Issue: "Ollama error"

**Solution: Start Ollama**
```bash
ollama serve
```

In another terminal:
```bash
ollama pull llama3.2
```

### Issue: Real inference times out

**Solution: Increase timeout or use smaller test**
- Check that no other heavy processes are running
- Try simpler transaction first
- Verify model is properly loaded

---

## ⚙️ Advanced Testing

### Test Different Checkpoints

You can test earlier checkpoints to see training progression:

```bash
# Test iteration 100
mlx_lm.generate \
  --model mlx-community/Llama-3.2-1B-Instruct-4bit \
  --adapter-path ./adapters/0000100_adapters.safetensors \
  --prompt "Your test prompt" \
  --max-tokens 150
```

**Compare:**
- Iteration 100 vs 200 vs 300 (final)
- Earlier iterations should be less specialized

### Batch Testing

Create a test script to evaluate multiple transactions:

```python
import subprocess

test_cases = [
    "Amount: $500, Prob: 15%, Age: 120 days",
    "Amount: $8500, Prob: 85%, Age: 10 days",
    # Add more...
]

for i, case in enumerate(test_cases):
    print(f"\n=== Test Case {i+1} ===")
    result = subprocess.run([
        'mlx_lm.generate',
        '--model', 'mlx-community/Llama-3.2-1B-Instruct-4bit',
        '--adapter-path', './adapters',
        '--prompt', f"Analyze fraud: {case}",
        '--max-tokens', '100'
    ], capture_output=True, text=True)
    print(result.stdout)
```

---

## 📊 Performance Benchmarks

**Expected Performance:**
- **Inference Speed:** 5-15 seconds per transaction
- **Memory Usage:** ~2-4 GB
- **Model Size:** 22 MB (adapters only, base model cached)

**Comparison:**
- **Simulated Mode:** Instant (0s)
- **Real MLX Mode:** ~10s
- **Real Ollama Mode:** ~20-30s

---

## ✅ Next Steps

1. **Test in UI** - Try Tab 4 with real inference mode
2. **Compare Quality** - Simulated vs Real outputs
3. **Try Different Transactions** - High-risk vs low-risk
4. **Document Findings** - Note improvements from training
5. **Production Testing** - Test on actual new cases

---

## 🆘 Need Help?

**Common Questions:**

**Q: Where is the model saved?**  
A: `./adapters/adapters.safetensors` in your project root

**Q: How do I retrain?**  
A: Go to Tab 3, export dataset, click "Start Training"

**Q: Can I use this in production?**  
A: Yes, but test thoroughly first. Load via `mlx_lm.generate` as shown above.

**Q: How do I improve the model?**  
A: Collect more expert feedback in Tab 1, retrain in Tab 3 with more iterations

---

**Location:** `/Users/yanhuo68/ai-projects/ml/fraud-tab-b7-v1/Docs/MLX_TESTING_GUIDE.md`
