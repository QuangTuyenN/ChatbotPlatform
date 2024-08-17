# # IMPORT FRAMEWORK / THIRD-PARTY
import uuid
from bot.serializers import EventsCustomSerializer
from bot.models import Events
from rest_framework import permissions, generics, status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from datetime import datetime, timedelta, date
import json
from django.db import connection
import pytz
import uuid
timezone = pytz.timezone('Asia/Bangkok')
# IMPORT CUSTOM MODULE / LOCAL FILES


def json_escape(text):
    return json.dumps(text)[1:-1]


class EventsList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventsCustomSerializer  # Use custom serializer
    queryset = Events.objects.filter(type_name="user")

    @staticmethod
    def is_valid_uuid(input_string):
        try:
            uuid_obj = uuid.UUID(input_string)
            return str(uuid_obj) == input_string
        except ValueError:
            return False

    @extend_schema(parameters=[OpenApiParameter(name="bot", description="Filter by assistant_id", required=True, type=str),
                               OpenApiParameter(
                                   name="text", description="Filter by text", required=False, type=str),
                               OpenApiParameter(
                                   name="dayNumber", description="Filter by dayNumber", required=False, type=str),
                               OpenApiParameter(name="start_date",
                                                description="Start date for filtering (format: DD/MM/YYYY)",
                                                required=False, type=str),
                               OpenApiParameter(name="end_date",
                                                description="End date for filtering (format: DD/MM/YYYY)",
                                                required=False, type=str)
                               ])
    def get(self, request, *args, **kwargs):
        bot = request.query_params.get("bot")
        text = request.query_params.get("text", '')
        day_number = request.query_params.get('dayNumber', '')
        start_date_str = request.query_params.get('start_date', '')
        end_date_str = request.query_params.get('end_date', '')
        if bot is not None and self.is_valid_uuid(str(bot)) is True:
            # Lọc theo assistant_id
            events = self.queryset.filter(
                data__icontains=f'"assistant_id": "{bot}"').order_by('-timestamp')
            if text:
                # Đổi từ định dạng utf8 sang json để search database dạng json
                escaped_text = json_escape(text)
                events = events.filter(
                    data__icontains=f'"text": "{escaped_text}')
            if day_number:
                try:
                    day_number = int(day_number)
                    # if day_number in [1, 7, 14, 30]:
                    duration_time = datetime.now() - timedelta(days=day_number)
                    events = events.filter(
                        timestamp__gte=duration_time.timestamp())
                except ValueError:
                    return Response({"message": "Invalid dayNumber. Must be an integer."},
                                    status=status.HTTP_400_BAD_REQUEST)
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
                    #end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
                    end_date = datetime.strptime(end_date_str, '%d/%m/%Y') + timedelta(days=1) - timedelta(seconds=1)
                    # Ensure the dates are timezone aware
                    start_date = timezone.localize(start_date)
                    end_date = timezone.localize(end_date)
                    events = events.filter(
                        timestamp__gte=start_date.timestamp(), timestamp__lte=end_date.timestamp())
                except ValueError:
                    return Response({"message": "Invalid date format. Use DD/MM/YYYY."},
                                    status=status.HTTP_400_BAD_REQUEST)

            formatted_events = []
            for event in events:
                event_data = event.data
                confidence = event_data['parse_data']['intent']['confidence']
                timestamp = datetime.fromtimestamp(
                    event.timestamp).strftime('%H:%M:%S %d/%m/%Y')
                text = event_data['text']
                intent_name = event.intent_name
                formatted_event = {
                    'id': event.id,
                    'timestamp':  timestamp,
                    'text': text,
                    'intent_name': intent_name,
                    'confidence': int(confidence*100),
                }
                formatted_events.append(formatted_event)
            page = self.paginate_queryset(formatted_events)
            serializer = EventsCustomSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class EventsCustomList(generics.ListAPIView):
    # test cronjob
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EventsCustomSerializer  # Use custom serializer
    queryset = Events.objects.filter(type_name="user")

    def get(self, request, *args, **kwargs):
        today = datetime.now(timezone).date()+timedelta(days=1)
        today = date(2024, 6, 20)+timedelta(days=1)

        # Calculate Monday (start of the current week)
        monday = today - timedelta(days=today.weekday())
        print(monday)

        # Calculate Sunday (end of the current week)
        sunday = monday + timedelta(days=6)
        print(sunday)
        monday_timestamp = datetime.combine(
            monday, datetime.min.time()).timestamp()
        print(monday_timestamp)
        sunday_timestamp = datetime.combine(
            sunday, datetime.min.time()).timestamp() + 24 * 60 * 60
        print(sunday_timestamp)
        print(monday.strftime('%Y_%m_%d') + "_" +
              sunday.strftime('%Y_%m_%d'))
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
