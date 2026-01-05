import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PHOTO_DIR = os.path.join(BASE_DIR, "uploads", "attendance_photos")

def should_delete(filename):
    try:
        # filename format: empid_start_YYYYMMDDHHMMSS.jpg
        date_part = filename.split("_")[-1].split(".")[0][:8]
        photo_date = datetime.strptime(date_part, "%Y%m%d")

        # Month end
        next_month = photo_date.replace(day=28) + timedelta(days=4)
        month_end = next_month - timedelta(days=next_month.day)

        delete_after = month_end + timedelta(days=15)

        return datetime.now() > delete_after
    except:
        return False

def cleanup():
    deleted = 0
    for f in os.listdir(PHOTO_DIR):
        path = os.path.join(PHOTO_DIR, f)
        if os.path.isfile(path) and should_delete(f):
            os.remove(path)
            deleted += 1

    print(f"Deleted {deleted} old photos")

if __name__ == "__main__":
    cleanup()
