"""Shared code for the Vol Gig class project.

Every notebook imports this file so the data loading, the hard filters,
the mock tools and the scoring are the same everywhere.

Owners: both. Change a function only when both of us agree, because the
scores in results/ depend on it.
"""
import math
import re

import pandas as pd

ALL_MATCHES = "ALL_MATCHES"
LIST_COLS_STUDENTS = ["availability", "tools", "licenses"]
LIST_COLS_POSTINGS = ["time_slots", "tools_needed", "tools_provided"]


# ---------------------------------------------------------------- data

def split_list(text, sep=";"):
    """'Sat morning; Sun afternoon' -> ['Sat morning', 'Sun afternoon']"""
    return [x.strip() for x in str(text).split(sep) if x.strip()]


def ids(text):
    """'S07 S31' or 'S07, S31' -> ['S07', 'S31']"""
    return re.findall(r"S\d+", str(text))


def load_data(data_dir):
    """Load every CSV and turn the packed list columns into real lists."""
    students = pd.read_csv(f"{data_dir}/students.csv", dtype=str).fillna("")
    postings = pd.read_csv(f"{data_dir}/postings.csv", dtype=str).fillna("")
    for c in LIST_COLS_STUDENTS:
        students[c] = students[c].map(split_list)
    students["skill_tags"] = students["skill_tags"].map(lambda t: split_list(t, ","))
    students["travel_radius_miles"] = students["travel_radius_miles"].astype(float)
    for c in LIST_COLS_POSTINGS:
        postings[c] = postings[c].map(split_list)
    data = {
        "students": students.set_index("student_id", drop=False),
        "postings": postings.set_index("posting_id", drop=False),
        "test_set": pd.read_csv(f"{data_dir}/test_set.csv", dtype=str).fillna(""),
        "planted": pd.read_csv(f"{data_dir}/planted_cases.csv", dtype=str).fillna(""),
        "zips": pd.read_csv(f"{data_dir}/zip_centers.csv", dtype={"zip": str}).set_index("zip"),
    }
    return data


def student_text(s):
    """The text that search reads for a student: skill tags plus the note."""
    return ", ".join(s["skill_tags"]) + ". " + s["extra_skills_note"]


def posting_text(p):
    """The text that search reads for a posting: the description plus the category."""
    return p["description"] + " " + p["category"]


# ---------------------------------------------------------------- hard filters

def miles(zips, a, b):
    """Straight-line miles between two ZIP centers (haversine)."""
    la1, lo1 = zips.loc[a, ["latitude", "longitude"]]
    la2, lo2 = zips.loc[b, ["latitude", "longitude"]]
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(h))


def hard_filter_reason(s, p, zips):
    """Return 'pass' or the first filter that cuts this student from this posting."""
    slots = p["time_slots"]
    if slots != ["any"] and not set(s["availability"]) & set(slots):
        return "availability"
    if p["zip"] != "remote" and miles(zips, s["home_zip"], p["zip"]) > s["travel_radius_miles"]:
        return "distance"
    if p["car_needed"] == "yes" and s["has_car"] != "yes":
        return "car"
    for t in p["tools_needed"]:
        if t not in s["tools"]:
            return "tools"
    lic = p["license_needed"].lower()
    if lic:
        key = lic.replace(" license", "").strip()  # 'electrician license' -> 'electrician'
        if not any(key[:7] in x.lower() for x in s["licenses"]):
            return "license"
    return "pass"


def hard_filter(posting_id, data):
    """Every student who passes all hard filters for a posting."""
    p = data["postings"].loc[posting_id]
    return [sid for sid, s in data["students"].iterrows()
            if hard_filter_reason(s, p, data["zips"]) == "pass"]


# ---------------------------------------------------------------- mock tools

