---
name: creating-skills
description: Guide for creating effective skills. Use when users say "create a skill", "new skill", "build a skill", "update skill", or want to extend Claude's capabilities with specialized knowledge, workflows, or tool integrations.
---

# Creating Skills

Guide for creating effective skills. For detailed best practices, see
[references/best-practices.md](references/best-practices.md).

## Quick Reference

### Skill Structure

```txt
skill-name/
├── SKILL.md              # Required: YAML frontmatter + instructions
├── scripts/              # Optional: Executable code (Python/Bash)
├── references/           # Optional: Documentation loaded as needed
└── assets/               # Optional: Templates, images, fonts for output
```

### YAML Frontmatter

**name**: Max 64 chars, lowercase/numbers/hyphens only, gerund form preferred
(`processing-pdfs`, not `helper`)

**description**: Max 1024 chars, third person, include what AND when to use

### Key Principles

- **Concise is key**: Only add context Claude doesn't already have
- **Avoid duplication**: Information lives in SKILL.md OR references, not both
- **Keep SKILL.md under 500 lines**: Move details to references/
- **References one level deep**: Avoid nested file references

## Skill Creation Process

### Step 1: Understanding the Skill with Concrete Examples

Skip this step only when the skill's usage patterns are already clearly understood. It remains valuable even when working with an existing skill.

To create an effective skill, clearly understand concrete examples of how the skill will be used. This understanding can come from either direct user examples or generated examples that are validated with user feedback.

For example, when building an image-editor skill, relevant questions include:

- "What functionality should the image-editor skill support? Editing, rotating, anything else?"
- "Can you give some examples of how this skill would be used?"
- "I can imagine users asking for things like 'Remove the red-eye from this image' or 'Rotate this image'. Are there other ways you imagine this skill being used?"
- "What would a user say that should trigger this skill?"

To avoid overwhelming users, avoid asking too many questions in a single message. Start with the most important questions and follow up as needed for better effectiveness.

Conclude this step when there is a clear sense of the functionality the skill should support.

### Step 2: Planning the Reusable Skill Contents

To turn concrete examples into an effective skill, analyze each example by:

1. Considering how to execute on the example from scratch
2. Identifying what scripts, references, and assets would be helpful when executing these workflows repeatedly

Example: When building a `pdf-editor` skill to handle queries like "Help me rotate this PDF," the analysis shows:

1. Rotating a PDF requires re-writing the same code each time
2. A `scripts/rotate_pdf.py` script would be helpful to store in the skill

Example: When designing a `frontend-webapp-builder` skill for queries like "Build me a todo app" or "Build me a dashboard to track my steps," the analysis shows:

1. Writing a frontend webapp requires the same boilerplate HTML/React each time
2. An `assets/hello-world/` template containing the boilerplate HTML/React project files would be helpful to store in the skill

Example: When building a `big-query` skill to handle queries like "How many users have logged in today?" the analysis shows:

1. Querying BigQuery requires re-discovering the table schemas and relationships each time
2. A `references/schema.md` file documenting the table schemas would be helpful to store in the skill

To establish the skill's contents, analyze each concrete example to create a list of the reusable resources to include: scripts, references, and assets.

### Step 3: Initializing the Skill

At this point, it is time to actually create the skill.

Skip this step only if the skill being developed already exists, and iteration or packaging is needed. In this case, continue to the next step.

When creating a new skill from scratch, always run the `init_skill.py` script. The script conveniently generates a new template skill directory that automatically includes everything a skill requires, making the skill creation process much more efficient and reliable.

Usage:

```bash
scripts/init_skill.py <skill-name> --path <output-directory>
```

The script:

- Creates the skill directory at the specified path
- Generates a SKILL.md template with proper frontmatter and TODO placeholders
- Creates example resource directories: `scripts/`, `references/`, and `assets/`
- Adds example files in each directory that can be customized or deleted

After initialization, customize or remove the generated SKILL.md and example files as needed.

### Step 4: Edit the Skill

When editing the (newly-generated or existing) skill, remember that the skill is being created for another instance of Claude to use. Focus on including information that would be beneficial and non-obvious to Claude. Consider what procedural knowledge, domain-specific details, or reusable assets would help another Claude instance execute these tasks more effectively.

#### Start with Reusable Skill Contents

To begin implementation, start with the reusable resources identified above: `scripts/`, `references/`, and `assets/` files. Note that this step may require user input. For example, when implementing a `brand-guidelines` skill, the user may need to provide brand assets or templates to store in `assets/`, or documentation to store in `references/`.

Also, delete any example files and directories not needed for the skill. The initialization script creates example files in `scripts/`, `references/`, and `assets/` to demonstrate structure, but most skills won't need all of them.

#### Update SKILL.md

To complete SKILL.md, address:

1. What is the purpose of the skill, in a few sentences?
2. When should the skill be used?
3. How should Claude use the skill? Reference all bundled resources.

For content guidelines, common patterns, and anti-patterns, see
[references/best-practices.md](references/best-practices.md).

### Step 5: Validate the Skill

Once the skill is ready, validate it to ensure it meets all requirements:

```bash
scripts/quick_validate.py <path/to/skill-folder>
```

The validation checks:

- YAML frontmatter format and required fields
- Skill naming conventions and directory structure
- Description completeness and quality
- File organization and resource references

If validation fails, fix the reported errors and run the command again.

### Step 6: Lint the Skill

Run the markdown linter to auto-fix and verify SKILL.md and any other markdown files in the skill:

```bash
mise run fix-md
mise run check-md
```

If errors remain after auto-fix, manually correct them until `check-md` passes with zero errors.

### Step 7: Evaluate and Iterate

**Build evaluations first**: Create evaluations BEFORE writing extensive documentation. This
ensures the skill solves real problems rather than documenting imagined ones.

**Evaluation-driven development:**

1. **Identify gaps**: Run Claude on representative tasks without the skill. Document failures.
2. **Create evaluations**: Build 3+ scenarios that test these gaps.
3. **Establish baseline**: Measure Claude's performance without the skill.
4. **Write minimal instructions**: Create just enough content to pass evaluations.
5. **Iterate**: Execute evaluations, compare against baseline, refine.

**Iterative development with Claude:**

Work with one Claude instance ("Claude A") to create the skill, test with another ("Claude B"):

1. Complete a task without a skill, noting what context was repeatedly provided
2. Ask Claude A to create a skill capturing the reusable pattern
3. Review for conciseness - remove explanations Claude already knows
4. Test with Claude B on similar tasks, observe behavior
5. Return to Claude A with specific observations for improvements
6. Repeat the observe-refine-test cycle

**Observe how Claude navigates skills:**

- Unexpected exploration paths may indicate non-intuitive structure
- Missed references suggest links need to be more explicit
- Overreliance on certain files suggests content should move to SKILL.md
- Ignored files may be unnecessary or poorly signaled

**Checklist before sharing**: See the "Checklist for Effective Skills" in
[references/best-practices.md](references/best-practices.md).
