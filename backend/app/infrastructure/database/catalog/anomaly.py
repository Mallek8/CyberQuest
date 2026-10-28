ANOMALY_MISSION = {
    "slug": "anomaly-detection",
    "title": "Anomaly Detection",
    "description": "Compare network indicators with their baselines and mark the rows the change notes do not explain.",
    "category": "anomaly",
    "difficulty": "intermediate",
    "xp_reward": 200,
    "pass_score": 70,
    "order_index": 3,
    "briefing": (
        "These are hourly summaries for one site. Outbound spikes caused by change CHG-104 "
        "are expected around 01:00 UTC from backup host 10.0.4.12. DNS volume rises modestly "
        "when the workday starts. A handful of sign-in retries on single accounts is normal. "
        "Many failures across accounts from one network is not."
    ),
    "challenge": {
        "prompt": "Select every row that is anomalous for this site.",
        "challenge_type": "select_signals",
        "max_score": 100,
        "payload": {
            "events": [
                {
                    "id": "planned-backup",
                    "time": "01:00",
                    "metric": "outbound_mbps",
                    "value": 90,
                    "baseline": 15,
                    "unit": "Mbps",
                    "context": "CHG-104 nightly backup from 10.0.4.12.",
                },
                {
                    "id": "morning-dns",
                    "time": "09:00",
                    "metric": "dns_queries",
                    "value": 120,
                    "baseline": 45,
                    "unit": "queries",
                    "context": "First hour of the business day.",
                },
                {
                    "id": "night-outbound",
                    "time": "03:10",
                    "metric": "outbound_mbps",
                    "value": 470,
                    "baseline": 12,
                    "unit": "Mbps",
                    "context": "No change ticket. Destination 203.0.113.200.",
                },
                {
                    "id": "random-dns",
                    "time": "03:10",
                    "metric": "dns_queries",
                    "value": 8600,
                    "baseline": 40,
                    "unit": "queries",
                    "context": "Many random-looking names under lookup-cdn.example.",
                },
                {
                    "id": "concentrated-dest",
                    "time": "03:12",
                    "metric": "unique_dest_ips",
                    "value": 3,
                    "baseline": 30,
                    "unit": "hosts",
                    "context": "Almost all bytes go to 203.0.113.200.",
                },
                {
                    "id": "normal-retries",
                    "time": "11:00",
                    "metric": "failed_auth",
                    "value": 5,
                    "baseline": 4,
                    "unit": "failures",
                    "context": "A few retries on single accounts.",
                },
                {
                    "id": "account-spray",
                    "time": "14:40",
                    "metric": "failed_auth",
                    "value": 110,
                    "baseline": 4,
                    "unit": "failures",
                    "context": "Failures across 70 accounts from 198.51.100.0/24.",
                },
                {
                    "id": "afternoon-traffic",
                    "time": "15:00",
                    "metric": "outbound_mbps",
                    "value": 22,
                    "baseline": 18,
                    "unit": "Mbps",
                    "context": "Ordinary afternoon volume.",
                },
                {
                    "id": "web-destinations",
                    "time": "16:00",
                    "metric": "unique_dest_ips",
                    "value": 34,
                    "baseline": 28,
                    "unit": "hosts",
                    "context": "Destination count sits close to the usual range.",
                },
            ]
        },
        "answer_key": {
            "suspicious_ids": [
                "night-outbound",
                "random-dns",
                "concentrated-dest",
                "account-spray",
            ],
            "explanations": {
                "planned-backup": "CHG-104 names this 01:00 outbound rise and the backup host. It is planned work.",
                "morning-dns": "120 queries against a baseline of 45 fits the modest workday increase in the brief.",
                "afternoon-traffic": "22 against 18 is ordinary variation.",
                "normal-retries": "Five failures against a baseline of four, on single accounts, matches normal retries.",
                "web-destinations": "The destination count stays close to the baseline and does not show a focused transfer.",
                "night-outbound": "470 Mbps against a baseline of 12 at 03:10 has no change ticket. CHG-104 does not cover this window.",
                "random-dns": "8600 queries at 03:10, aimed at random-looking names, is far from the baseline and lines up with the volume spike.",
                "concentrated-dest": "Unique destinations drop to 3 while bytes concentrate on one host. That is a focused transfer, not browsing.",
                "account-spray": "110 failures across 70 accounts from one network is the spray pattern the brief separates from a few retries.",
            },
        },
        "hints": [
            {
                "level": 1,
                "text": "Compare each value with its baseline, then read the note beside it. A value above the baseline can still be planned work.",
            },
            {
                "level": 2,
                "text": "Check which rows share the 03:10 window. Outbound volume, DNS query count, and how concentrated the destinations are can describe one transfer.",
            },
            {
                "level": 3,
                "text": "The change ticket in the brief covers the outbound rise around 01:00. It does not cover a later outbound spike. A wave of failures across many accounts is also outside the normal retry pattern.",
            },
        ],
    },
}
