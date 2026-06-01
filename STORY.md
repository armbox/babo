# The 29-Year Promise

**1997, Fall Semester. Formal Language Theory, Room 401.**

Final project. The assignment: *design and implement a new programming language.*

Four students huddled around a table in the library, throwing ideas at the whiteboard. Someone suggested a LISP dialect. Too safe. A stack-based concatenative language? Too obscure. Then Quho, the youngest of the group, slammed his notebook on the table.

*"I don't want to make a language for programmers. I want to make a language for my grandmother. A language so simple even a 바보 — a fool — could use it. You just... describe what you want, and the computer figures it out."*

Silence. Then laughter. Then — *wait, could that actually work?*

They called it the **Babo Language**. The pitch was audacious: no syntax, no grammar, no types. Just intent. Write what you want in plain language. The computer does the rest.

The midterm presentation was legendary. The team stood before the class and declared:

> **BABO = { w | w describes a program, and a sufficiently intelligent system can produce ⟦w⟧ }**

*"We don't need to invent syntax,"* they proclaimed. *"We need to invent understanding."*

Professor Lim raised an eyebrow. *"And how do you propose to implement that?"*

The team smiled confidently.

They had no idea.

---

### The Spiral

The following weeks were brutal. They tried everything:

- **Pattern matching?** Worked for "add two numbers." Failed on "make me a game about a dancing dinosaur."
- **Template filling?** They wrote 200 templates. Real language had infinite variety. 200 wasn't even close.
- **A rule-based expert system?** 3,000 lines of Prolog later, it could... sort of greet someone. Sometimes.
- **Statistical NLP?** They read three papers, understood none of them, and went back to templates.

The dorm room became a graveyard of failed approaches. Coffee cups stacked like monuments to hubris. Quho stopped attending other classes. Gichang, the team's best coder, rewrote the parser from scratch four times — each time convinced *this* architecture would work. Each time wrong.

The problem wasn't parsing. The problem wasn't code generation. The problem was **semantic understanding** — turning a vague human desire into a precise, runnable specification. That required something none of them knew how to build: a system that actually understood what words meant.

One night, at 3 AM, Quho stared at the whiteboard covered in crossed-out diagrams. The formal definition they'd been so proud of stared back at him:

> **BABO = { w | ... a sufficiently intelligent system ... }**

He circled the word *"sufficiently intelligent."* That was the whole problem. That one phrase contained a mountain they couldn't climb with 1997 technology.

*"We're not building a compiler,"* he whispered. *"We'd need to build a brain."*

---

### The Deadline

The submission deadline came and went. The team had nothing runnable — just a binder full of theory, a broken prototype that could parse exactly five sentence patterns, and a white paper titled *"BABO: A Vision for Intent-Based Programming"* that read more like science fiction than computer science.

They took the F.

Professor Lim left a single comment on their proposal: *"Beautiful idea. Wrong century. Come back when the machines can think."*

The team disbanded after the semester. Quho kept the white paper in a drawer. Every few years he'd pull it out, read it, and wonder. Gichang went into industry and spent 20 years watching AI grow from pattern matching to deep learning to large language models. He never stopped thinking about Babo.

---

## 2026: One Click

Twenty-nine years later, the missing piece arrived.

Not through a PhD dissertation or a research grant. Through a command-line tool called Claude Code — a "sufficiently intelligent system" that could read a natural language description and produce a complete, runnable program.

The team — now middle-aged, scattered across three countries — reunited on a video call. Quho opened a terminal. He typed:

```bash
$ babo hello.babo
```

One command. One click.

The machine thought for a moment. Then it wrote code. Real, runnable, *correct* code. Generated from nothing but a plain-language description.

Gichang cried. Quho laughed. The fourth team member simply said: *"Finally."*

The 1997 vision — a language so simple even a fool could use — was no longer science fiction. It was a shell command. It was `git clone && pip install -e .`. It was real.

**It really is a universal language that even a fool can use.**

The F has been revised. The assignment is finally submitted.
