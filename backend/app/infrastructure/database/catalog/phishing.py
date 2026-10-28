PHISHING_MISSION = {
    "slug": "phishing-investigation",
    "title": "Phishing Investigation",
    "description": "Review a forwarded email and mark the observations that belong in the incident report.",
    "category": "phishing",
    "difficulty": "beginner",
    "xp_reward": 120,
    "pass_score": 70,
    "order_index": 1,
    "briefing": (
        "You are the analyst on duty at Northwind Analytics. The company domain is "
        "northwind.example. Internal notices come from it-helpdesk@northwind.example. "
        "An employee forwarded the message below and did not open the link. Mark the "
        "observations that are actual phishing signals. A tidy layout or a workday "
        "timestamp is not enough to clear a message."
    ),
    "challenge": {
        "prompt": "Select every observation that should be cited as a phishing signal.",
        "challenge_type": "select_signals",
        "max_score": 100,
        "payload": {
            "email": {
                "from_name": "IT Support",
                "from_address": "it-support@microsft-secure-login.example",
                "reply_to": "alerts@mail-security-check.example",
                "subject": "Urgent: your mailbox will be suspended today",
                "date": "Tue, 14 Apr 2026 08:12:03 +0000",
                "body": (
                    "Dear user,\n\n"
                    "We detected unusual sign-in activity. Your mailbox will be suspended "
                    "today unless you verify your password within 30 minutes.\n\n"
                    "Verify now: http://microsft-secure-login.example/verify-mailbox\n\n"
                    "IT Support\n"
                    "Northwind Analytics\n"
                    "+1-202-555-0148\n"
                ),
                "headers": [
                    {
                        "name": "Authentication-Results",
                        "value": "northwind.example; spf=fail smtp.mailfrom=mail-security-check.example; dkim=fail",
                    },
                    {
                        "name": "Return-Path",
                        "value": "bounce@mail-security-check.example",
                    },
                ],
            },
            "indicators": [
                {
                    "id": "sender-domain",
                    "label": "Sender domain",
                    "group": "identity",
                    "detail": "The From address is it-support@microsft-secure-login.example.",
                },
                {
                    "id": "reply-to-mismatch",
                    "label": "Reply-To domain",
                    "group": "identity",
                    "detail": "Reply-To is alerts@mail-security-check.example.",
                },
                {
                    "id": "auth-results",
                    "label": "Authentication results",
                    "group": "delivery",
                    "detail": "The header shows spf=fail and dkim=fail for this message.",
                },
                {
                    "id": "urgency",
                    "label": "Deadline language",
                    "group": "content",
                    "detail": "The body threatens suspension today unless the recipient acts within 30 minutes.",
                },
                {
                    "id": "credential-request",
                    "label": "Password request",
                    "group": "content",
                    "detail": "The body asks the recipient to verify a password.",
                },
                {
                    "id": "link-host",
                    "label": "Link destination",
                    "group": "content",
                    "detail": "The link host is microsft-secure-login.example.",
                },
                {
                    "id": "generic-greeting",
                    "label": "Greeting",
                    "group": "content",
                    "detail": 'The message opens with "Dear user" and never uses the employee name.',
                },
                {
                    "id": "business-hours",
                    "label": "Send time",
                    "group": "context",
                    "detail": "The Date header is Tue, 14 Apr 2026 08:12:03 +0000.",
                },
                {
                    "id": "signature-block",
                    "label": "Signature block",
                    "group": "context",
                    "detail": "The footer shows a team name, the company name, and a phone number.",
                },
                {
                    "id": "readable-prose",
                    "label": "Writing quality",
                    "group": "context",
                    "detail": "The sentences are grammatically clean and the layout is tidy.",
                },
            ],
        },
        "answer_key": {
            "suspicious_ids": [
                "sender-domain",
                "reply-to-mismatch",
                "auth-results",
                "urgency",
                "credential-request",
                "link-host",
                "generic-greeting",
            ],
            "explanations": {
                "sender-domain": "The company domain in this case is northwind.example. The sender domain is a lookalike, so the display name does not establish identity.",
                "reply-to-mismatch": "Reply-To points at a third domain that matches neither the From address nor northwind.example.",
                "auth-results": "SPF and DKIM both failed, so the message is unauthenticated.",
                "urgency": "A 30 minute suspension threat is pressure, not proof of an IT process.",
                "credential-request": "The message asks for a password. Staff should not type one into a page opened from mail.",
                "link-host": "The link host repeats the lookalike domain and is not northwind.example.",
                "generic-greeting": "A generic greeting is a weak signal alone, but it fits a bulk lure and belongs in the report with the identity failures.",
                "business-hours": "08:12 UTC can be a normal work hour. The clock does not clear or condemn the message.",
                "signature-block": "A signature is easy to copy and does not prove control of a Northwind mailbox.",
                "readable-prose": "Clean writing is not an authenticity check. Templates are often tidy.",
            },
        },
        "hints": [
            {
                "level": 1,
                "text": "Start with identity. Put the domain in the From address next to the company domain from the case brief. A friendly display name does not settle that comparison.",
            },
            {
                "level": 2,
                "text": "Read the ask and the link as a pair. Note any deadline, and check whether the link host is the company domain. A request for a password belongs in your notes.",
            },
            {
                "level": 3,
                "text": "Use the headers. Authentication results and Reply-To are both in the brief. A polished signature, a tidy sentence, or a workday timestamp does not confirm the sender.",
            },
        ],
    },
}
