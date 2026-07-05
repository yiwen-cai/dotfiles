---
name: testing-quality-assurance
description: Comprehensive testing and quality assurance — API testing, performance benchmarking, reality checking, and test
  results analysis.
user-invocable: true
metadata:
  migrated_from: hermes-agent
  source_skills_count: 0
---

# Testing and Quality Assurance

Comprehensive testing and quality assurance. Covers API testing, performance benchmarking, reality checking, and test results analysis.

## When to Use

- User wants to test APIs or systems
- Need performance benchmarks or load testing
- Want a reality check before production deployment
- Need to analyze test results and generate reports
- Setting up CI/CD quality gates

## Four Testing Dimensions

| Dimension | Focus | Key Metrics |
|-----------|-------|-------------|
| **API Testing** | Functional, security, integration | Coverage, error rates, response times |
| **Performance** | Load, stress, capacity | QPS, latency percentiles, resource usage |
| **Reality Check** | Production readiness | Evidence-based assessment |
| **Test Analysis** | Results interpretation | Trends, predictions, recommendations |

## API Testing

### Coverage Goals
- 95%+ endpoint coverage
- All HTTP methods tested
- Authentication/authorization verified
- Error handling validated
- Rate limiting confirmed

### Security Testing
- OWASP API Security Top 10
- SQL injection prevention
- XSS protection
- Input validation
- Token security

### Sample Test Structure
```javascript
describe('User API', () => {
  describe('Functional', () => {
    test('create user with valid data');
    test('reject invalid input');
    test('handle edge cases');
  });
  
  describe('Security', () => {
    test('reject unauthenticated requests');
    test('prevent SQL injection');
    test('enforce rate limiting');
  });
  
  describe('Performance', () => {
    test('respond within 200ms (P95)');
    test('handle 50 concurrent requests');
  });
});
```

## Performance Benchmarking

### Test Types
- **Baseline**: Current performance snapshot
- **Load**: Gradual increase to find拐点
- **Stress**: Beyond normal capacity
- **Endurance**: Long-running stability

### Key Metrics
| Metric | Target | Tool |
|--------|--------|------|
| P50 latency | < 50ms | k6, Locust |
| P95 latency | < 200ms | k6, Locust |
| P99 latency | < 500ms | k6, Locust |
| Error rate | < 0.1% | k6, Locust |
| Throughput | > 1000 QPS | k6, wrk |

### k6 Script Example
```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 200 },
    { duration: '3m', target: 500 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const resp = http.get('https://api.example.com/users');
  check(resp, { 'status is 200': (r) => r.status === 200 });
}
```

## Reality Checking

### Principles
- **Default to "needs work"** — require overwhelming evidence for "production ready"
- **Evidence-based** — every claim needs proof
- **Honest grading** — C+/B- is normal for first iterations
- **Specific feedback** — actionable, not vague

### Checklist
- [ ] All features implemented per spec
- [ ] Screenshots match claims
- [ ] Performance meets SLA
- [ ] Security scan passed
- [ ] Error handling verified
- [ ] Documentation complete
- [ ] Monitoring configured

### Report Template
```markdown
## Quality Assessment
**Overall Score**: C+ / B- / B / B+
**Production Ready**: FAILED / NEEDS WORK / READY

### Issues Found
1. [Specific issue with evidence]
2. [Specific issue with evidence]

### Required Fixes
1. [Actionable fix]
2. [Actionable fix]

### Timeline
[Realistic estimate for fixes]
```

## Test Results Analysis

### Analysis Framework
1. **Collect** — gather all test results
2. **Validate** — check data quality
3. **Analyze** — statistical analysis, pattern recognition
4. **Predict** — defect-prone areas, release readiness
5. **Report** — actionable insights for different roles

### Key Outputs
- **Coverage analysis** — gaps and priorities
- **Failure patterns** — root cause trends
- **Quality trends** — improving or declining
- **Risk assessment** — probability and impact
- **Recommendations** — prioritized by ROI

### Executive Report
```markdown
## Quality Summary
**Score**: [0-100]
**Trend**: ↑ / → / ↓
**Release**: GO / NO-GO

## Top Risks
1. [Risk + probability + impact]
2. [Risk + probability + impact]

## Recommendations
1. [Action + expected impact]
2. [Action + expected impact]
```

## Common Pitfalls

1. **Testing in isolation** — test the full user journey
2. **Ignoring performance** — test under realistic load
3. **Over-optimism** — be honest about readiness
4. **Missing edge cases** — test boundaries and failures
5. **No baselines** — establish before optimizing
6. **Analysis paralysis** — act on findings quickly

## Snapshot Testing (ML/Model Components)

When debugging snapshot test failures in ML model component tests (e.g., PyTorch forward functions compared via `numpy_snapshot.assert_match`):

- See `references/snapshot-test-debugging.md` for the systematic 5-phase debugging flow
- Key principle: verify the implementation independently first (einsum ↔ @ → torch.einsum), then check fixture/snapshot consistency
- Many tests offer dual-path acceptance: match PyTorch reference OR match snapshot

## Triton Kernel Numerical Tests

For custom Triton kernels, prefer a temporary focused harness before broad suite runs:

- Put the harness outside the student/project source tree (for example `/tmp/...`) when testing coursework or review-only code.
- Compare against an independent PyTorch/autograd reference and print `max_abs`, `mean_abs`, and `allclose` for each output tensor.
- Cover both ordinary and adversarial shapes: single-token, assignment/default shape, `n_q != n_k`, tail tiles on each axis, causal and non-causal paths, and nonstandard tile sizes.
- Treat Triton `tl.dot` tile constraints as test-parameter issues when the failing dimension is below the backend minimum (commonly reduction dimension `< 16`), then rerun with legal tile sizes before declaring a kernel bug.
- When academic-integrity constraints apply, create and run verification scripts but avoid editing or completing the student's implementation.
- See `scripts/triton_kernel_numerical_harness.py` for a copy-and-adapt template.

## Related Skills

- `engineering-code-reviewer` — For code quality
- `engineering-minimal-change-engineer` — For focused fixes
- `systematic-debugging` — For investigating failures
- `github-pr-workflow` — For CI integration