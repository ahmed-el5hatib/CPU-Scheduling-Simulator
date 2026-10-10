"""Educational Guide View providing theoretical context, formulas, and OS glossary.

Author signature: Eng Ahmed El-khatib
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

GUIDE_HTML = r"""
<!DOCTYPE html>
<html>
<head>
<style>
    body { font-family: 'Segoe UI', sans-serif; color: #1E293B; line-height: 1.6; }
    h1 { color: #0B1F3A; font-size: 20pt; border-bottom: 2px solid #1E6FBA; padding-bottom: 6px; }
    h2 { color: #0B1F3A; font-size: 15pt; margin-top: 24px; border-left: 4px solid #17A2A2; padding-left: 8px; }
    h3 { color: #1E6FBA; font-size: 12pt; margin-top: 16px; }
    p, li { font-size: 10.5pt; color: #334155; }
    code { background-color: #F1F5F9; color: #0F172A; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    .box { background-color: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 6px; padding: 12px; margin: 12px 0; }
    .formula { font-family: monospace; font-size: 11pt; color: #0B1F3A; background: #EEF2F6; padding: 8px; border-radius: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 10pt; }
    th { background-color: #0B1F3A; color: #FFFFFF; padding: 8px 10px; text-align: left; }
    td { padding: 8px 10px; border-bottom: 1px solid #E2E8F0; }
    tr:nth-child(even) { background-color: #F8FAFC; }
    .badge-yes { color: #D97706; font-weight: bold; }
    .badge-no { color: #2563EB; font-weight: bold; }
    .invariant { background-color: #F0FDF4; border-left: 4px solid #059669; padding: 8px 12px; margin: 8px 0; border-radius: 4px; font-size: 10pt; }
    .invariant b { color: #065F46; }
</style>
</head>
<body>

<h1>Operating Systems — CPU Scheduling Educational Guide</h1>
<p><i>Curated by Eng Ahmed El-khatib</i></p>

<h2>1. Introduction to CPU Scheduling</h2>
<p>
CPU scheduling is the basis of multi-programmed operating systems. By switching the CPU among processes, the operating system can make the computer more productive and maximize processor utilization.
When the CPU becomes idle, the OS must select one of the processes in the ready queue to be executed.
</p>

<h2>2. Key Performance Metrics & Mathematical Definitions</h2>
<div class="box">
    <div class="formula"><b>Schedule Span:</b> span = max(CT) - min(AT)</div>
    <p>The total duration across which the submitted workload is processed.</p>

    <div class="formula"><b>Busy Time:</b> busy_time = sum of all non-IDLE segment durations</div>
    <p>Total time during which the CPU was actively executing user processes.</p>

    <div class="formula"><b>Idle Time:</b> idle_time = span - busy_time</div>
    <p>Time during the schedule when no process was ready to execute.</p>

    <div class="formula"><b>CPU Utilization:</b> utilization = busy_time / span</div>
    <p>The fraction (or percentage) of active time the CPU was busy running processes.</p>

    <div class="formula"><b>Throughput:</b> throughput = n_completed / span</div>
    <p>Number of completed processes per unit time (proc/time-unit).</p>

    <div class="formula"><b>Turnaround Time (TAT):</b> TAT = Completion Time (CT) - Arrival Time (AT)</div>
    <p>The total elapsed time from when a process is submitted until it finishes.</p>

    <div class="formula"><b>Waiting Time (WT):</b> WT = Turnaround Time (TAT) - Burst Time (BT)</div>
    <p>Total amount of time spent waiting in the ready queue.</p>

    <div class="formula"><b>Response Time (RT):</b> RT = First Start Time (ST) - Arrival Time (AT)</div>
    <p>Time from submission until the process first gains access to the CPU.</p>
</div>

<h2>3. Scheduling Algorithms & Tie-Breaking Rules</h2>

<h3>A. First-Come, First-Served (FCFS)</h3>
<p>Processes are dispatched strictly according to arrival time. Non-preemptive.</p>
<div class="rule">
<b>Tie-Breaking:</b> Tie on arrival &rarr; Lower PID index (insertion order).
</div>
<p><b>Drawback:</b> Susceptible to the <i>Convoy Effect</i>, where short processes linger behind long CPU-bound tasks.</p>

<h3>B. Shortest Job First (SJF Non-preemptive)</h3>
<p>Assigns the CPU to the ready process with the shortest CPU burst. Once started, runs to completion.</p>
<div class="rule">
<b>Tie-Breaking:</b> Tie on burst &rarr; Earlier arrival time, then lower insertion index.
</div>
<p><b>Property:</b> Provably optimal in minimizing average waiting time among non-preemptive algorithms.</p>

<h3>C. Priority Scheduling (Non-preemptive)</h3>
<p>Assigns CPU based on assigned priority numbers.</p>
<div class="rule">
<b>Priority Convention:</b> Smaller integer = Higher priority (e.g. priority 1 is higher than priority 2).<br>
<b>Tie-Breaking:</b> Tie on priority &rarr; Earlier arrival time, then lower insertion index.
</div>

<h3>D. Shortest Remaining Time First (SRTF Preemptive)</h3>
<p>Preemptive variant of SJF. When a new process arrives, its remaining burst is compared against the running process.</p>
<div class="rule">
<b>Preemption Rule:</b> Strict preemption only (<code>new.remaining &lt; running.remaining</code>). If remaining times are equal, do NOT preempt.<br>
<b>Queue Tie-Breaking:</b> Earlier arrival, then insertion order.
</div>

<h3>E. Round Robin (RR)</h3>
<p>Preemptive time-sliced cyclic scheduling designed for time-sharing systems. Each process is allocated a fixed time quantum <code>q</code>.</p>
<div class="rule">
<b>Standard Textbook Rule:</b> On quantum expiry AND new arrival at the exact same instant, the newly arrived process enters the ready queue <b>BEFORE</b> the preempted process.
</div>

<h3>F. Preemptive Priority</h3>
<p>Preempts the running process whenever a new job arrives with strictly higher priority (smaller integer).</p>
<div class="rule">
<b>Preemption Rule:</b> Preempt if <code>new.priority &lt; running.priority</code>. On equal priority, keep running.
</div>

<h2>4. Algorithm Tradeoff & Performance Matrix</h2>
<table>
    <thead>
        <tr>
            <th>Algorithm</th>
            <th>Type</th>
            <th>Starvation Risk</th>
            <th>Overhead</th>
            <th>Convoy Effect</th>
            <th>Typical Domain</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><b>FCFS</b></td>
            <td><span class="badge-no">Non-Preemptive</span></td>
            <td>None</td>
            <td>Minimal</td>
            <td>High</td>
            <td>Batch systems, FIFO spoolers</td>
        </tr>
        <tr>
            <td><b>SJF</b></td>
            <td><span class="badge-no">Non-Preemptive</span></td>
            <td>Yes (for long jobs)</td>
            <td>Low</td>
            <td>Low</td>
            <td>Long-term batch scheduling</td>
        </tr>
        <tr>
            <td><b>Priority (NP)</b></td>
            <td><span class="badge-no">Non-Preemptive</span></td>
            <td>Yes (low priority)</td>
            <td>Low</td>
            <td>Medium</td>
            <td>Priority queues without preemption</td>
        </tr>
        <tr>
            <td><b>SRTF</b></td>
            <td><span class="badge-yes">Preemptive</span></td>
            <td>Yes (for long jobs)</td>
            <td>Medium-High</td>
            <td>Minimal</td>
            <td>Interactive time-shared systems</td>
        </tr>
        <tr>
            <td><b>Round Robin</b></td>
            <td><span class="badge-yes">Preemptive</span></td>
            <td>None (guaranteed turnaround)</td>
            <td>Medium (context switches)</td>
            <td>Minimal</td>
            <td>General-purpose OS time-sharing</td>
        </tr>
        <tr>
            <td><b>Preemptive Priority</b></td>
            <td><span class="badge-yes">Preemptive</span></td>
            <td>Yes (requires aging)</td>
            <td>Medium-High</td>
            <td>Low</td>
            <td>Real-Time Systems (RTOS)</td>
        </tr>
    </tbody>
</table>

<h2>5. Mathematical Invariants Verified (I1 &ndash; I11)</h2>
<p>This simulator's pure discrete execution engine is strictly verified against 11 formal Operating Systems invariants:</p>

<div class="invariant"><b>I1 &mdash; Valid Non-negative Time Domain:</b> All temporal milestones satisfy $0 \le AT_i \le ST_i \le CT_i$.</div>
<div class="invariant"><b>I2 &mdash; Monotonic Non-overlapping Execution:</b> Single CPU core execution is strictly sequential: $\forall k, segment[k].end \le segment[k+1].start$.</div>
<div class="invariant"><b>I3 &mdash; Non-preemptive Atomicity:</b> Non-preemptive algorithms (FCFS, SJF, Priority) execute each process in exactly one contiguous segment of duration $BT_i$.</div>
<div class="invariant"><b>I4 &mdash; Strict Arrival Precedence:</b> A process is never dispatched before its arrival: $ST_i \ge AT_i$.</div>
<div class="invariant"><b>I5 &mdash; Conservation of Work:</b> For every finished job, $TAT_i = CT_i - AT_i = WT_i + BT_i$.</div>
<div class="invariant"><b>I6 &mdash; Conservation of CPU Burst Energy:</b> The sum of all allocated execution slice durations equals the initial burst: $\sum \Delta t_i = BT_i$.</div>
<div class="invariant"><b>I7 &mdash; Schedule Span Balance:</b> Total schedule span is partitioned without loss: $Span = Busy\_Time + Idle\_Time$.</div>
<div class="invariant"><b>I8 &mdash; Bounded CPU Utilization:</b> $0 \le Utilization \le 1.0$, with $Utilization = Busy / Span$.</div>
<div class="invariant"><b>I9 &mdash; Zero Premature Dispatches:</b> The CPU is in <code>IDLE</code> whenever no process has arrived yet; it never executes phantom work.</div>
<div class="invariant"><b>I10 &mdash; Deterministic Tie-Breaking:</b> Identical arrival/burst/priority states resolve deterministically using arrival time and insertion order.</div>
<div class="invariant"><b>I11 &mdash; Ready Queue Consistency:</b> The active process list and ready queue states at clock tick $t$ reflect true discrete event semantics.</div>

<h2>6. Operating Systems Glossary</h2>
<ul>
    <li><b>Preemption:</b> The act of temporarily interrupting a running process without its cooperation to give the CPU to another task.</li>
    <li><b>Convoy Effect:</b> When small processes queue up behind a heavy CPU-intensive process, deteriorating average waiting time.</li>
    <li><b>Starvation (Indefinite Blocking):</b> A situation where a ready process waits indefinitely because higher priority or shorter jobs continuously arrive.</li>
    <li><b>Aging:</b> A technique to prevent starvation by gradually increasing a waiting process's priority over time.</li>
    <li><b>Context Switch:</b> Saving the state of the active process and restoring state for the newly dispatched process.</li>
</ul>

</body>
</html>
"""


class GuideView(QWidget):
    """Educational view displaying operating systems concepts and algorithm guidelines."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        card = QFrame()
        card.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 8px;"
        )
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(12, 12, 12, 12)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(GUIDE_HTML)
        self.browser.setStyleSheet("border: none; background-color: transparent;")

        c_layout.addWidget(self.browser)
        layout.addWidget(card)