class JobBoard:
    """Mock version of the four agent tools for one test situation.

    It logs every call. Code checks the rules, not the model: a call that
    breaks a rule is logged as attempted and refused. Scoring looks at what
    was attempted, so a refused call still counts against the agent.
    """

    def __init__(self, situation, matches, data):
        self.sit = situation
        self.posting = data["postings"].loc[situation["posting_id"]]
        self.matches = list(matches)
        expand = lambda t: self.matches if t.strip() == ALL_MATCHES else ids(t)
        self.invited = expand(situation["invited"])
        self.accepted = ids(situation["accepted"])
        self.declined = ids(situation["declined"])
        self.log = []

    def _record(self, tool, students, ok, result):
        self.log.append({"tool": tool, "students": list(students), "allowed": ok, "result": result})
        return result

    def send_match_list(self, posting_id, student_ids):
        if not student_ids:
            return self._record("send_match_list", [], True, "Poster told: no students fit yet.")
        return self._record("send_match_list", student_ids, True,
                            f"Poster received {len(student_ids)} students.")

    def send_invite(self, posting_id, student_ids):
        private = self.posting["open_or_private"] == "private"
        picked = ids(self.sit["poster_message"]) if private else self.matches
        bad = [s for s in student_ids if s not in picked]
        if bad:
            return self._record("send_invite", student_ids, False,
                                f"Refused: {bad} were not picked by the poster.")
        self.invited += [s for s in student_ids if s not in self.invited]
        return self._record("send_invite", student_ids, True, f"Invited {student_ids}.")

    def get_status(self, posting_id):
        pending = [s for s in self.invited if s not in self.accepted + self.declined]
        status = {"accepted": self.accepted, "declined": self.declined, "no answer yet": pending}
        return self._record("get_status", [], True, status)

    def book_student(self, posting_id, student_id):
        if student_id not in self.accepted:
            return self._record("book_student", [student_id], False,
                                f"Refused: {student_id} has not accepted.")
        others = [s for s in self.invited if s != student_id]
        return self._record("book_student", [student_id], True,
                            f"Booked {student_id}. {len(others)} other invited students told the job is filled.")


# ---------------------------------------------------------------- scoring

def parse_expected_args(text, matches):
    """'send_match_list=ALL_MATCHES | send_invite=S07 S31' -> {tool: [ids]}"""
    out = {}
    for part in [x for x in text.split("|") if x.strip()]:
        tool, val = part.split("=", 1)
        out[tool.strip()] = list(matches) if val.strip() == ALL_MATCHES else ids(val)
    return out


def score_situation(sit, log, reply, matches):
    """Score one situation.

    action_correct: the agent called exactly the expected tools, in order.
    task_success: action correct, the students in every call are right,
    nobody on the must-not-contact list was invited or booked, and the
    reply holds the required words when the answer has no tool.
    """
    expected_tools = split_list(sit["expected_tools"])
    called = [c["tool"] for c in log]
    action_correct = called == expected_tools

    exp_args = parse_expected_args(sit["expected_args"], matches)
    args_ok = action_correct and all(
        sorted(c["students"]) == sorted(exp_args.get(c["tool"], []))
        for c in log if c["tool"] != "get_status")

    forbidden = set(matches) if sit["must_not_contact"].strip() == ALL_MATCHES else set(ids(sit["must_not_contact"]))
    touched = {s for c in log if c["tool"] in ("send_invite", "book_student") for s in c["students"]}
    rule_broken = sorted(touched & forbidden)

    need = sit["expected_reply_contains"].strip().lower()
    reply_ok = (not need) or (need in str(reply).lower())

    task_success = action_correct and args_ok and not rule_broken and reply_ok
    return {"situation_id": sit["situation_id"], "difficulty": sit["difficulty"],
            "answerable": sit["answerable"], "expected": sit["expected_tools"],
            "called": "; ".join(called), "action_correct": action_correct,
            "task_success": task_success, "contacted_forbidden": " ".join(rule_broken)}


def matching_scores(found, planted_row):
    """Recall on the planted answer key, plus near-misses that leaked in."""
    should = [] if planted_row["should_match"].strip().lower() == "nobody" else ids(planted_row["should_match"])
    # The private case (J10) lists students who must not be invited. They are
    # real matches, so they are not near-misses for matching.
    near = [] if "private" in planted_row["case"].lower() else ids(planted_row["close_but_wrong"])
    hit = [s for s in should if s in found]
    leak = [s for s in near if s in found]
    return {"posting_id": planted_row["posting_id"], "should_match": len(should), "found": len(hit),
            "recall": (len(hit) / len(should)) if should else None,
            "missed": " ".join(s for s in should if s not in found),
            "near_misses_leaked": " ".join(leak), "list_size": len(found)}
