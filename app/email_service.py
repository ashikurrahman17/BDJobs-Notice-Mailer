from email.message import EmailMessage
import aiosmtplib
from app.config import settings
from typing import List, Dict


# ═══════════════════════════════════════════════════════════════
# CORE SENDER
# ═══════════════════════════════════════════════════════════════

async def send_email(to_email: str, subject: str, html_content: str):
    msg = EmailMessage()
    msg["From"] = f"BDJobs Mailer <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(html_content, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        start_tls=True,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    )


# ═══════════════════════════════════════════════════════════════
# SHARED DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "bg":            "#f1f5f9",
    "card":          "#ffffff",
    "border":        "#e2e8f0",
    "border_soft":   "#f1f5f9",
    "text_dark":     "#0f172a",
    "text_body":     "#334155",
    "text_muted":    "#64748b",
    "text_faint":    "#94a3b8",
    "brand":         "#0891b2",
    "brand_light":   "#22d3ee",
    "brand_bg":      "#ecfeff",
    "brand_border":  "#cffafe",
    "danger":        "#dc2626",
    "danger_bg":     "#fef2f2",
    "danger_border": "#fecaca",
    "warning_bg":    "#fef3c7",
    "warning_text":  "#b45309",
    "warning_border":"#fde68a",
    "slate_bg":      "#f1f5f9",
    "slate_border":  "#e2e8f0",
    "header_from":   "#0f172a",
    "header_to":     "#1e293b",
}


# ═══════════════════════════════════════════════════════════════
# SHARED RESPONSIVE STYLES
# ═══════════════════════════════════════════════════════════════

RESPONSIVE_STYLES = """
    /* ── Base resets ── */
    body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
    table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
    img { -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }

    /* ── Dark mode ── */
    @media (prefers-color-scheme: dark) {
        .dm-bg           { background-color: #0b1324 !important; }
        .dm-card         { background-color: #0f172a !important; border-color: #1e293b !important; }
        .dm-text         { color: #e2e8f0 !important; }
        .dm-body         { color: #cbd5e1 !important; }
        .dm-muted        { color: #94a3b8 !important; }
        .dm-faint        { color: #64748b !important; }
        .dm-footer       { background-color: #0b1324 !important; border-color: #1e293b !important; }
        .dm-title a      { color: #e2e8f0 !important; }
        .dm-divider      { border-color: #1e293b !important; }
        .dm-badge-slate  { background-color: #1e293b !important; color: #cbd5e1 !important; border-color: #334155 !important; }
        .dm-code         { background-color: #0f172a !important; border-color: #1e293b !important; color: #22d3ee !important; }
        .dm-expiry       { background-color: rgba(6,182,212,0.1) !important; border-color: rgba(6,182,212,0.25) !important; }
    }

    /* ── Mobile (≤ 600px) ── */
    @media only screen and (max-width: 600px) {
        .container       { width: 100% !important; max-width: 100% !important; }
        .wrapper         { padding: 16px 10px !important; }

        .header-pad      { padding: 24px 18px !important; }
        .header-title    { font-size: 20px !important; line-height: 1.25 !important; }
        .header-sub      { font-size: 12px !important; }

        .content-pad     { padding: 20px 16px !important; }
        .card-pad        { padding: 16px 16px 14px 16px !important; }

        .stack-mobile    { display: block !important; width: 100% !important; text-align: left !important; padding: 0 0 10px 0 !important; }
        .stack-mobile-r  { display: block !important; width: 100% !important; text-align: left !important; padding: 0 !important; }

        .cta-btn         { display: block !important; width: 100% !important; text-align: center !important; padding: 13px 16px !important; font-size: 13px !important; box-sizing: border-box !important; }

        .badge           { font-size: 10px !important; padding: 4px 9px !important; letter-spacing: 0.4px !important; }
        .job-title       { font-size: 15.5px !important; line-height: 1.4 !important; }

        .otp-cell        { padding: 0 3px !important; }
        .otp-digit       { width: 34px !important; height: 44px !important; line-height: 44px !important; font-size: 20px !important; border-radius: 8px !important; }

        .footer-link     { display: block !important; padding: 6px 0 !important; }
        .footer-sep      { display: none !important; }
    }

    /* ── Very small phones (≤ 360px) ── */
    @media only screen and (max-width: 360px) {
        .otp-digit       { width: 30px !important; height: 40px !important; line-height: 40px !important; font-size: 18px !important; }
        .otp-cell        { padding: 0 2px !important; }
        .badge           { font-size: 9.5px !important; padding: 3px 7px !important; }
        .content-pad     { padding: 16px 12px !important; }
        .card-pad        { padding: 14px 13px 12px 13px !important; }
    }

    /* ── Reduce motion ── */
    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }
"""


