# KV Cache Quantization: Asymmetric (KIVI/KVQuant) Defense Notes

Use this reference when the user asks about "asymmetric quantization" in KIVI, KVQuant, or similar KV-cache quantization methods during presentation/research prep.

## Core distinction (what "asymmetric" means here)

In KIVI/KVQuant, **"asymmetric" does NOT mean "has a zero-point"** (although the quantizer does use zero-point). It means **Key and Value caches use different quantization dimensions**:

| Tensor | Quantization dimension | Why |
|--------|------------------------|-----|
| Key cache | **per-channel** | Key has fixed outlier channels; per-channel confines error to each channel without impacting normal channels |
| Value cache | **per-token** | Value has no channel-wise outlier pattern; attention output is a weighted sum of few important tokens, so per-token confines error to unimportant tokens |

## Primary source evidence (KIVI paper)

- **Figure 2**: Key cache shows "a few fixed channels whose magnitudes are very large"; Value cache "does not show the channel-wise outlier pattern."
- **Table 1**: `2bit (K per-channel, V per-token)` achieves 63.53 CoQA vs 2.88 for `2bit (K per-channel, V per-channel)` and 52.93 for `2bit (K per-token, V per-token)`.
- **Table 2**: Key per-channel reduces attention score error from 47.00 to 9.60; Value per-token reduces output error from 49.89 to 3.55.
- **Section 3.2**: "The per-token quantization can confine the error to each individual token. Thus, quantizing other tokens does not affect the accuracy of important tokens."

## Defense wording

> KIVI/KVQuant's "asymmetric quantization" refers to the fact that Key and Value caches are quantized along different dimensions. Key cache is quantized per-channel because it exhibits fixed outlier channels; per-channel quantization confines the error to each individual channel. Value cache is quantized per-token because it has no channel-wise outlier pattern, and attention output is a sparse weighted sum of value tokens; per-token quantization confines error to unimportant tokens without affecting the few tokens that actually contribute to the output. This is why symmetrically using per-channel for both or per-token for both causes severe accuracy degradation at 2-bit.

## Pitfalls

- Do not answer with "asymmetric means it has a zero-point." That is the generic definition, not the domain-specific meaning in KIVI/KVQuant.
- Do not claim KIVI and KVQuant are identical. KVQuant adds per-channel Key quantization + pre-RoPE quantization + non-uniform datatypes + dense-and-sparse outlier isolation; KIVI adds the residual/sliding-window full-precision buffer for recent tokens.
- Do not present the 2.6× memory reduction or 4× batch size as universal; they are model- and workload-dependent.
