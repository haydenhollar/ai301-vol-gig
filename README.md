# AI 301 Team 6: Vol Gig matching agent

Class project for AI 301 (Track 2, Agents). A poster fills out a job form. The system finds every student who qualifies, then an agent picks tools to send the match list, notify or invite students, book one, and tell the others the job is filled.

Team: Hayden Hollar and Jefferson Vicente.

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
| `notebooks/03_agent.ipynb` (agent loop, guardrails, messaging tools) | Hayden |
| `notebooks/04_evaluation.ipynb` (score all 20 situations, results table, chart) | Hayden |
| `notebooks/05_demo.ipynb` (Gradio demo) | Jefferson |
| `results/` | Whoever's notebook writes the file |
| `README.md` | Both. Hayden leads. |

Slides (Jefferson leads) and the report (Hayden leads) live in shared Google Drive files, not here.

## Tool contract

Agree on this before writing agent code. The matching tool and the messaging tools are built by different people, so the names, inputs and outputs must match exactly. Change this table only when both of us agree.

| Tool | Owner | Input | Output |
|---|---|---|---|
| `find_matches` (name to confirm) | Jefferson | `posting_id` | Every student who passes the hard filters and the similarity floor, as a list of `{student_id, similarity}`, closest first |
| `send_match_list` | Hayden | `posting_id`, list of `student_id` | Confirmation that the poster received the list |
| `notify_students` | Hayden | `posting_id`, list of `student_id` | Who was notified. Open jobs only. |
| `send_invite` | Hayden | `posting_id`, list of `student_id` chosen by the poster | Who was invited. Private jobs only. |
| `book_student` | Hayden | `posting_id`, `student_id` | Booking confirmed. Chat opens between poster and student. |
| `notify_filled` | Hayden | `posting_id`, list of `student_id` | Who was told the job is filled |
| `tell_poster` | Hayden | `posting_id`, message built from logged tool results | Confirmation the poster got the report |

Rules the code checks on every call, not the model:
- A private job only ever reaches students the poster picked.
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
