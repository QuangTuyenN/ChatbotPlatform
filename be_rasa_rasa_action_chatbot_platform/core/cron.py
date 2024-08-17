from bot.models import Events
from bot.models import Bot
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
# IMPORT CUSTOM MODULE / LOCAL FILES
from bot.models import Events
from django.db import connection
import pytz
timezone = pytz.timezone('Asia/Bangkok')


def auto_delete_data():
    # Lấy tổng số bản ghi hiện tại
    try:
        # Lấy tổng số bản ghi hiện tại
        list_bot = Bot.objects.all()
        list_id = []
        for bot in list_bot:
            list_id.append(bot.id)
        for bot_id in list_id:
            # bot_id = '20231220-104352-bare-oasis'
            # Lấy tổng số bản ghi hiện tại của bot
            search_str = f'"assistant_id": "{bot_id}"'
            total_records = Events.objects.filter(
                data__icontains=search_str).count()
            print(total_records)

            if total_records > 1000:
                # Lấy danh sách các bản ghi cần giữ lại (1000 bản ghi mới nhất)
                records_to_keep = total_records = Events.objects.filter(
                    data__icontains=search_str).order_by('-timestamp')[:1000]
                last_record_to_keep = records_to_keep[999]
                Events.objects.filter(
                    data__icontains=search_str, timestamp__lt=last_record_to_keep.timestamp).delete()
                return Response(status=status.HTTP_200_OK)
            else:
                print("không đủ 1000 records")
        return Response(status=status.HTTP_403_FORBIDDEN)
    except Exception as e:
        print(f"Failed to clean history records: {str(e)}")
        return Response(status=status.HTTP_403_FORBIDDEN)


def auto_create_partition_event():
    today = datetime.now(timezone).date()+timedelta(days=1)

    # Calculate Monday (start of the current week)
    monday = today - timedelta(days=today.weekday())

    # Calculate Sunday (end of the current week)
    sunday = monday + timedelta(days=6)
    monday_timestamp = datetime.combine(
        monday, datetime.min.time()).timestamp()
    sunday_timestamp = datetime.combine(
        sunday, datetime.min.time()).timestamp() + 24 * 60 * 60
    try:
        connection.schema_editor().add_range_partition(
            model=Events,
            name=monday.strftime('%Y_%m_%d') + "_" +
            sunday.strftime('%Y_%m_%d'),
            from_values=monday_timestamp,
            to_values=sunday_timestamp,
        )
        return Response(status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"message": f"partition is already exist: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
