from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Show which database Django is using and test the connection, with plain-English hints."

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        engine = db["ENGINE"].rsplit(".", 1)[-1]
        out = self.stdout.write

        out(f"Engine   : {engine}")
        if engine == "sqlite3":
            out(self.style.WARNING(
                "\nDjango is using a LOCAL sqlite file — NOT Supabase.\n"
                "That means DATABASE_URL isn't being read. Check that:\n"
                "  1. a file named exactly .env sits next to manage.py\n"
                "  2. it contains a line starting DATABASE_URL=postgres...\n"
                "  3. you saved the file, and ran this from the same folder."))
            return

        host, port, user, name = db.get("HOST"), db.get("PORT"), db.get("USER"), db.get("NAME")
        out(f"Host     : {host}")
        out(f"Port     : {port}")
        out(f"User     : {user}")
        out(f"Database : {name}")
        out(f"Password : {'*' * 8} ({len(db.get('PASSWORD') or '')} characters)")

        if host and host.startswith("db.") and host.endswith(".supabase.co"):
            out(self.style.WARNING(
                "\nThis is the DIRECT connection (IPv6 only). It fails on Render and on many\n"
                "home networks. Use the SESSION POOLER string instead: Connect button ->\n"
                "Session pooler (host contains 'pooler.supabase.com')."))
        if host and "pooler.supabase.com" in host and user and "." not in user:
            out(self.style.WARNING(
                "\nPooler usernames look like postgres.<project-ref>, but yours is just "
                f"'{user}'. Copy the whole string from the Connect panel again."))

        out("\nTrying to connect...")
        try:
            with connection.cursor() as cursor:
                cursor.execute("select version()")
                version = cursor.fetchone()[0]
        except Exception as exc:  # noqa: BLE001 - we want to show any failure
            message = str(exc)
            out(self.style.ERROR(f"\nFAILED:\n{message}\n"))
            low = message.lower()
            if any(k in low for k in ("could not translate host", "name or service not known",
                                      "network is unreachable", "timeout", "nodename nor servname")):
                hint = ("Django can't reach that address. Most likely you pasted the DIRECT connection.\n"
                        "Use Connect -> Session pooler instead (IPv4-friendly). Also check for typos in the host.")
            elif "password authentication failed" in low:
                hint = ("The password is wrong. Check: the [YOUR-PASSWORD] brackets are removed; the password is\n"
                        "the one you set for the DATABASE (reset it in Supabase if unsure); and any special\n"
                        "characters are URL-encoded (@ -> %40, : -> %3A, / -> %2F, # -> %23, ? -> %3F).\n"
                        "Easiest fix: reset the database password to letters and numbers only.")
            elif "tenant or user not found" in low:
                hint = ("The username is wrong for the pooler. It must look like postgres.<project-ref>.\n"
                        "Copy the whole Session pooler string from the Connect panel again.")
            elif "ssl" in low:
                hint = "An SSL problem. Make sure you copied the Supabase string unchanged."
            elif "does not exist" in low:
                hint = "The database name is wrong. For Supabase it should be 'postgres'."
            else:
                hint = "Copy the whole FAILED message above and send it for help."
            out(self.style.WARNING(f"Hint: {hint}"))
            return

        out(self.style.SUCCESS(f"\nConnected!\n{version}"))
        out("Next: python manage.py migrate   (then look for the tables in Supabase's Table Editor)")