# ═══════════════════════════════════════════════════════════════
# OTP EMAIL
# ═══════════════════════════════════════════════════════════════

async def send_otp_email(to_email: str, otp: str, purpose: str = "Account Verification"):
    # Individual digit boxes
    digits_html = ""
    for d in otp:
        digits_html += f"""
            <td class="otp-cell" style="padding: 0 4px;">
                <div class="otp-digit dm-code" style="width: 42px; height: 52px; line-height: 52px; background-color: #ffffff; border: 1.5px solid {COLORS['brand_border']}; border-radius: 10px; text-align: center; font-family: 'SF Mono', Monaco, Consolas, monospace; font-size: 24px; font-weight: 700; color: {COLORS['brand']}; box-shadow: 0 1px 2px rgba(8,145,178,0.06);">
                    {d}
                </div>
            </td>
        """

    html = f"""<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>Your verification code</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>{RESPONSIVE_STYLES}</style>
</head>
<body class="dm-bg" style="margin: 0; padding: 0; background-color: {COLORS['bg']}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

    <!-- Preheader -->
    <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; color: transparent;">
        Your verification code is {otp}. Expires in 10 minutes.
    </div>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="dm-bg" style="background-color: {COLORS['bg']};">
        <tr>
            <td align="center" class="wrapper" style="padding: 32px 16px;">

                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="container dm-card" style="max-width: 480px; width: 100%; background-color: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px -6px rgba(15,23,42,0.08);">

                    <!-- Header -->
                    <tr>
                        <td class="header-pad" style="background: linear-gradient(135deg, {COLORS['header_from']} 0%, {COLORS['header_to']} 100%); background-color: {COLORS['header_from']}; padding: 28px 24px; text-align: center;">
                            <div style="display: inline-block; background-color: rgba(6,182,212,0.12); border: 1px solid rgba(6,182,212,0.25); color: {COLORS['brand_light']}; padding: 5px 12px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 14px;">
                                🔐 Security Verification
                            </div>
                            <h1 class="header-title" style="margin: 0; color: #ffffff; font-size: 21px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.2;">
                                BDJobs <span style="color: {COLORS['brand_light']};">Notice Mailer</span>
                            </h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td class="content-pad" style="padding: 32px 28px 12px 28px;">
                            <h2 class="dm-text" style="margin: 0 0 8px 0; color: {COLORS['text_dark']}; font-size: 17px; font-weight: 700; letter-spacing: -0.2px;">
                                {purpose}
                            </h2>
                            <p class="dm-muted" style="margin: 0 0 24px 0; color: {COLORS['text_muted']}; font-size: 13px; line-height: 1.6;">
                                Enter the code below to complete your verification. For your security, this code will expire shortly.
                            </p>
                        </td>
                    </tr>

                    <!-- OTP Digits -->
                    <tr>
                        <td align="center" style="padding: 4px 16px 8px 16px;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                                <tr>
                                    {digits_html}
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Expiry -->
                    <tr>
                        <td align="center" style="padding: 16px 24px 28px 24px;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="dm-expiry" style="background-color: {COLORS['brand_bg']}; border: 1px solid {COLORS['brand_border']}; border-radius: 10px;">
                                <tr>
                                    <td style="padding: 10px 16px; font-size: 12px; color: {COLORS['brand']}; font-weight: 600;">
                                        ⏱️ Expires in 10 minutes
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Security Tip -->
                    <tr>
                        <td class="content-pad" style="padding: 0 28px 28px 28px;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td class="dm-divider" style="border-top: 1px solid {COLORS['border_soft']}; padding-top: 20px;">
                                        <p class="dm-faint" style="margin: 0; color: {COLORS['text_faint']}; font-size: 11px; line-height: 1.6;">
                                            <strong class="dm-muted" style="color: {COLORS['text_muted']};">🛡️ Didn't request this?</strong><br>
                                            You can safely ignore this email. Someone may have entered your address by mistake. Never share this code with anyone.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td class="dm-footer" style="background-color: {COLORS['bg']}; border-top: 1px solid {COLORS['border_soft']}; padding: 18px 24px; text-align: center;">
                            <p class="dm-faint" style="margin: 0; color: {COLORS['text_faint']}; font-size: 11px; line-height: 1.5;">
                                Automated message from <strong class="dm-muted" style="color: {COLORS['text_muted']};">BDJobs Notice Mailer</strong><br>
                                Please do not reply to this email.
                            </p>
                        </td>
                    </tr>

                </table>

                <p class="dm-faint" style="margin: 20px 0 0 0; color: {COLORS['text_faint']}; font-size: 10px; text-align: center; letter-spacing: 0.3px;">
                    © BDJobs Notice Mailer · Automated Real-Time Career Dispatcher
                </p>

            </td>
        </tr>
    </table>

</body>
</html>"""

    await send_email(to_email, f"🔑 {otp} is your verification code", html)


