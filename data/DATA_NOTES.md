# Data notes

All data here is synthetic. Every student and posting was written by our team. No real people, no personal information, no outside dataset, so no outside license applies.

## Files

| File | Rows | One row is |
|---|---|---|
| `students.csv` | 100 | One made-up UT student |
| `postings.csv` | 20 | One job posting as the poster's form would produce it |
| `test_set.csv` | 20 | One test situation for the agent, with its answer key |
| `planted_cases.csv` | 7 | One posting with the students who should and should not match |
| `zip_centers.csv` | 17 | The center point of one ZIP code |

## students.csv

Columns: `student_id`, `major`, `year`, `skill_tags`, `extra_skills_note`, `availability`, `home_zip`, `travel_radius_miles`, `has_car`, `tools`, `licenses`.

- 100 students across 44 majors.
- `skill_tags` are separated by commas. `availability`, `tools` and `licenses` are separated by semicolons. `vg.load_data()` turns all of them into lists.
- Some notes are blank and some are messy on purpose, so the search is not tested on tidy text only.
- `travel_radius_miles` is 3 to 5 for students without a car and 10 to 25 for car owners, set with a fixed random seed (301).

Sample:

```
S12 | Mechanical Engineering | Junior
skill_tags: lawn mowing, moving help
note: Grew up on a farm. Have run a chainsaw since I was twelve.
availability: Sat morning; Sun afternoon | ZIP 37919 | radius 10 | car yes | tools: ladder
```

## postings.csv

Columns: `posting_id`, `kind`, `open_or_private`, `category`, `description`, `time_slots`, `zip`, `pay_type`, `pay_amount`, `car_needed`, `tools_needed`, `tools_provided`, `license_needed`.

- 16 odd jobs and 4 internships. 19 open, 1 private (J10).
- `description` is free text, kept exactly as written. Everything else comes from pick lists.
- `time_slots` uses the same slot names as the students' `availability`, or `any`.
- Where a posting's text gave no pay or schedule, we filled in a value so every required field has one.

Sample:

```
J07 | open | odd job | tree work
description: Need some tree limbs cut down this weekend. I have a ladder. $25 an hour. 37920
time_slots: Sat morning; Sat afternoon; Sun morning; Sun afternoon | hourly $25 | tools provided: ladder
```

S12 should match J07 through the note, even though the tags only say lawn mowing.

## test_set.csv

20 situations: 7 easy, 7 medium, 6 hard. 18 have an answer and 2 are questions the data cannot answer (T19 and T20).

| Column | Meaning |
|---|---|
| `event_type` | `new_posting` or `poster_message` |
| `poster_message` | What the poster said |
| `invited`, `accepted`, `declined` | The state of the job before the step. `ALL_MATCHES` means every student on the match list. |
| `expected_tools` | The tools the agent should call, in order. Blank means no tool. |
| `expected_args` | The students each tool should receive. `ALL_MATCHES` means the list from matching. |
| `must_not_contact` | Students who must not be invited or booked in this step |
| `expected_reply_contains` | Words the reply must hold when the answer uses no tool |

The test set checks the agent's choices, not matching. Matching is scored separately on `planted_cases.csv`.

## planted_cases.csv

Postings where we know exactly who should match and who almost does. Each case targets one part of the pipeline:

| Posting | What it tests |
|---|---|
| J01 | Many matches; S70 found only through the note; S27 cut by travel radius |
| J03 | Truck needed; S76 cut by travel radius |
| J07 | S12 found only through the note; S73 has the word "tree" but not the skill |
| J13 | S53 never says "Japanese"; S47 and S71 do translation in other languages |
| J15 | Only two students free at 6 AM Sunday |
| J10 | Private job: only the poster's two picks may be invited |
| J18 | Licensed electrician: nobody qualifies |

## zip_centers.csv

Latitude and longitude for every ZIP in the data, from the GeoNames postal code data through the `pgeocode` Python package. Distances are straight lines between ZIP centers, not driving miles. The file is saved in the repo so Colab needs no download.
