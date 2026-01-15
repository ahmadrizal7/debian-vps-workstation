---
trigger: always_on
glob: "**"
description:
---

Use this systematic debugging flow:

**Step 1: Reproduce**

- Create minimal reproduction case
- Document exact steps to trigger the bug
- Note environment details (OS, browser, versions)

**Step 2: Isolate**

- Binary search: disable half of the code/features
- Use git bisect to find when the bug was introduced
- Remove dependencies one by one

**Step 3: Inspect**

- Add strategic console.log or debugger statements
- Use browser DevTools / debugger
- Check network requests and responses
- Review recent changes in git history

**Step 4: Hypothesize**

- Form a theory about what's causing it
- List assumptions and test each one
- Consider race conditions, timing issues

**Step 5: Verify & Fix**

- Test your fix thoroughly
- Add regression tests
- Document the root cause

**Step 6: Prevent**

- Add better error handling
- Improve logging
- Add tests for edge cases