# ═══════════════════════════════════════════════════════════════
# JOB ALERT EMAIL — RESPONSIVE CARD
# ═══════════════════════════════════════════════════════════════

def _render_job_card(j: Dict) -> str:
    """Render a single, fully responsive job card."""
    category    = j.get("category") or "General"
    location    = j.get("location") or "Dhaka"
    experience  = j.get("experience_level") or "Any"
    deadline    = j.get("deadline") or "Check Circular"
    apply_url   = j.get("job_url") or "#"
    details_url = j.get("details_url") or apply_url
    title       = j.get("title", "Untitled Position")
    company     = j.get("company_name", "Unknown Company")

    return f"""
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="dm-card"
        style="background-color: {COLORS['card']}; border: 1px solid {COLORS['border']}; border-radius: 14px; margin-bottom: 14px; border-collapse: separate; overflow: hidden; box-shadow: 0 2px 8px -2px rgba(15,23,42,0.06);">

        <!-- Left accent bar -->
        <tr>
            <td style="height: 4px; background: linear-gradient(90deg, {COLORS['brand']} 0%, {COLORS['brand_light']} 100%); background-color: {COLORS['brand']}; line-height: 4px; font-size: 0;">&nbsp;</td>
        </tr>

        <tr>
            <td class="card-pad" style="padding: 20px 22px 18px 22px;">

                <!-- ═══ BADGES ROW ═══ -->
                <div style="margin-bottom: 14px; line-height: 1.6;">
                    <span class="badge" style="display: inline-block; background-color: {COLORS['brand_bg']}; color: {COLORS['brand']}; padding: 5px 11px; border-radius: 6px; font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; border: 1px solid {COLORS['brand_border']}; margin: 0 6px 6px 0; white-space: nowrap;">
                        {category}
                    </span>
                    <span class="badge dm-badge-slate" style="display: inline-block; background-color: {COLORS['slate_bg']}; color: {COLORS['text_body']}; padding: 5px 11px; border-radius: 6px; font-size: 10.5px; font-weight: 600; border: 1px solid {COLORS['slate_border']}; margin: 0 6px 6px 0; white-space: nowrap;">
                        📍 {location}
                    </span>
                    <span class="badge" style="display: inline-block; background-color: {COLORS['warning_bg']}; color: {COLORS['warning_text']}; padding: 5px 11px; border-radius: 6px; font-size: 10.5px; font-weight: 600; border: 1px solid {COLORS['warning_border']}; margin: 0 6px 6px 0; white-space: nowrap;">
                        💼 {experience}
                    </span>
                </div>

                <!-- ═══ JOB TITLE ═══ -->
                <h3 class="job-title dm-title" style="margin: 0 0 6px 0; font-size: 17px; font-weight: 700; line-height: 1.35; color: {COLORS['text_dark']}; letter-spacing: -0.2px;">
                    <a href="{details_url}" target="_blank" style="text-decoration: none; color: {COLORS['text_dark']};">
                        {title}
                    </a>
                </h3>

                <!-- ═══ COMPANY ═══ -->
                <p style="margin: 0 0 16px 0; font-size: 13px; color: {COLORS['text_muted']}; font-weight: 500;">
                    <span class="dm-body" style="color: {COLORS['text_body']}; font-weight: 700;">{company}</span>
                </p>

                <!-- ═══ DIVIDER ═══ -->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 14px;">
                    <tr>
                        <td class="dm-divider" style="border-top: 1px solid {COLORS['border_soft']}; font-size: 0; line-height: 0;">&nbsp;</td>
                    </tr>
                </table>

                <!-- ═══ DEADLINE + CTA — stacks on mobile ═══ -->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                    <tr>
                        <td align="left" valign="middle" class="stack-mobile" style="font-size: 11.5px; color: {COLORS['text_muted']}; font-weight: 600; padding-right: 10px; width: auto;">
                            <span style="display: inline-block; background-color: {COLORS['danger_bg']}; color: {COLORS['danger']}; padding: 5px 10px; border-radius: 6px; font-size: 10.5px; font-weight: 700; border: 1px solid {COLORS['danger_border']}; white-space: nowrap;">
                                ⏳ {deadline}
                            </span>
                        </td>
                        <td align="right" valign="middle" class="stack-mobile-r" style="width: auto;">
                            <!--[if mso]>
                            <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="{apply_url}" style="height:38px;v-text-anchor:middle;width:130px;" arcsize="22%" stroke="f" fillcolor="{COLORS['brand']}">
                                <w:anchorlock/>
                                <center style="color:#ffffff;font-family:sans-serif;font-size:12px;font-weight:700;">Apply Now →</center>
                            </v:roundrect>
                            <![endif]-->
                            <!--[if !mso]><!-- -->
                            <a href="{apply_url}" target="_blank" class="cta-btn" style="display: inline-block; background: linear-gradient(135deg, {COLORS['brand']} 0%, #06b6d4 100%); background-color: {COLORS['brand']}; color: #ffffff; padding: 9px 18px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: 700; letter-spacing: 0.2px; box-shadow: 0 2px 6px rgba(8,145,178,0.25); white-space: nowrap;">
                                Apply Now →
                            </a>
                            <!--<![endif]-->
                        </td>
                    </tr>
                </table>

            </td>
        </tr>
    </table>
    """


