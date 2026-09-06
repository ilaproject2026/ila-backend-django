from django.core.mail import EmailMultiAlternatives


def send_registration_otp_email(identifier, otp):
    subject = "Your OTP Code - mridhulkrishnatk@gmail.com"
    from_email = "mridhulkrishnatk@gmail.com"
    to = [identifier]

    text_content = f"Your OTP for registration is: {otp}"

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <h2 style="color: #007bff; text-align: center;">Registration OTP</h2>
                <p style="font-size: 16px; color: #333;">
                    Hello,<br><br>
                    Thank you for registering on <b>mridhulkrishna.in</b> 🎉 <br>
                    Please use the OTP below to complete your registration:
                </p>
                <div style="text-align: center; margin: 20px 0;">
                    <span style="font-size: 26px; font-weight: bold; color: #007bff; padding: 12px 24px; border: 2px solid #007bff; display: inline-block; border-radius: 6px; border-style: dashed;">
                        {otp}
                    </span>
                </div>
                <p style="font-size: 14px; color: #555;">
                    This OTP is valid for <b>10 minutes</b>. Do not share it with anyone.
                </p>
                <p style="font-size: 12px; color: #aaa; text-align: center; margin-top: 30px;">
                    &copy; 2025 mridhulkrishna.in
                </p>
            </div>
        </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

