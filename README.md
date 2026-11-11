# AI 301 Team 6: Vol Gig matching agent

Class project for AI 301 (Track 2, Agents). A poster fills out a job form. The system finds every student who qualifies, then an agent picks from four tools to send the match list to the poster, invite the students the poster picks, check who accepted or declined, and book one.

Team: Hayden Hollar and Jefferson Vicente.

Data: 100 synthetic students (`students.csv`) and 20 job postings (`postings.csv`).

All data in this repository is synthetic. No real people.

## How we work

1. **One owner per file.** Only the owner edits and saves a notebook. If you need a change in someone else's file, tell them.
2. **Save to GitHub when something works.** In Colab: File > Save a copy in GitHub, pick this repo and the `main` branch, write a short note about what changed.
3. **Run all before saving.** Runtime > Restart and run all. The version in the repo must run top to bottom.
4. **Notebooks opened from GitHub do not autosave.** Use Save a copy in GitHub every time.
5. **No secrets in notebooks.** Tokens and keys go in Colab's Secrets panel, never in a cell.
6. **Every notebook starts with the setup cell.** It clones this repo and loads the data, so both of us always run on the same files.

## Who owns what

| File | Owner |
|---|---|
| `data/students.csv` | Jefferson |
| `data/postings.csv` | Jefferson |
| `data/test_set.csv` (20 test situations and answer keys) | Hayden |
| `data/planted_cases.csv` | Hayden |
| `notebooks/01_data_checks.ipynb` | Hayden |
| `notebooks/02_matching.ipynb` (hard filters, embeddings, FAISS, similarity floor, BM25 baseline, two-vector test) | Jefferson |
| `notebooks/03_agent.ipynb` (agent loop, guardrails, the four agent tools) | Hayden |
| `notebooks/04_evaluation.ipynb` (score all 20 situations, results table, chart) | Hayden |
| `notebooks/05_demo.ipynb` (Gradio demo) | Jefferson |
| `results/` | Whoever's notebook writes the file |
| `README.md` | Both. Hayden leads. |

Slides (Jefferson leads) and the report (Hayden leads) live in shared Google Drive files, not here.

## Tool contract

Agree on this before writing agent code. The matching step and the agent tools are built by different people, so the names, inputs and outputs must match exactly. Change this table only when both of us agree.

**Matching step (runs as code before the agent starts, not an agent tool)**

| Function | Owner | Input | Output |
|---|---|---|---|
| `find_matches` | Jefferson | `posting_id` | Every student who passes the hard filters and the similarity floor, as a list of `{student_id, similarity}`, closest first |

**Agent tools (four, per instructor recommendation)**

| Tool | Owner | Input | Output |
|---|---|---|---|
| `send_match_list` | Hayden | `posting_id`, list of `student_id` from `find_matches` | Confirmation that the poster received the list |
| `send_invite` | Hayden | `posting_id`, list of `student_id` chosen by the poster | Who was invited |
| `get_status` | Hayden | `posting_id` | Each invited student and their answer: accepted, declined or no answer yet |
| `book_student` | Hayden | `posting_id`, `student_id` | Booking confirmed |

Rules the code checks on every call, not the model:
- A private job only ever reaches students the poster picked.
- `book_student` only works on a student who accepted.
- The agent never writes reasons, rankings or praise about a student.
- Step limit per job. Every tool call and result is logged.

## Folder layout

```
data/        students.csv, postings.csv, test_set.csv, planted_cases.csv
notebooks/   01 to 05, one owner each
results/     score tables, charts, agent logs
```

## Due dates

- Checkpoint 1, Nov 12: repo link, data loads from the repo, 20 test situations with answer keys, baseline scores
- Project review, Nov 24: agent runs all 20 situations
- Slides and recorded demo, Nov 29
- Presentation, Dec 1
- Report, notebooks, repo link, data, README and peer evaluations, Dec 7