async def send_job_alert(to_email: str, jobs: List[Dict]):
    cards = "".join(_render_job_card(j) for j in jobs)
    job_count = len(jobs)
    job_word = "circular" if job_count == 1 else "circulars"

    preview_titles = ", ".join([j.get("title", "")[:40] for j in jobs[:2]])
    if job_count > 2:
        preview_titles += f" +{job_count - 2} more"
    preheader = f"{job_count} new {job_word} matched your preferences: {preview_titles}"

    html = f"""<!DOCTYPE html>
<html lang="en" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <meta name="format-detection" content="telephone=no,address=no,email=no,date=no,url=no">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>{job_count} New Job {job_word.title()}</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>{RESPONSIVE_STYLES}</style>
</head>
<body class="dm-bg" style="margin: 0; padding: 0; background-color: {COLORS['bg']}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">

    <!-- Preheader -->
    <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0; max-width: 0; opacity: 0; overflow: hidden; mso-hide: all; color: transparent;">
        {preheader}
    </div>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="dm-bg" style="background-color: {COLORS['bg']};">
        <tr>
            <td align="center" class="wrapper" style="padding: 28px 12px;">

                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="container" style="max-width: 600px; width: 100%;">

                    <!-- ═══ HEADER ═══ -->
                    <tr>
                        <td class="header-pad" style="background: linear-gradient(135deg, {COLORS['header_from']} 0%, {COLORS['header_to']} 100%); background-color: {COLORS['header_from']}; padding: 32px 24px 30px 24px; border-radius: 16px 16px 0 0; text-align: center;">

                            <div style="display: inline-block; background-color: rgba(6,182,212,0.15); border: 1px solid rgba(6,182,212,0.3); color: {COLORS['brand_light']}; padding: 5px 13px; border-radius: 20px; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 16px;">
                                ⚡ Real-Time Job Dispatcher
                            </div>

                            <h1 class="header-title" style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 800; letter-spacing: -0.6px; line-height: 1.2;">
                                BDJobs <span style="color: {COLORS['brand_light']};">Notice Mailer</span>
                            </h1>

                            <p class="header-sub" style="margin: 12px 0 0 0; color: #cbd5e1; font-size: 13.5px; line-height: 1.5;">
                                We matched
                                <strong style="color: {COLORS['brand_light']}; font-weight: 700;">{job_count} new {job_word}</strong>
                                based on your preferences
                            </p>

                        </td>
                    </tr>

                    <!-- ═══ ACCENT BAR ═══ -->
                    <tr>
                        <td style="height: 4px; background: linear-gradient(90deg, {COLORS['brand']} 0%, {COLORS['brand_light']} 50%, {COLORS['brand']} 100%); background-color: {COLORS['brand']}; line-height: 4px; font-size: 0;">&nbsp;</td>
                    </tr>

                    <!-- ═══ INTRO ═══ -->
                    <tr>
                        <td class="dm-card content-pad" style="background-color: {COLORS['card']}; padding: 22px 24px 6px 24px;">
                            <p class="dm-muted" style="margin: 0; color: {COLORS['text_muted']}; font-size: 12.5px; line-height: 1.6;">
                                Hi there! Here are the latest job circulars that match your subscribed categories and keywords. Apply early — deadlines are approaching.
                            </p>
                        </td>
                    </tr>

                    <!-- ═══ JOB CARDS ═══ -->
                    <tr>
                        <td class="dm-card content-pad" style="background-color: {COLORS['card']}; padding: 18px 24px 24px 24px;">
                            {cards}
                        </td>
                    </tr>

                    <!-- ═══ FOOTER CTA ═══ -->
                    <tr>
                        <td class="dm-card content-pad" style="background-color: {COLORS['card']}; padding: 0 24px 28px 24px;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td class="dm-divider" style="border-top: 1px solid {COLORS['border_soft']}; padding-top: 22px;" align="center">
                                        <a href="http://localhost:8000" target="_blank" class="cta-btn" style="display: inline-block; background: linear-gradient(135deg, {COLORS['header_from']} 0%, {COLORS['header_to']} 100%); background-color: {COLORS['header_from']}; color: #ffffff; padding: 11px 24px; border-radius: 9px; text-decoration: none; font-size: 12.5px; font-weight: 700; letter-spacing: 0.2px; box-shadow: 0 3px 8px rgba(15,23,42,0.15);">
                                            View All Circulars →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- ═══ FOOTER ═══ -->
                    <tr>
                        <td class="dm-footer" style="background-color: {COLORS['bg']}; border-top: 1px solid {COLORS['border']}; border-radius: 0 0 16px 16px; padding: 22px 24px; text-align: center;">
                            <p class="dm-muted" style="margin: 0 0 14px 0; color: {COLORS['text_muted']}; font-size: 11.5px; line-height: 1.6;">
                                You're receiving this because you're subscribed to <strong class="dm-body" style="color: {COLORS['text_body']};">BDJobs Notice Mailer</strong> alerts.
                            </p>

                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
                                <tr>
                                    <td class="footer-link" style="padding: 0 8px;">
                                        <a href="http://localhost:8000" target="_blank" style="color: {COLORS['brand']}; text-decoration: none; font-size: 11.5px; font-weight: 700;">
                                            Manage Preferences
                                        </a>
                                    </td>
                                    <td class="footer-sep" style="color: {COLORS['text_faint']}; font-size: 11.5px;">·</td>
                                    <td class="footer-link" style="padding: 0 8px;">
                                        <a href="http://localhost:8000" target="_blank" style="color: {COLORS['text_muted']}; text-decoration: none; font-size: 11.5px; font-weight: 600;">
                                            Pause Alerts
                                        </a>
                                    </td>
                                    <td class="footer-sep" style="color: {COLORS['text_faint']}; font-size: 11.5px;">·</td>
                                    <td class="footer-link" style="padding: 0 8px;">
                                        <a href="http://localhost:8000" target="_blank" style="color: {COLORS['text_muted']}; text-decoration: none; font-size: 11.5px; font-weight: 600;">
                                            Unsubscribe
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p class="dm-faint" style="margin: 16px 0 0 0; color: {COLORS['text_faint']}; font-size: 10.5px; line-height: 1.5;">
                                © BDJobs Notice Mailer · Automated Real-Time Career Dispatcher
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>"""

    await send_email(to_email, f"🔔 {job_count} New Job {job_word.title()} Alert", html)